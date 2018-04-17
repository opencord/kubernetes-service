
# Copyright 2017-present Open Networking Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
    sync_service.py

    Synchronize Services. The only type of Service this step knows how to deal with are services that use Kubernetes
    NodePort to expose ports.
"""

from synchronizers.new_base.syncstep import SyncStep
from synchronizers.new_base.modelaccessor import Service

from xosconfig import Config
from multistructlog import create_logger

from kubernetes.client.rest import ApiException
from kubernetes import client as kubernetes_client, config as kubernetes_config

log = create_logger(Config().get('logging'))

class SyncService(SyncStep):

    """
        SyncService

        Implements sync step for syncing Services.
    """

    provides = [Service]
    observes = Service
    requested_interval = 0

    def __init__(self, *args, **kwargs):
        super(SyncService, self).__init__(*args, **kwargs)
        kubernetes_config.load_incluster_config()
        self.v1 = kubernetes_client.CoreV1Api()

    def fetch_pending(self, deletion=False):
        """ Filter the set of pending objects.
            As this syncstep can only create Service that exist within Trust Domains, filter out those services that
            don't have Trust Domains associated with them.
        """
        models = super(SyncService, self).fetch_pending(deletion)

        if (not deletion):
            for model in models[:]:
                if not self.get_trust_domain(model):
                    log.info("Unable to determine Trust Domain for service %s. Ignoring." % model.name)
                    models.remove(model)
                elif not model.serviceports.exists():
                    # If there are not ServicePorts, then there's not much for us to do at this time...
                    log.info("Service %s is not interesting. Ignoring." % model.name)
                    models.remove(model)

        return models

    def get_trust_domain(self, o):
        """ Given a service, determine its Trust Domain.

            The design we've chosen to go with is that a service is pinned to a Trust Domain based on the slices
            that it contains. It's an error for a service to be directly comprised of slices from multiple
            trust domains.

            This allows for "logical services", that contain no slices of their own, but are comprised of multiple
            subservices. For example, EPC.
        """

        trust_domain = None
        for slice in o.slices.all():
            if slice.trust_domain:
                if (trust_domain is None):
                    trust_domain = slice.trust_domain
                elif (trust_domain.id != slice.trust_domain.id):
                    # Bail out of we've encountered a situation where a service spans multiple trust domains.
                    log.warning("Service %s is comprised of slices from multiple trust domains." % o.name)
                    return None

        return trust_domain

    def get_service(self, o, trust_domain):
        """ Given an XOS Service, read the associated Service from Kubernetes.
            If no Kubernetes service exists, return None
        """
        try:
            k8s_service = self.v1.read_namespaced_service(o.name, trust_domain.name)
        except ApiException, e:
            if e.status == 404:
                return None
            raise
        return k8s_service

    def sync_record(self, o):
        trust_domain = self.get_trust_domain(o)
        k8s_service = self.get_service(o,trust_domain)

        if not k8s_service:
            k8s_service = kubernetes_client.V1Service()
            k8s_service.metadata = kubernetes_client.V1ObjectMeta(name=o.name)

            ports=[]
            for service_port in o.serviceports.all():
                port=kubernetes_client.V1ServicePort(name = service_port.name,
                                                  node_port = service_port.external_port,
                                                  port = service_port.internal_port,
                                                  target_port = service_port.internal_port,
                                                  protocol = service_port.protocol)
                ports.append(port)

            k8s_service.spec = kubernetes_client.V1ServiceSpec(ports=ports,
                                                               type="NodePort")

            self.v1.create_namespaced_service(trust_domain.name, k8s_service)

    def delete_record(self, o):
        # TODO(smbaker): Implement delete step
        pass

