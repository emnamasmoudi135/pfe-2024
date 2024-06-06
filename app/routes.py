
# app/routes.py
from flask import jsonify , request
from app import app, proxmox_api ,terraform_api 
from app.api.ansible.ansible import Ansible
from flask_cors import CORS
CORS(app)
from dotenv import load_dotenv, set_key, unset_key
import os
from app.api.userManagement.auth import Auth


#authentification routes :

@app.route('/signup', methods=['POST'])
def signup():
    return Auth.signup()

@app.route('/login', methods=['POST'])
def login():
    return Auth.login()

@app.route('/logout', methods=['POST'])
def logout():
    return Auth.logout()

@app.route('/verify-email', methods=['GET'])
def verify_email():
    return Auth.verify_email()

@app.route('/confirm-login', methods=['GET'])
def confirm_login():
    return Auth.confirm_login()

#ansible routes

# Endpoint to get environment variables
@app.route('/env', methods=['GET'])
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
        "OPENAI_API_KEY": os.getenv('OPENAI_API_KEY')
    }
    return jsonify(env_vars)



@app.route('/env', methods=['PUT'])
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
def playbook_detail(playbook_name):
    """
    API endpoint to retrieve the content of a specific playbook.

    This endpoint allows clients to view the content of an Ansible playbook by specifying
    its name. If the playbook exists, it returns the content; otherwise, it returns an error.

    Args:
        playbook_name (str): The name of the playbook whose content is to be retrieved.

    Returns:
        A JSON response containing the playbook content or an error message.

    Example Response:
        - Success: 200 OK, {"content": "---\n- hosts: all\n  tasks:\n    ..."}
        - Error: 404 Not Found, {"error": "Playbook does not exist."}
        - Error: 500 Internal Server Error, {"error": "Error retrieving playbook"}
    """
    ansible_instance = Ansible()
    return jsonify(ansible_instance.playbook_detail(playbook_name))

@app.route('/get-hosts-content', methods=['GET'])
def get_hosts_content():
    """
    Get the current content of the hosts.ini file.

    Returns:
        A JSON response with the current content of the hosts.ini file.
    """
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
def modify_hosts():
    """
    Modify the content of the hosts.ini file.

    Returns:
        A JSON response indicating success or failure.
    """
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
def delete_playbook(playbook_name):
    """
    Delete a playbook from the remote server.

    This endpoint deletes a specified playbook by name. If the playbook does not exist,
    it returns an error. The deletion operation is reflected directly on the remote server.

    Args:
        playbook_name (str): The name of the playbook to delete.

    Returns:
        A JSON response indicating whether the deletion was successful or not.

    Example Response:
        - Success: 200 OK, {"message": "Playbook deleted successfully."}
        - Error: 404 Not Found, {"error": "Playbook does not exist."}
        - Error: 500 Internal Server Error, {"error": "Error deleting playbook"}
    """
    ansible_instance = Ansible()
    return jsonify(ansible_instance.delete_playbook(playbook_name))
  
@app.route('/list-playbooks', methods=['GET'])
def list_playbooks():
    """
    List all playbooks available on the remote server.

    This endpoint retrieves a list of all the Ansible playbooks that are
    stored in the specified directory on the remote server. It returns the list
    as a JSON response.

    Returns:
        A JSON response containing an array of playbook names or an error message.

    Example Response:
        - Success: 200 OK, {"playbooks": ["site.yml", "nginx.yml"]}
        - Error: 500 Internal Server Error, {"error": "Failed to retrieve playbooks"}
    """
    ansible_instance = Ansible()
    return jsonify(ansible_instance.list_playbooks())




@app.route('/modify-playbook/<playbook_name>', methods=['PUT'])
def modify_playbook(playbook_name):
    ansible_instance = Ansible()
    success, message, status_code = ansible_instance.modify_playbook(playbook_name)
    if success:
        return jsonify({'message': message}), 200
    return jsonify({'error': message}), status_code


  

  
@app.route('/execute-playbook/<playbook_name>', methods=['POST'])
def execute_playbook(playbook_name):
    """
    Execute a playbook that is already deployed on the remote server.

    This endpoint triggers the execution of a specified playbook that exists on
    the remote server. The name of the playbook to execute is provided in the URL.

    Args:
        playbook_name (str): The name of the playbook to execute.

    Returns:
        A JSON response with the output or result of the playbook execution.

    Example Response:
        - Success: 200 OK, {"message": "Playbook executed successfully."}
        - Error: 500 Internal Server Error, {"error": "Failed to execute playbook"}
    """
    ansible = Ansible()
    return jsonify(ansible.execute_playbook(playbook_name))

# proxmox routes

@app.route('/login-proxmox')
def login_proxmox():
    """
    Authenticate against the Proxmox server and obtain a session ticket.
    Returns:
        JSON response containing the session ticket and CSRF prevention token if successful, or an error message.
    """
    with proxmox_api.login_context('/access/ticket'):
        return jsonify(proxmox_api.login('/access/ticket'))

     
@app.route('/list-vms/<string:node>')
def list_vms(node):
    """
    Retrieve a list of all virtual machines (VMs) on a specified Proxmox node.
    Args:
        node (str): The name of the Proxmox node.
    Returns:
        JSON response containing a list of VMs if successful, or an error message.
    """
    return jsonify(proxmox_api.list_vms(f'/nodes/{node}/qemu'))

@app.route('/create-vm/<string:node>', methods=['POST'])
def create_vm_route(node):
    """
    Create a new virtual machine on the specified Proxmox node using provided configuration.
    Args:
        node (str): The name of the Proxmox node where the VM will be created.
    Returns:
        JSON response indicating the result of the VM creation process, either success or error message.
    """
    vm_config = request.json
    if not vm_config:
        return jsonify({"error": "No data provided"}), 400
    return jsonify(proxmox_api.create_vm(f'/nodes/{node}/qemu', vm_config))

@app.route('/destroy-vm/<string:node>/<int:vmid>', methods=['DELETE'])
def destroy_vm_route(node, vmid):
    """
    Delete an existing virtual machine from a specified Proxmox node.
    Args:
        node (str): The name of the Proxmox node.
        vmid (int): The identifier of the virtual machine to be destroyed.
    Returns:
        JSON response indicating whether the VM was successfully deleted or an error occurred.
    """
    return jsonify(proxmox_api.destroy_vm(f'/nodes/{node}/qemu/{vmid}'))

@app.route('/update-vm/<string:node>/<int:vmid>', methods=['PUT'])
def update_vm_route(node, vmid):
    """
    Update the configuration of an existing virtual machine on a specified Proxmox node.
    Args:
        node (str): The name of the Proxmox node.
        vmid (int): The identifier of the virtual machine to update.
    Returns:
        JSON response indicating the result of the update operation, either success or error message.
    """
    vm_config = request.json
    if not vm_config:
        return jsonify({"error": "No configuration provided"}), 400
    return jsonify(proxmox_api.update_vm(f'/nodes/{node}/qemu/{vmid}/config', vm_config))

@app.route('/vm-status/<string:node>/<int:vmid>', methods=['GET'])
def vm_status_route(node, vmid):
    """
    Retrieve the current status of a specified virtual machine on a Proxmox node.
    Args:
        node (str): The name of the Proxmox node.
        vmid (int): The identifier of the virtual machine whose status is being requested.
    Returns:
        JSON response with the status of the VM if successful, or an error message if not.
    """
    return jsonify(proxmox_api.get_vm_status(f'/nodes/{node}/qemu/{vmid}/status/current'))



@app.route('/proxmox/nodes/<string:node_name>/statistics', methods=['GET'])
def get_proxmox_node_statistics(node_name):
    success, data, status_code = proxmox_api.get_node_statistics(f'/nodes/{node_name}/status')
    if success:
        return jsonify(data), 200
    else:
        return jsonify({'error': 'Failed to retrieve node statistics', 'status': status_code}), status_code


@app.route('/vms/<string:node>/<int:vmid>/start', methods=['POST'])
def start_vm_route(node, vmid):
    """
    Start a virtual machine on a specified Proxmox node.
    Args:
        node (str): The name of the Proxmox node.
        vmid (int): The identifier of the virtual machine to be started.
    Returns:
        JSON response indicating whether the VM was successfully started or an error occurred.
    """
    success, data, status_code = proxmox_api.start_vm(f'/nodes/{node}/qemu/{vmid}/status/start')
    if success:
        return jsonify(data), 200
    else:
        return jsonify({'error': 'Failed to start VM', 'status_code': status_code}), status_code

@app.route('/vms/<string:node>/<int:vmid>/stop', methods=['POST'])
def stop_vm_route(node, vmid):
    """
    Stop a virtual machine on a specified Proxmox node.
    Args:
        node (str): The name of the Proxmox node.
        vmid (int): The identifier of the virtual machine to be stopped.
    Returns:
        JSON response indicating whether the VM was successfully stopped or an error occurred.
    """
    success, data, status_code = proxmox_api.stop_vm(f'/nodes/{node}/qemu/{vmid}/status/stop')
    if success:
        return jsonify(data), 200
    else:
        return jsonify({'error': 'Failed to stop VM', 'status_code': status_code}), status_code



# terraform routes 

@app.route('/terraform/init', methods=['GET'])
def terraform_init():
    """
    Initialize the Terraform environment. This route handles GET requests to set up the necessary
    infrastructure as defined in the Terraform configuration files.

    Returns:
        A JSON object containing the result of the Terraform 'init' command, including status
        and any output or error messages.
    """
    result = terraform_api.init()
    return jsonify(result)

@app.route('/terraform/apply', methods=['POST'])
def terraform_apply():
    """
    Apply Terraform configurations. This route handles POST requests to apply changes and create
    or update resources as defined in the Terraform plan.

    Returns:
        A JSON object containing the result of the Terraform 'apply' command, including status
        and any output or error messages.
    """
    result = terraform_api.apply()
    return jsonify(result)

@app.route('/terraform/destroy', methods=['POST'])
def terraform_destroy():
    """
    Destroy Terraform-managed infrastructure. This route handles POST requests to remove all
    resources managed by Terraform according to the defined plan.

    Returns:
        A JSON object containing the result of the Terraform 'destroy' command, including status
        and any output or error messages.
    """
    result = terraform_api.destroy()
    return jsonify(result)


@app.route('/terraform/config', methods=['GET'])
def get_terraform_config():
    """
    Retrieve the current Terraform configuration file content.
    """
    try:
        with open(os.path.join(terraform_api.working_dir, 'main.tf'), 'r') as file:
            content = file.read()
        return jsonify({'success': True, 'content': content})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/terraform/config', methods=['POST'])
def update_terraform_config():
    """
    Update the Terraform configuration file with the provided content.
    """
    data = request.json
    new_content = data.get('content')
    try:
        with open(os.path.join(terraform_api.working_dir, 'main.tf'), 'w') as file:
            file.write(new_content)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})












