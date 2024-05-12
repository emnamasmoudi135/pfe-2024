# app/__init__.py
from flask import Flask
from .config import Config
from .api.terraform.terraform import get_terraform_api
from .api.proxmox.proxmox import get_proxmox_api

app = Flask(__name__)
app.config.from_object(Config)

# Crée une instance de la classe ProxmoxAPI
proxmox_api = get_proxmox_api(app)
terraform_api=get_terraform_api(app)

from app import routes
