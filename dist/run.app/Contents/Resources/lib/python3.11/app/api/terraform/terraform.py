import subprocess
from typing import Dict, List, Any
from .base_terraform_api import BaseTerraformAPI

class TerraformAPI(BaseTerraformAPI):
    """
    Provides an interface for executing Terraform commands within a specified working directory.
    The working directory is set during the initialization of the class instance.
    """

    def __init__(self, app: Any) -> None:
        """
        Initializes the TerraformAPI with the application configuration.

        Args:
            app (Any): The application object containing configuration details.
        """
        self.working_dir: str = app.config['TERRAFORM_WORKING_DIR']

    def _run_terraform_command(self, command: List[str]) -> tuple[bool, str]:
        """
        Executes a Terraform command in the configured working directory and handles the output.

        Args:
            command (List[str]): The command to execute as a list of strings.

        Returns:
            Dict[str, str]: A dictionary containing the status ('success' or 'error') and the command output.
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.working_dir,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return (True, result.stdout.decode())
        except subprocess.CalledProcessError as e:
            return (False, e.stderr.decode())

    def init(self) -> Dict[str, str]:
        """
        Initializes a Terraform working environment by running `terraform init`.

        Returns:
            Dict[str, str]: The output from the initialization command.
        """
        return self._run_terraform_command(['terraform', 'init'])

    def apply(self) -> Dict[str, str]:
        """
        Applies the Terraform changes automatically without manual approval by using `terraform apply -auto-approve`.

        Returns:
            Dict[str, str]: The output from the apply command.
        """
        return self._run_terraform_command(['terraform', 'apply', '-auto-approve'])

    def destroy(self) -> Dict[str, str]:
        """
        Destroys the Terraform managed infrastructure by using `terraform destroy -auto-approve`.

        Returns:
            Dict[str, str]: The output from the destroy command.
        """
        return self._run_terraform_command(['terraform', 'destroy', '-auto-approve'])
    

def get_terraform_api(app: Any) -> TerraformAPI:
    """
    Factory function to create a TerraformAPI instance.

    Args:
        app (Any): The application object to pass to the TerraformAPI constructor.

    Returns:
        TerraformAPI: An instance of the TerraformAPI class.
    """
    return TerraformAPI(app)
