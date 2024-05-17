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
                
                
    def list_playbooks(self) -> tuple[bool, Optional[list[str]], Optional[int]]:
        """
        List all Ansible playbooks in the remote directory.

        Returns:
            Tuple[bool, Optional[List[str]], Optional[int]]: (success, list of playbooks, status_code)
        """
        playbook_dir = current_app.config['REMOTE_PLAYBOOKS_DIR']
        self.ssh_connection.connect()
        try:
            # Listing command adjusted to your SSH setup and playbook directory structure
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"ls {playbook_dir}/*.yml")
            error = stderr.read().decode()
            if error:
                return False, None, 500

            playbooks = stdout.read().decode().strip().split('\n')
            # Cleanup filenames to return only the names, not full paths
            playbooks = [os.path.basename(pb) for pb in playbooks]
            return True, playbooks, None
        except Exception as e:
            return False, None, 500
        finally:
            self.ssh_connection.disconnect()


    def delete_playbook(self, playbook_name: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Delete an existing playbook from the remote server.

        Args:
            playbook_name (str): The name of the playbook to be deleted.

        Returns:
            Tuple[bool, Optional[str], Optional[int]]: (success, message, status_code)
        """
        remote_path = os.path.join(current_app.config['REMOTE_PLAYBOOKS_DIR'], playbook_name)
        self.ssh_connection.connect()
        try:
            # Check if the playbook exists
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"test -f {remote_path} && echo exists")
            if stdout.read().decode().strip() != "exists":
                return False, "Playbook does not exist.", 404

            # Delete the playbook if it exists
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"rm {remote_path}")
            error = stderr.read().decode()
            if error:
                return False, error, 500

            return True, "Playbook deleted successfully.", None
        except Exception as e:
            return False, f"Error deleting playbook: {str(e)}", 500
        finally:
            self.ssh_connection.disconnect()

    def modify_hosts_file(self, new_content: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Modify the hosts.ini file on the remote server.
        """
        hosts_path = current_app.config['INVENTORY_PATH']  # Ensure this is correctly fetching the path
        self.ssh_connection.connect()
        try:
            # Command to check if the hosts.ini file exists
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"test -f {hosts_path} && echo exists")
            if stdout.read().decode().strip() != "exists":
                return False, "hosts.ini does not exist.", 404

            # Command to write new content to hosts.ini
            with tempfile.NamedTemporaryFile('w', delete=False) as tmp_file:
                tmp_file.write(new_content)
                local_path = tmp_file.name

            self.ssh_connection.upload_file(local_path, hosts_path)
            os.remove(local_path)
            return True, "hosts.ini modified successfully.", None
        except Exception as e:
            return False, f"Error modifying hosts.ini: {str(e)}", 500
        finally:
            self.ssh_connection.disconnect()


    def playbook_detail(self, playbook_name: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Retrieve the content of a specified playbook from the remote server.

        Args:
            playbook_name (str): The name of the playbook to retrieve.

        Returns:
            Tuple[bool, Optional[str], Optional[int]]: (success, content or error message, status code)
        """
        playbook_path = os.path.join(current_app.config['REMOTE_PLAYBOOKS_DIR'], playbook_name)
        self.ssh_connection.connect()
        try:
            # Check if the playbook exists
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"test -f {playbook_path} && echo exists")
            if stdout.read().decode().strip() != "exists":
                return False, "Playbook does not exist.", 404

            # Read the playbook content if it exists
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"cat {playbook_path}")
            content = stdout.read().decode()
            return True, content, None
        except Exception as e:
            return False, f"Error retrieving playbook: {str(e)}", 500
        finally:
            self.ssh_connection.disconnect()

    # def generate_playbook_from_ai(self,tool):
    #     """
    #     Génère un playbook Ansible en utilisant le modèle de langage GPT. 
    #     """
    
    #     try:
    #         openai.api_key = current_app.config['OPENAI_API_KEY']
    #         response = openai.ChatCompletion.create(
    #             model="gpt-3.5-turbo",
    #             messages=[
    #                 {"role": "system", "content": "You are a helpful assistant."},
    #                 {"role": "user", "content": f"Write an Ansible playbook for installing and configuring {tool}."}
    #             ]
    #         )
    #         playbook_content = response['choices'][0]['message']['content']
    #         return True, playbook_content
    #     except Exception as e:
    #         return False, str(e)
    



    # def deploy_generated_playbook(tool, playbook_content):
    #     ansible = Ansible()
    #     playbook_name = f"{tool}.yml"
    #     success, message, _ = ansible.add_and_deploy_playbook(playbook_name, playbook_content)
    #     if success:
    #         return jsonify({'success': True, 'message': message}), 200
    #     else :
    #         return jsonify({'success': False, 'message': message}), 400
        






# import requests

# api_key = 'sk-proj-UvXWZxoOYmgSCux7ocPsT3BlbkFJBfBVC1CwteGKfuSeopGO'
# headers = {
#     'Authorization': f'Bearer {api_key}'
# }

# data = {
#     'model': 'gpt-3.5-turbo',
#     'prompt': 'Hello, world!',
#     'max_tokens': 5
# }

# response = requests.post('https://api.openai.com/v1/completions', headers=headers, json=data)
# print(response.json())

import flask
print(flask.__version__)