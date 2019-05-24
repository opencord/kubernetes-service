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


from xossynchronizer.steps.syncstep import SyncStep
from xossynchronizer.modelaccessor import KubernetesService

from xosconfig import Config
from multistructlog import create_logger

log = create_logger(Config().get('logging'))

class SyncK8Service(SyncStep):
    provides = [KubernetesService]
    observes = KubernetesService

    max_version = "1.14"
    [expected_major, expected_minor] = max_version.split(".")

    def __init__(self, *args, **kwargs):
        super(SyncK8Service, self).__init__(*args, **kwargs)
        self.init_kubernetes_client()

    def init_kubernetes_client(self):
        from kubernetes.client.rest import ApiException
        from kubernetes import client as kubernetes_client, config as kubernetes_config
        kubernetes_config.load_incluster_config()
        self.api_instance = kubernetes_client.VersionApi(kubernetes_client.ApiClient())
        self.ApiException = ApiException

    def sync_record(self, o):
        log.info("[K8Service SyncStep] Sync'ing model", model=o, name=o.name)

        res = self.api_instance.get_code()
        major = res.major
        minor = res.minor
        log.debug("[K8Service SyncStep] API response", res=res)
        log.info("[K8Service SyncStep] API Code", major=major, minor=minor,
                 expected_major=self.expected_major, expected_minor=self.expected_minor)

        if int(major) != int(self.expected_major) or int(minor) > int(self.expected_minor):
            raise Exception("Kubernetes cluster of version %s is not supported by the kubernetes-services" % res.git_version+
                            "the maximum supported version is %s" % self.max_version)

    def delete_record(self, o):
        pass