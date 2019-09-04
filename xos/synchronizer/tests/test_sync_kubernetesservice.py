
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

import json
import os
import sys
import unittest
from mock import patch, PropertyMock, ANY, MagicMock
from unit_test_common import setup_sync_unit_test

class ApiException(Exception):
    def __init__(self, status, *args, **kwargs):
        super(ApiException, self).__init__(*args, **kwargs)
        self.status = status

def fake_init_kubernetes_client(self):
    self.api_instance = MagicMock()
    self.ApiException = ApiException

class TestSyncKubernetesServiceInstance(unittest.TestCase):

    def setUp(self):
        self.unittest_setup = setup_sync_unit_test(os.path.abspath(os.path.dirname(os.path.realpath(__file__))),
                                                   globals(),
                                                   [("kubernetes-service", "kubernetes.xproto")] )

        self.MockObjectList = self.unittest_setup["MockObjectList"]
        self.model_accessor = self.unittest_setup["model_accessor"]

        sys.path.append(os.path.join(os.path.abspath(os.path.dirname(os.path.realpath(__file__))), "../steps"))

        from sync_kubernetes_service import SyncK8Service
        self.step_class = SyncK8Service

        self.service = KubernetesService(name="TestK8")

    def tearDown(self):
        sys.path = self.unittest_setup["sys_path_save"]

    def test_valid_version(self):

        version = MagicMock()
        version.major = '1'
        version.minor = '13'
        version.git_version = "v1.13.0"

        with patch.object(self.step_class, "init_kubernetes_client", new=fake_init_kubernetes_client):
            step = self.step_class(model_accessor=self.model_accessor)

            step.api_instance.get_code.return_value = version

            step.sync_record(self.service)

    def test_valid_version_int(self):

        version = MagicMock()
        version.major = 1
        version.minor = 13
        version.git_version = "v1.13.0"

        with patch.object(self.step_class, "init_kubernetes_client", new=fake_init_kubernetes_client):
            step = self.step_class(model_accessor=self.model_accessor)

            step.api_instance.get_code.return_value = version

            step.sync_record(self.service)

    def test_invalid_version(self):

        version = MagicMock()
        version.major = 1
        version.minor = 16
        version.git_version = "v1.16.0"

        with patch.object(self.step_class, "init_kubernetes_client", new=fake_init_kubernetes_client):
            step = self.step_class(model_accessor=self.model_accessor)

            step.api_instance.get_code.return_value = version

            with self.assertRaises(Exception):
                step.sync_record(self.service)


if __name__ == '__main__':
    unittest.main()
