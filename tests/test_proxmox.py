import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import MagicMock
from app import app
from app.api.proxmox.proxmox import ProxmoxAPI

class TestProxmoxAPI(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        self.proxmox_api = ProxmoxAPI(self.app)
        self.proxmox_api.session = MagicMock()

    def tearDown(self):
        self.app_context.pop()

    def test_list_vms(self):
        self.proxmox_api.session.request.return_value.json.return_value = {'data': 'vm_list'}
        success, data, status_code = self.proxmox_api.list_vms('/api2/json/nodes/localhost/qemu')
        self.assertTrue(success)
        self.assertEqual(data, 'vm_list')

    def test_create_vm(self):
        self.proxmox_api.session.request.return_value.json.return_value = {'data': 'vm_created'}
        success, data, status_code = self.proxmox_api.create_vm('/api2/json/nodes/localhost/qemu', {'name': 'test-vm'})
        self.assertTrue(success)
        self.assertEqual(data, 'vm_created')

if __name__ == '__main__':
    unittest.main()
