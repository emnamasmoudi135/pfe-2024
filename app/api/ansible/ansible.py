import os
import tempfile
from typing import Tuple, Optional, Any
from flask import current_app, request, jsonify
import yaml
from app.ssh_connection import SSHConnection

class Ansible:
    def __init__(self):
        self.ssh_connection = SSHConnection()

    def handle_exception(self, exception: Exception) -> Tuple[bool, Optional[Any], Optional[int]]:
        if isinstance(exception, HTTPError):
            return False, None, exception.response.status_code
        return False, None, 500
    

    def add_and_deploy_playbook(self, playbook_name, playbook_content):
        try:
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                temp_file.write(playbook_content.encode('utf-8'))
                local_path = temp_file.name

            remote_path = os.path.join(current_app.config['REMOTE_PLAYBOOKS_DIR'], playbook_name)

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

    def modify_playbook(self, playbook_name: str) -> Tuple[bool, Optional[str], Optional[int]]:
        remote_path = os.path.join(current_app.config['REMOTE_PLAYBOOKS_DIR'], playbook_name)
        new_content = request.json.get('new_content')

        self.ssh_connection.connect()
        try:
            # Check if file exists
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"test -f {remote_path} && echo exists")
            if stdout.read().decode().strip() != "exists":
                return False, "Playbook does not exist.", 404

            # Parse new content into YAML
            try:
                yaml_content = yaml.safe_load(new_content)
            except yaml.YAMLError as e:
                return False, f"Error parsing YAML: {str(e)}", 400

            # Write YAML to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, mode='w+') as temp_file:
                yaml.dump(yaml_content, temp_file)
                local_path = temp_file.name

            # Upload the new content to the remote playbook
            self.ssh_connection.upload_file(local_path, remote_path)
            return True, "Playbook modified successfully.", None
        except Exception as e:
            return False, f"Error modifying playbook: {str(e)}", 500
        finally:
            self.ssh_connection.disconnect()
            if 'local_path' in locals():
                os.remove(local_path)

    def list_playbooks(self) -> Tuple[bool, Optional[list[str]], Optional[int]]:
        playbook_dir = current_app.config['REMOTE_PLAYBOOKS_DIR']
        self.ssh_connection.connect()
        try:
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"ls {playbook_dir}/*.yml")
            error = stderr.read().decode()
            if error:
                return False, None, 500

            playbooks = stdout.read().decode().strip().split('\n')
            playbooks = [os.path.basename(pb) for pb in playbooks]
            return True, playbooks, None
        except Exception as e:
            return False, None, 500
        finally:
            self.ssh_connection.disconnect()

    def delete_playbook(self, playbook_name: str) -> Tuple[bool, Optional[str], Optional[int]]:
        remote_path = os.path.join(current_app.config['REMOTE_PLAYBOOKS_DIR'], playbook_name)
        self.ssh_connection.connect()
        try:
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"test -f {remote_path} && echo exists")
            if stdout.read().decode().strip() != "exists":
                return False, "Playbook does not exist.", 404

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
        hosts_path = current_app.config['INVENTORY_PATH']
        self.ssh_connection.connect()
        try:
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"test -f {hosts_path} && echo exists")
            if stdout.read().decode().strip() != "exists":
                return False, "hosts.ini does not exist.", 404

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

    def playbook_detail(self, playbook_name: str) -> Tuple[bool, Optional[Any], Optional[int]]:
        playbook_path = os.path.join(current_app.config['REMOTE_PLAYBOOKS_DIR'], playbook_name)
        self.ssh_connection.connect()
        try:
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"test -f {playbook_path} && echo exists")
            if stdout.read().decode().strip() != "exists":
                return False, "Playbook does not exist.", 404

            stdin, stdout, stderr = self.ssh_connection.client.exec_command(f"cat {playbook_path}")
            content = stdout.read().decode()
            try:
                parsed_content = yaml.safe_load(content)
            except yaml.YAMLError as e:
                return False, f"Error parsing YAML: {str(e)}", 500

            return True, parsed_content, None
        except Exception as e:
            return False, f"Error retrieving playbook: {str(e)}", 500
        finally:
            self.ssh_connection.disconnect()
