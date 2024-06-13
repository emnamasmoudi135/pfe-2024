# app/__init__.py
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_pymongo import PyMongo
from .config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

jwt = JWTManager(app)
mongo = PyMongo(app)

from .api.terraform.terraform import get_terraform_api
from .api.proxmox.proxmox import get_proxmox_api

proxmox_api = get_proxmox_api(app)
terraform_api = get_terraform_api(app)

from app import routes


