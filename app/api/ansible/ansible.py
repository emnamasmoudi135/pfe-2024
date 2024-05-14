import os
from flask import current_app
from app.ssh_connection import SSHConnection
import tempfile

class Ansible:
    def __init__(self):
        self.ssh_connection = SSHConnection()

    def add_and_deploy_playbook(self, playbook_name, playbook_content):
        # Utiliser un fichier temporaire pour stocker le contenu du playbook
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(playbook_content.encode('utf-8'))
            local_path = temp_file.name
        
        remote_path = os.path.join(current_app.config['REMOTE_PLAYBOOKS_DIR'], playbook_name)
        
        # Connecter et transférer le playbook
        self.ssh_connection.connect()
        try:
            self.ssh_connection.upload_file(local_path, remote_path)
            return f"Playbook {playbook_name} deployed successfully."
        except Exception as e:
            return f"Failed to deploy playbook: {str(e)}"
        finally:
            self.ssh_connection.disconnect()
            os.remove(local_path)

    def execute_playbook(self, playbook_name):
        playbook_dir = current_app.config['REMOTE_PLAYBOOKS_DIR']
        inventory_path = current_app.config['INVENTORY_PATH']
        command = f"cd {playbook_dir} && ansible-playbook -i {inventory_path} {playbook_name}"
        
        self.ssh_connection.connect()
        try:
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            return output if not error else error
        finally:
            self.ssh_connection.disconnect()



