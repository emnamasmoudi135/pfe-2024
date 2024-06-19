# app/routes.py
from flask import jsonify, redirect, request
from app import app, proxmox_api, terraform_api, mongo
from app.api.ansible.ansible import Ansible
from flask_cors import CORS
CORS(app)
from dotenv import load_dotenv, set_key
import os
from app.api.userManagement.auth import Auth
from app.api.userManagement.auth import User

from app.api.prometheus.dashboardProxmox import (
    get_cpu_usage, get_memory_usage, get_disk_usage, get_network_usage,
    get_system_load, get_uptime
)
from app.api.userManagement.decorators import role_required
from flask_jwt_extended import jwt_required ,  get_jwt_identity

# Authentification routes
@app.route('/signup', methods=['POST'])
def signup():
    return Auth.signup()

@app.route('/login', methods=['POST'])
def login():
    return Auth.login()

@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    return Auth.logout()

@app.route('/verify-email', methods=['GET'])
def verify_email():
    return Auth.verify_email()

@app.route('/confirm-login', methods=['GET'])
def confirm_login():
    return Auth.confirm_login()


@app.route('/forgot-password', methods=['POST'])
def forgot_password():
    return Auth.forgot_password()


@app.route('/reset-password', methods=['POST'])
def reset_password():
    return Auth.reset_password()

# app/routes.py

@app.route('/reset-password', methods=['GET'])
def reset_password_page():
    token = request.args.get('token')
    return redirect(f"http://127.0.0.1:3000/reset-password?token={token}")

# Ansible routes
@app.route('/env', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_env():
    env_vars = {
        "PROXMOX_URL": os.getenv('PROXMOX_URL'),
        "PROXMOX_USER": os.getenv('PROXMOX_USER'),
        "PROXMOX_PASSWORD": os.getenv('PROXMOX_PASSWORD'),
        "TERRAFORM_WORKING_DIR": os.getenv('TERRAFORM_WORKING_DIR'),
        "SSH_HOSTNAME": os.getenv('SSH_HOSTNAME'),
        "SSH_USERNAME": os.getenv('SSH_USERNAME'),
        "SSH_PASSWORD": os.getenv('SSH_PASSWORD'),
        "LOCAL_PLAYBOOKS_DIR": os.getenv('LOCAL_PLAYBOOKS_DIR'),
        "REMOTE_PLAYBOOKS_DIR": os.getenv('REMOTE_PLAYBOOKS_DIR'),
        "INVENTORY_PATH": os.getenv('INVENTORY_PATH'),
        "SSH_PORT": os.getenv('SSH_PORT'),
        "OPENAI_API_KEY": os.getenv('OPENAI_API_KEY'),
        "MONGO_URI" : os.environ.get('MONGO_URI'),
        "MONGO_DB_NAME" : os.environ.get('MONGO_DB_NAME'),
        "SECRET_KEY" : os.environ.get('SECRET_KEY'),
        "SMTP_SERVER" :os.environ.get('SMTP_SERVER'),
        "SMTP_PORT" : int(os.environ.get('SMTP_PORT')),
        "SMTP_USERNAME" : os.environ.get('SMTP_USERNAME'),
        "SMTP_PASSWORD" : os.environ.get('SMTP_PASSWORD'),
        "PROMETHEUS_URL ": os.environ.get('PROMETHEUS_URL'),
        "JWT_SECRET_KEY" : os.environ.get('JWT_SECRET_KEY'),
        "MAIL_USE_SSL" : os.environ.get('MAIL_USE_SSL'),
        "MAIL_USE_TLS" : os.environ.get('MAIL_USE_TLS')
    }
    return jsonify(env_vars)

@app.route('/env', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_env():
    updates = request.json
    env_file = os.path.join(app.root_path, '.env')  # Utilisation de app.root_path pour obtenir le chemin racine de l'application
    try:
        for key, value in updates.items():
            set_key(env_file, key, value)
        load_dotenv(env_file)  # Recharger les variables d'environnement
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": f"Error modifying .env file: {str(e)}"}), 500

@app.route('/add-playbook/<playbook_name>', methods=['POST'])
@jwt_required()
def add_playbook(playbook_name):
    playbook_content = request.json.get('new_content')
    if not playbook_content:
        return jsonify({'error': 'Playbook content is required'}), 400

    ansible = Ansible()
    success, message, status_code = ansible.add_and_deploy_playbook(playbook_name, playbook_content)
    if not success:
        return jsonify({'error': message}), status_code
    return jsonify({'message': message}), 200

@app.route('/playbook-detail/<playbook_name>', methods=['GET'])
@jwt_required()
def playbook_detail(playbook_name):
    ansible_instance = Ansible()
    return jsonify(ansible_instance.playbook_detail(playbook_name))

@app.route('/get-hosts-content', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_hosts_content():
    current_user = get_jwt_identity()
    app.logger.info(f"Current user: {current_user}")
    if current_user.get('role') != 'admin':
        app.logger.info("User does not have admin privileges")
        return jsonify({"msg": "Forbidden"}), 403

    hosts_path = app.config['INVENTORY_PATH']
    ansible_instance = Ansible()
    ansible_instance.ssh_connection.connect()
    try:
        stdin, stdout, stderr = ansible_instance.ssh_connection.client.exec_command(f"cat {hosts_path}")
        content = stdout.read().decode()
        return jsonify({'content': content}), 200
    except Exception as e:
        return jsonify({'error': f"Error retrieving hosts.ini content: {str(e)}"}), 500
    finally:
        ansible_instance.ssh_connection.disconnect()

@app.route('/modify-hosts', methods=['POST'])
@jwt_required()
@role_required('admin')
def modify_hosts():
    new_content = request.json.get('new_content')
    hosts_path = app.config['INVENTORY_PATH']
    ansible_instance = Ansible()
    ansible_instance.ssh_connection.connect()
    try:
        stdin, stdout, stderr = ansible_instance.ssh_connection.client.exec_command(f"echo '{new_content}' > {hosts_path}")
        stdout.read()
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': f"Error modifying hosts.ini content: {str(e)}"}), 500
    finally:
        ansible_instance.ssh_connection.disconnect()

@app.route('/delete-playbook/<playbook_name>', methods=['DELETE'])
@jwt_required()
def delete_playbook(playbook_name):
    ansible_instance = Ansible()
    return jsonify(ansible_instance.delete_playbook(playbook_name))

@app.route('/list-playbooks', methods=['GET'])
@jwt_required()
def list_playbooks():
    ansible_instance = Ansible()
    return jsonify(ansible_instance.list_playbooks())

@app.route('/modify-playbook/<playbook_name>', methods=['PUT'])
@jwt_required()
def modify_playbook(playbook_name):
    ansible_instance = Ansible()
    success, message, status_code = ansible_instance.modify_playbook(playbook_name)
    if success:
        return jsonify({'message': message}), 200
    return jsonify({'error': message}), status_code

@app.route('/execute-playbook/<playbook_name>', methods=['POST'])
@jwt_required()

def execute_playbook(playbook_name):
    ansible = Ansible()
    return jsonify(ansible.execute_playbook(playbook_name))

# Proxmox routes
@app.route('/login-proxmox')
@jwt_required()
def login_proxmox():
    with proxmox_api.login_context('/access/ticket'):
        return jsonify(proxmox_api.login('/access/ticket'))

@app.route('/list-vms/<string:node>')
@jwt_required()
def list_vms(node):
    return jsonify(proxmox_api.list_vms(f'/nodes/{node}/qemu'))

@app.route('/create-vm/<string:node>', methods=['POST'])
@jwt_required()
def create_vm_route(node):
    vm_config = request.json
    if not vm_config:
        return jsonify({"error": "No data provided"}), 400
    return jsonify(proxmox_api.create_vm(f'/nodes/{node}/qemu', vm_config))

@app.route('/destroy-vm/<string:node>/<int:vmid>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def destroy_vm_route(node, vmid):
    return jsonify(proxmox_api.destroy_vm(f'/nodes/{node}/qemu/{vmid}'))

@app.route('/update-vm/<string:node>/<int:vmid>', methods=['PUT'])
@jwt_required()
def update_vm_route(node, vmid):
    vm_config = request.json
    if not vm_config:
        return jsonify({"error": "No configuration provided"}), 400
    return jsonify(proxmox_api.update_vm(f'/nodes/{node}/qemu/{vmid}/config', vm_config))

@app.route('/vm-status/<string:node>/<int:vmid>', methods=['GET'])
@jwt_required()
def vm_status_route(node, vmid):
    return jsonify(proxmox_api.get_vm_status(f'/nodes/{node}/qemu/{vmid}/status/current'))

@app.route('/proxmox/nodes/<string:node_name>/statistics', methods=['GET'])
@jwt_required()
def get_proxmox_node_statistics(node_name):
    success, data, status_code = proxmox_api.get_node_statistics(f'/nodes/{node_name}/status')
    if success:
        return jsonify(data), 200
    else:
        return jsonify({'error': 'Failed to retrieve node statistics', 'status': status_code}), status_code

@app.route('/vms/<string:node>/<int:vmid>/start', methods=['POST'])
@jwt_required()
def start_vm_route(node, vmid):
    success, data, status_code = proxmox_api.start_vm(f'/nodes/{node}/qemu/{vmid}/status/start')
    if success:
        return jsonify(data), 200
    else:
        return jsonify({'error': 'Failed to start VM', 'status_code': status_code}), status_code

@app.route('/vms/<string:node>/<int:vmid>/stop', methods=['POST'])
@jwt_required()
def stop_vm_route(node, vmid):
    success, data, status_code = proxmox_api.stop_vm(f'/nodes/{node}/qemu/{vmid}/status/stop')
    if success:
        return jsonify(data), 200
    else:
        return jsonify({'error': 'Failed to stop VM', 'status_code': status_code}), status_code

# Terraform routes
@app.route('/terraform/init', methods=['GET'])
@jwt_required()
def terraform_init():
    result = terraform_api.init()
    return jsonify(result)

@app.route('/terraform/apply', methods=['POST'])
@jwt_required()
def terraform_apply():
    result = terraform_api.apply()
    return jsonify(result)

@app.route('/terraform/destroy', methods=['POST'])
@jwt_required()
def terraform_destroy():
    result = terraform_api.destroy()
    return jsonify(result)

@app.route('/terraform/config', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_terraform_config():
    try:
        with open(os.path.join(terraform_api.working_dir, 'main.tf'), 'r') as file:
            content = file.read()
        return jsonify({'success': True, 'content': content})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/terraform/config', methods=['POST'])
@jwt_required()
@role_required('admin')
def update_terraform_config():
    data = request.json
    new_content = data.get('content')
    try:
        with open(os.path.join(terraform_api.working_dir, 'main.tf'), 'w') as file:
            file.write(new_content)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Prometheus metrics routes
@app.route('/metrics/cpu', methods=['GET'])
@jwt_required()
def cpu_usage():
    return get_cpu_usage()

@app.route('/metrics/memory', methods=['GET'])
@jwt_required()
def memory_usage():
    return get_memory_usage()

@app.route('/metrics/disk', methods=['GET'])
@jwt_required()
def disk_usage():
    return get_disk_usage()

@app.route('/metrics/network', methods=['GET'])
@jwt_required()
def network_usage():
    return get_network_usage()

@app.route('/metrics/system_load', methods=['GET'])
@jwt_required()
def system_load():
    return get_system_load()

@app.route('/metrics/uptime', methods=['GET'])
@jwt_required()
def uptime():
    return get_uptime()

# User management
@app.route('/users', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_users():
    user = User()
    users = user.get_all_users()
    return jsonify(users), 200

@app.route('/users/<user_id>/role', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_user_role(user_id):
    data = request.get_json()
    new_role = data.get('role')
    if not new_role:
        return jsonify({"error": "Role is required"}), 400

    user = User()
    if user.update_user_role(user_id, new_role):
        return jsonify({"message": "Role updated successfully"}), 200
    return jsonify({"error": "Failed to update role"}), 400
