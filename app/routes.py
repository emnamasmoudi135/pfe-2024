
# app/routes.py
from flask import jsonify , request
from app import app, proxmox_api ,terraform_api 
from app.api.ansible.ansible import Ansible


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
    """
    Modify an existing playbook by uploading new content.

    This endpoint accepts new content for a specified playbook and updates it
    on the remote server. The playbook to be modified is specified in the URL,
    and the new content must be provided in the JSON payload.

    Args:
        playbook_name (str): The name of the playbook to modify.

    Returns:
        A JSON response indicating whether the modification was successful or not.

    Example Request Body:
        - {"new_content": "---\n- hosts: all\n  tasks:\n    - name: update"}

    Example Response:
        - Success: 200 OK, {"message": "Playbook updated successfully."}
        - Error: 400 Bad Request, {"error": "New content is required"}
    """
    data = request.get_json()
    new_content = data.get('new_content')
    if not new_content:
        return jsonify({'error': 'New content is required'}), 400

    ansible_instance = Ansible()
    return jsonify(ansible_instance.modify_playbook(playbook_name, new_content))


@app.route('/add-playbook/<playbook_name>', methods=['POST'])
def add_playbook(playbook_name):
    """
    Add a new playbook to the remote server.

    This endpoint uploads a new playbook to the remote server. The name of the
    new playbook and its content must be provided. The content of the playbook
    should be included in the request's JSON body.

    Args:
        playbook_name (str): The name of the playbook to be added.

    Returns:
        A JSON response indicating the result of the operation.

    Example Request Body:
        - {"content": "---\n- hosts: all\n  tasks:\n    - name: install nginx"}

    Example Response:
        - Success: 200 OK, {"message": "Playbook added successfully."}
        - Error: 400 Bad Request, {"error": "Playbook content is required"}
    """
    playbook_content = request.json.get('content')
    if not playbook_content:
        return jsonify({'error': 'Playbook content is required'}), 400

    ansible = Ansible()
    return jsonify(ansible.add_and_deploy_playbook(playbook_name, playbook_content))

  
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















