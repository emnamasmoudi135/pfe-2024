import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
from unittest.mock import patch
from flask import Flask
from app.api.terraform.terraform import TerraformAPI
from app import app

class TestTerraformAPI(unittest.TestCase):

    def setUp(self):
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.app.config['TERRAFORM_WORKING_DIR'] = '/tmp/terraform'
        self.terraform_api = TerraformAPI(self.app)

    def tearDown(self):
        self.app_context.pop()

    @patch('subprocess.run')
    def test_init(self, mock_run):
        mock_run.return_value.stdout.decode.return_value = 'init_output'
        success, output = self.terraform_api.init()
        self.assertTrue(success)
        self.assertEqual(output, 'init_output')

    @patch('subprocess.run')
    def test_apply(self, mock_run):
        mock_run.return_value.stdout.decode.return_value = 'apply_output'
        success, output = self.terraform_api.apply()
        self.assertTrue(success)
        self.assertEqual(output, 'apply_output')

    @patch('subprocess.run')
    def test_destroy(self, mock_run):
        mock_run.return_value.stdout.decode.return_value = 'destroy_output'
        success, output = self.terraform_api.destroy()
        self.assertTrue(success)
        self.assertEqual(output, 'destroy_output')

if __name__ == '__main__':
    unittest.main()
