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
    pull_pods.py

    Implements a syncstep to pull information about pods form Kubernetes.
"""

from synchronizers.new_base.pullstep import PullStep
from synchronizers.new_base.modelaccessor import KubernetesServiceInstance

from xosconfig import Config
from multistructlog import create_logger

from kubernetes import client as kubernetes_client, config as kubernetes_config

log = create_logger(Config().get('logging'))

class KubernetesServiceInstancePullStep(PullStep):
    """
         KubernetesServiceInstancePullStep

         Pull information from Kubernetes.
    """

    def __init__(self):
        super(KubernetesServiceInstancePullStep, self).__init__(observed_model=KubernetesServiceInstance)

        kubernetes_config.load_incluster_config()
        self.v1 = kubernetes_client.CoreV1Api()

    def pull_records(self):
        # TODO(smbaker): implement pull step here
        pass

