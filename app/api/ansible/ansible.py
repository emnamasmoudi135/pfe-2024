import os
import tempfile
from typing import Tuple, Optional, Any
from flask import current_app
from app.ssh_connection import SSHConnection

class Ansible:
    def __init__(self):
        self.ssh_connection = SSHConnection()

    def handle_exception(self, exception: Exception) -> Tuple[bool, Optional[Any], Optional[int]]:
        """
        Handle exceptions uniformly across methods.

        Args:
            exception (Exception): The exception that was raised.

        Returns:
            tuple: (False, None, error_code) where False indicates the operation failed,
                   None shows there is no data to return, and error_code is the specific error code.
        """
        if isinstance(exception, HTTPError):
            return False, None, exception.response.status_code
        return False, None, 500

    def add_and_deploy_playbook(self, playbook_name: str, playbook_content: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Add and deploy an Ansible playbook using SSH.

        Args:
            playbook_name (str): The name of the playbook file.
            playbook_content (str): The content of the playbook.

        Returns:
            Tuple[bool, Optional[str], Optional[int]]: (success, message, status_code)
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(playbook_content.encode('utf-8'))
                local_path = temp_file.name

            remote_path = os.path.join(current_app.config['REMOTE_PLAYBOOKS_DIR'], playbook_name)

            # Connect and transfer the playbook
            self.ssh_connection.connect()
            try:
                self.ssh_connection.upload_file(local_path, remote_path)
            finally:
                self.ssh_connection.disconnect()
                os.remove(local_path)

            return True, f"Playbook {playbook_name} deployed successfully.", None
        except Exception as e:
            return self.handle_exception(e)

    def execute_playbook(self, playbook_name: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Execute an Ansible playbook that is already deployed.

        Args:
            playbook_name (str): The name of the playbook to execute.

        Returns:
            Tuple[bool, Optional[str], Optional[int]]: (success, result, status_code)
        """
        playbook_dir = current_app.config['REMOTE_PLAYBOOKS_DIR']
        inventory_path = current_app.config['INVENTORY_PATH']
        command = f"ansible-playbook -i {inventory_path} {playbook_name}"
        try:
            self.ssh_connection.connect()
            try:
                stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"cd {playbook_dir} && {command}")
                output = stdout.read().decode()
                error = stderr.read().decode()
                if error:
                    return False, error, None
                return True, output, None
            finally:
                self.ssh_connection.disconnect()
        except Exception as e:
            return self.handle_exception(e)
        

    def modify_playbook(self, playbook_name: str, new_content: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Check if a playbook exists and modify it if it does.

        Args:
            playbook_name (str): The name of the playbook to be modified.
            new_content (str): The new content to replace the existing playbook content.

        Returns:
            Tuple[bool, Optional[str], Optional[int]]: (success, message, status_code)
        """
        remote_path = os.path.join(current_app.config['REMOTE_PLAYBOOKS_DIR'], playbook_name)
        self.ssh_connection.connect()
        try:
            # Check if file exists
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"test -f {remote_path} && echo exists")
            if stdout.read().decode().strip() != "exists":
                return False, "Playbook does not exist.", 404

            # If file exists, write to a temporary file and upload it
            with tempfile.NamedTemporaryFile(delete=False, mode='w+') as temp_file:
                temp_file.write(new_content)
                local_path = temp_file.name

            self.ssh_connection.upload_file(local_path, remote_path)
            return True, "Playbook modified successfully.", None
        except Exception as e:
            return False, f"Error modifying playbook: {str(e)}", 500
        finally:
            self.ssh_connection.disconnect()
            if 'local_path' in locals():
                os.remove(local_path)
