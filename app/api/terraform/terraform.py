# api/terraform/terraform.py
import subprocess
from .base_terraform_api import BaseTerraformAPI

class TerraformAPI(BaseTerraformAPI):

    def __init__(self, app):
        self.working_dir = app.config['TERRAFORM_WORKING_DIR']

    def _run_terraform_command(self, command):
        try:
            result = subprocess.run(
                command,
                cwd=self.working_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return {'status': 'success', 'output': result.stdout.decode()}
        except subprocess.CalledProcessError as e:
            return {'status': 'error', 'output': e.stderr.decode()}

    def init(self):
        command = ['terraform', 'init']
        return self._run_terraform_command(command)
    

    def apply(self):
        command = ['terraform', 'apply', '-auto-approve']
        return self._run_terraform_command(command)

    def destroy(self):
        command = ['terraform', 'destroy', '-auto-approve']
        return self._run_terraform_command(command)
    

def get_terraform_api(app):
    return  TerraformAPI(app)