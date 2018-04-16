
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
"""

from synchronizers.new_base.syncstep import SyncStep
from synchronizers.new_base.modelaccessor import KubernetesServiceInstance

from xosconfig import Config
from multistructlog import create_logger

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

    def sync_record(self, o):
        # TODO(smbaker): implement sync step here
        pass


    def delete_record(self, port):
        # TODO(smbaker): implement delete sync step here
        pass

