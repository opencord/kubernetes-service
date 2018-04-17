
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
    sync_kubernetesserviceinstance.py

    Synchronize KubernetesServiceInstance. See also the related pull_step.

    This sync_step is intended to handle the case where callers are creating pods directly, as opposed to using
    a controller to manage pods for them. It makes some simplifying assumptions, such as each pod has one
    container and uses one image.
"""

from synchronizers.new_base.syncstep import SyncStep
from synchronizers.new_base.modelaccessor import KubernetesServiceInstance

from xosconfig import Config
from multistructlog import create_logger

from kubernetes.client.rest import ApiException
from kubernetes import client as kubernetes_client, config as kubernetes_config

log = create_logger(Config().get('logging'))

class SyncKubernetesServiceInstance(SyncStep):

    """
        SyncKubernetesServiceInstance

        Implements sync step for syncing kubernetes service instances.
    """

    provides = [KubernetesServiceInstance]
    observes = KubernetesServiceInstance
    requested_interval = 0

    def __init__(self, *args, **kwargs):
        super(SyncKubernetesServiceInstance, self).__init__(*args, **kwargs)
        kubernetes_config.load_incluster_config()
        self.v1 = kubernetes_client.CoreV1Api()

    def get_pod(self, o):
        """ Given a KubernetesServiceInstance, read the pod from Kubernetes.
            Return None if the pod does not exist.
        """
        try:
            pod = self.v1.read_namespaced_pod(o.name, o.slice.trust_domain.name)
        except ApiException, e:
            if e.status == 404:
                return None
            raise
        return pod

    def sync_record(self, o):
        if o.xos_managed:
            if (not o.slice) or (not o.slice.trust_domain):
                raise Exception("No trust domain for service instance", o=o)

            if (not o.name):
                raise Exception("No name for service instance", o=o)

            pod = self.get_pod(o)
            if not pod:
                # make a pod!
                pod = kubernetes_client.V1Pod()
                pod.metadata = kubernetes_client.V1ObjectMeta(name=o.name)

                if o.slice.trust_domain:
                    pod.metadata.namespace = o.slice.trust_domain.name

                if o.image.tag:
                    imageName = o.image.name + ":" + o.image.tag
                else:
                    # TODO(smbaker): Is this case possible?
                    imageName = o.image.name

                container=kubernetes_client.V1Container(name=o.name,
                                                        image=imageName)

                spec = kubernetes_client.V1PodSpec(containers=[container])
                pod.spec = spec

                if o.slice.principal:
                    pod.spec.service_account = o.slice.principal.name

                log.info("Creating pod", o=o, pod=pod)

                pod = self.v1.create_namespaced_pod(o.slice.trust_domain.name, pod)

            if (not o.backend_handle):
                o.backend_handle = pod.metadata.self_link
                o.save(update_fields=["backend_handle"])

    def delete_record(self, port):
        # TODO(smbaker): Implement delete step
        pass

