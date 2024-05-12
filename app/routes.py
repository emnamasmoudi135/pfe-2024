
# app/routes.py
from flask import jsonify , request
from app import app, proxmox_api ,terraform_api 
from app.api.ansible.ansible import Ansible


@app.route('/deploy-playbook/<playbook_name>', methods=['POST'])
def deploy_playbook(playbook_name):
    ansible = Ansible()  # Créer une nouvelle instance de la classe Ansible
    result = ansible.deploy_playbook(playbook_name,app)  # Appel de la méthode d'instance
    return jsonify({'message': result})

@app.route('/execute-playbook/<playbook_name>', methods=['POST'])
def execute_playbook(playbook_name):
    ansible = Ansible()  # Créer une nouvelle instance de la classe Ansible
    result = ansible.execute_playbook(playbook_name,app)  # Appel de la méthode d'instance
    return jsonify({'message': result})













@app.route('/terraform/init', methods=['GET'])
def terraform_init():
    result = terraform_api.init()
    return jsonify(result)

@app.route('/terraform/apply', methods=['POST'])
def terraform_apply():
    result = terraform_api.apply()
    return jsonify(result)

@app.route('/terraform/destroy', methods=['POST'])
def terraform_destroy():
    result = terraform_api.destroy()
    return jsonify(result)


from flask import jsonify
from app import app, proxmox_api

@app.route('/nodes/<string:node>/vms', methods=['GET'])
def get_node_vms(node):
    try:
        vms_list = proxmox_api.list_vms(node)
        return jsonify(vms_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


































@app.route('/login-proxmox')
def login_proxmox():
    return jsonify({"message": proxmox_api.login()})


@app.route('/list-vms')
def list_vms():
    return jsonify(proxmox_api.list_vms())

@app.route('/create-vm', methods=['POST'])
def create_vm_route():
    vm_config = request.json  # Récupérer le JSON de la requête
    if not vm_config:
        return jsonify({"error": "Pas de données fournies"}), 400
    result = proxmox_api.create_vm(vm_config)
    if "succès" in result:
        return jsonify({"message": result}), 200
    else:
        return jsonify({"error": result}), 500



@app.route('/destroy-vm/<node>/<int:vmid>', methods=['DELETE'])
def destroy_vm_route(node, vmid):
    result = proxmox_api.destroy_vm(node, vmid)
    if "succès" in result:
        return jsonify({"message": result}), 200
    else:
        return jsonify({"error": result}), 500




@app.route('/update-vm/<string:node>/<int:vmid>', methods=['PUT'])
def update_vm_route(node, vmid):
    vm_config = request.json
    if not vm_config:
        return jsonify({"error": "Aucune configuration fournie"}), 400
    result = proxmox_api.update_vm(node, vmid, vm_config)
    if "succès" in result:
        return jsonify({"message": result}), 200
    else:
        return jsonify({"error": result}), 500
    
   


@app.route('/vm-status/<string:node>/<int:vmid>', methods=['GET'])
def vm_status_route(node, vmid):
    vm_status = proxmox_api.get_vm_status(node, vmid)
    if vm_status:
        return jsonify(vm_status), 200
    else:
        return jsonify({"error": "Impossible de récupérer l'état de la VM"}), 500

