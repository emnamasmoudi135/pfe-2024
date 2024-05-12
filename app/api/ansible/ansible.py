import os
from app.ssh_connection import SSHConnection  # Assure-toi que le chemin d'importation est correct
class Ansible:
    def __init__(self):
        # Initialiser la connexion SSH
        self.ssh_connection = SSHConnection()

    def deploy_playbook(self, playbook_name,app):
        local_path = os.path.join(app.config['LOCAL_PLAYBOOKS_DIR'], playbook_name.strip())
        remote_path = os.path.join(app.config['REMOTE_PLAYBOOKS_DIR'], playbook_name.strip())
        
        # Connecter et transférer le playbook
        self.ssh_connection.connect()
        try:
            self.ssh_connection.upload_file(local_path, remote_path)
            return f"Playbook {playbook_name} deployed successfully."
        finally:
            self.ssh_connection.disconnect()

    def execute_playbook(self, playbook_name,app):
        playbook_dir = app.config['REMOTE_PLAYBOOKS_DIR']
        inventory_path = app.config['INVENTORY_PATH']
        command = f"cd {playbook_dir} && ansible-playbook -i {inventory_path} {playbook_name}"
        
        # Connecter et exécuter le playbook
        self.ssh_connection.connect()
        try:
            stdin, stdout, stderr = self.ssh_connection.client.exec_command(command)
            output = stdout.read().decode()
            error = stderr.read().decode()
            return output if not error else error
        finally:
            self.ssh_connection.disconnect()


