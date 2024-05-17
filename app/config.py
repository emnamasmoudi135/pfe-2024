# app/config.py
import os

class Config(object):
    PROXMOX_URL = os.environ.get('PROXMOX_URL')
    PROXMOX_USER = os.environ.get('PROXMOX_USER')
    PROXMOX_PASSWORD = os.environ.get('PROXMOX_PASSWORD')
    TERRAFORM_WORKING_DIR = os.environ.get('TERRAFORM_WORKING_DIR')
    SSH_HOSTNAME=os.environ.get('SSH_HOSTNAME')
    SSH_USERNAME=os.environ.get('SSH_USERNAME')
    SSH_PASSWORD=os.environ.get('SSH_PASSWORD')
    LOCAL_PLAYBOOKS_DIR=os.environ.get('LOCAL_PLAYBOOKS_DIR')
    REMOTE_PLAYBOOKS_DIR=os.environ.get('REMOTE_PLAYBOOKS_DIR')
    INVENTORY_PATH=os.environ.get('INVENTORY_PATH')
    SSH_PORT=int(os.environ.get('SSH_PORT'))
    OPENAI_API_KEY =os.environ.get('OPENAI_API_KEY')