
# app/routes.py
from flask import jsonify , request
from app import app, proxmox_api ,terraform_api 
from app.api.ansible.ansible import Ansible

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




# @app.route('/deploy-playbook/<playbook_name>', methods=['POST'])
# def deploy_playbook(playbook_name):
#     ansible = Ansible()  # Créer une nouvelle instance de la classe Ansible
#     result = ansible.deploy_playbook(playbook_name,app)  # Appel de la méthode d'instance
#     return jsonify({'message': result})

# @app.route('/execute-playbook/<playbook_name>', methods=['POST'])
# def execute_playbook(playbook_name):
#     ansible = Ansible()  # Créer une nouvelle instance de la classe Ansible
#     result = ansible.execute_playbook(playbook_name,app)  # Appel de la méthode d'instance
#     return jsonify({'message': result})













# @app.route('/terraform/init', methods=['GET'])
# def terraform_init():
#     result = terraform_api.init()
#     return jsonify(result)

# @app.route('/terraform/apply', methods=['POST'])
# def terraform_apply():
#     result = terraform_api.apply()
#     return jsonify(result)

# @app.route('/terraform/destroy', methods=['POST'])
# def terraform_destroy():
#     result = terraform_api.destroy()
#     return jsonify(result)


