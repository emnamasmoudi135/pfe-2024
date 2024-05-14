import paramiko
from flask import current_app

class SSHConnection:
    def __init__(self):
        self.hostname = current_app.config['SSH_HOSTNAME']
        self.username = current_app.config['SSH_USERNAME']
        self.password = current_app.config['SSH_PASSWORD']
        self.port = int(current_app.config['SSH_PORT'])
        self.client = None
        self.sftp = None

    def connect(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.hostname, username=self.username, password=self.password, port=self.port)
        self.sftp = self.client.open_sftp()

    def disconnect(self):
        if self.sftp:
            self.sftp.close()
        if self.client:
            self.client.close()

    def upload_file(self, local_path, remote_path):
        self.sftp.put(local_path, remote_path)



