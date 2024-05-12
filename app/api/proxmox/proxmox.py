import requests
import urllib3
from requests.exceptions import HTTPError
from .BaseProxmoxApi import BaseProxmoxAPI


# Désactiver les avertissements de vérification SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProxmoxAPI(BaseProxmoxAPI):


    def __init__(self, app):
        self.app = app
        self.base_url = app.config['PROXMOX_URL']
        self.session = requests.Session()
        self.session.verify = False  # Désactiver la vérification SSL

    def login(self):
        login_url = f"{self.base_url}/access/ticket"
        payload = {
            'username': self.app.config['PROXMOX_USER'],
            'password': self.app.config['PROXMOX_PASSWORD'],
        }
        try:
            response = self.session.post(login_url, data=payload)
            response.raise_for_status()
            data = response.json()['data']
            self.session.cookies.set('PVEAuthCookie', data['ticket'])
            self.session.headers.update({'CSRFPreventionToken': data['CSRFPreventionToken']})
            return "Connexion réussie à Proxmox API."
        except HTTPError as http_err:
            return f"HTTP error occurred: {http_err}"
        except Exception as err:
            return f"Other error occurred: {err}"
        
        





        

        
    def list_vms(self, node):
        vms_url = f"{self.base_url}/nodes/{node}/qemu"
        try:
           response = self.session.get(vms_url)
           response.raise_for_status()
           return response.json()['data']  # Retourne directement la liste des VMs
        except HTTPError as http_err:
           return f"HTTP error occurred: {http_err}"
        except Exception as err:
           return f"Other error occurred: {err}"


        
        





    def create_vm(self, vm_config):
        create_url = f"{self.base_url}/nodes/{vm_config['node']}/qemu"
        try:
            response = self.session.post(create_url, json=vm_config)  # Utilise l'argument `json` pour envoyer le payload en JSON
            response.raise_for_status()
            return f"VM créée avec succès : {response.json()}"
        except HTTPError as http_err:
            return f"Erreur HTTP lors de la création de la VM : {http_err}"
        except Exception as err:
            return f"Autre erreur survenue : {err}"
        
        
    

    def destroy_vm(self, node, vmid):
        destroy_url = f"{self.base_url}/nodes/{node}/qemu/{vmid}"
        try:
            response = self.session.delete(destroy_url)
            response.raise_for_status()
            return f"VM {vmid} supprimée avec succès sur le nœud {node}."
        except HTTPError as http_err:
            return f"Erreur HTTP lors de la suppression de la VM : {http_err}"
        except Exception as err:
            return f"Autre erreur survenue : {err}"
        


 
    

    def update_vm(self, node, vmid, vm_config):
        update_url = f"{self.base_url}/nodes/{node}/qemu/{vmid}/config"
        try:
            response = self.session.put(update_url, data=vm_config)
            response.raise_for_status()
            return f"VM {vmid} mise à jour avec succès sur le nœud {node}."
        except HTTPError as http_err:
            return f"Erreur HTTP lors de la mise à jour de la VM : {http_err}"
        except Exception as err:
            return f"Autre erreur survenue : {err}"
        


    

    def get_vm_status(self, node, vmid):
        status_url = f"{self.base_url}/nodes/{node}/qemu/{vmid}/status/current"
        try:
            response = self.session.get(status_url)
            response.raise_for_status()
            vm_status = response.json()['data']
            return vm_status
        except HTTPError as http_err:
            return f"Erreur HTTP lors de la récupération de l'état de la VM : {http_err}"
        except Exception as err:
            return f"Autre erreur survenue : {err}"
        



def get_proxmox_api(app):
    return ProxmoxAPI(app)
