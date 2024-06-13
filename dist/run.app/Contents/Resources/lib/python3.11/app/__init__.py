# app/__init__.py
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required
from .config import Config
from .api.terraform.terraform import get_terraform_api
from .api.proxmox.proxmox import get_proxmox_api
from flask_cors import CORS

app = Flask(__name__)
app.config.from_object(Config)
jwt = JWTManager(app)

# Configurer CORS pour permettre les requêtes de 'http://localhost:3000'
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


# Crée une instance de la classe ProxmoxAPI
proxmox_api = get_proxmox_api(app)
terraform_api = get_terraform_api(app)

from app import routes

@app.before_request
def require_authentication():
    if request.endpoint and 'auth.' not in request.endpoint:
        jwt_required()
