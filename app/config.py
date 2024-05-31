# app/config.py
import os
from dotenv import load_dotenv
load_dotenv()
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
    MONGO_URI = os.environ.get('MONGO_URI')
    MONGO_DB_NAME = os.environ.get('MONGO_DB_NAME')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SMTP_SERVER = os.environ.get('SMTP_SERVER')
    SMTP_PORT = int(os.environ.get('SMTP_PORT'))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD')