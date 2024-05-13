import requests
import urllib3
from requests.exceptions import HTTPError
from .BaseProxmoxApi import BaseProxmoxAPI

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProxmoxAPI(BaseProxmoxAPI):

    def __init__(self, app):
        """
        Initialize the ProxmoxAPI instance with the application context.

        Args:
            app: The application context containing configuration such as Proxmox URL and credentials.
        """
        self.app = app
        self.base_url = app.config['PROXMOX_URL']
        self.session = requests.Session()
        self.session.verify = False  # Disable SSL verification

    def make_request(self, method, url, **kwargs):
        """
        Centralized HTTP request handling method that includes error management.

        Args:
            method: HTTP method to use ('GET', 'POST', 'PUT', 'DELETE').
            url: API endpoint URL.
            **kwargs: Additional arguments to pass to requests method.

        Returns:
            tuple: (success, data or None) where success is a boolean indicating the outcome.
        """
        full_url = f"{self.base_url}{url}"
        try:
            response = self.session.request(method, full_url, **kwargs)
            response.raise_for_status()
            return True, response.json().get('data', None)
        except HTTPError as http_err:
            return False, None
        except Exception as err:
            return False, None

    def login(self, url):
        """
        Authenticate against the Proxmox API using provided credentials.

        Args:
            url: Endpoint URL for login.

        Returns:
            tuple: (success, data or None) indicating whether login was successful and session details.
        """
        payload = {
            'username': self.app.config['PROXMOX_USER'],
            'password': self.app.config['PROXMOX_PASSWORD'],
        }
        success, data = self.make_request('POST', url, data=payload)
        if success:
            self.session.cookies.set('PVEAuthCookie', data['ticket'])
            self.session.headers.update({'CSRFPreventionToken': data['CSRFPreventionToken']})
        return success, data

    def list_vms(self, url):
        """
        Retrieve a list of VMs from the Proxmox server.

        Args:
            url: Endpoint URL for listing VMs.

        Returns:
            tuple: (success, data or None) with the list of VMs or error.
        """
        return self.make_request('GET', url)

    def create_vm(self, url, vm_config):
        """
        Create a new VM on the Proxmox server with the specified configuration.

        Args:
            url: Endpoint URL for VM creation.
            vm_config: Configuration settings for the new VM.

        Returns:
            tuple: (success, data or None) with the creation result or error.
        """
        return self.make_request('POST', url, json=vm_config)

    def destroy_vm(self, url):
        """
        Delete a VM from the Proxmox server.

        Args:
            url: Endpoint URL for VM deletion.

        Returns:
            tuple: (success, data or None) indicating whether the VM was successfully deleted.
        """
        return self.make_request('DELETE', url)

    def update_vm(self, url, vm_config):
        """
        Update the configuration of an existing VM.

        Args:
            url: Endpoint URL for VM update.
            vm_config: Updated configuration settings for the VM.

        Returns:
            tuple: (success, data or None) with the update result or error.
        """
        return self.make_request('PUT', url, data=vm_config)

    def get_vm_status(self, url):
        """
        Retrieve the status of a specific VM from the Proxmox server.

        Args:
            url: Endpoint URL for fetching VM status.

        Returns:
            tuple: (success, data or None) with the status information or error.
        """
        return self.make_request('GET', url)

def get_proxmox_api(app):
    """
    Factory function to create a new instance of ProxmoxAPI with the provided application context.

    Args:
        app: The application context to use.

    Returns:
        ProxmoxAPI: A new instance of ProxmoxAPI.
    """
    return ProxmoxAPI(app)
