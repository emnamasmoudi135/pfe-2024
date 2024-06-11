import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import MagicMock, patch
from flask import Flask
from app.api.ansible.ansible import Ansible
from app import app

class TestAnsible(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.config['REMOTE_PLAYBOOKS_DIR'] = '/tmp/playbooks'
        self.app.config['INVENTORY_PATH'] = '/tmp/inventory'
        self.ansible = Ansible()
        self.ansible.ssh_connection = MagicMock()

    def tearDown(self):
        self.app_context.pop()

    def test_add_and_deploy_playbook(self):
        self.ansible.ssh_connection.upload_file.return_value = True
        success, message, status_code = self.ansible.add_and_deploy_playbook('test.yml', 'content')
        self.assertTrue(success)
        self.assertEqual(message, "Playbook test.yml deployed successfully.")

    def test_execute_playbook(self):
        self.ansible.ssh_connection.client.exec_command.return_value = (None, MagicMock(read=lambda: b'output'), MagicMock(read=lambda: b''))
        success, output, status_code = self.ansible.execute_playbook('test.yml')
        self.assertTrue(success)
        self.assertEqual(output, 'output')

if __name__ == '__main__':
    unittest.main()
