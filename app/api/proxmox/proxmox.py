import requests
import urllib3
from requests.exceptions import HTTPError
from .BaseProxmoxApi import BaseProxmoxAPI
from contextlib import contextmanager


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
            tuple: (success, data or None, status_code) where success is a boolean indicating the outcome,
                   data is the JSON response or None, and status_code is the HTTP status code from the error.
        """
        full_url = f"{self.base_url}{url}"
        try:
            response = self.session.request(method, full_url, **kwargs)
            response.raise_for_status()
            return True, response.json().get('data', None), None
        except HTTPError as http_err:
            # Here we return False, and the error from the server
            return False, None, http_err.response.status_code
        except Exception as error:
            # For other exceptions, you may choose to return a generic error code such as 500.
            return False, None,  error.response.status_code
        
    @contextmanager
    def login_context(self, url):
        """
        A context manager to handle API login and ensure the session is closed on exit.

        Args:
            url: Endpoint URL for login.

        Yields:
            The ProxmoxAPI instance itself.
        """
        try:
            self.login(url)
            yield self
        finally:
            self.session.close()

    def login(self, url):
        payload = {
            'username': self.app.config['PROXMOX_USER'],
            'password': self.app.config['PROXMOX_PASSWORD'],
        }
        success, data, status_code = self.make_request('POST', url, data=payload)
        if success:
            self.session.cookies.set('PVEAuthCookie', data['ticket'])
            self.session.headers.update({'CSRFPreventionToken': data['CSRFPreventionToken']})
        return success, data, status_code
    
    def list_vms(self, url):
        """
        Retrieve a list of VMs from the Proxmox server.

        Args:
            url: Endpoint URL for listing VMs.

        Returns:
            tuple: (success, data or None, status_code) with the list of VMs or error and the status code.
        """
        return self.make_request('GET', url)

    def create_vm(self, url, vm_config):
        """
        Create a new VM on the Proxmox server with the specified configuration.

        Args:
            url: Endpoint URL for VM creation.
            vm_config: Configuration settings for the new VM.

        Returns:
            tuple: (success, data or None, status_code) with the creation result or error and the status code.
        """
        return self.make_request('POST', url, json=vm_config)

    def destroy_vm(self, url):
        """
        Delete a VM from the Proxmox server.

        Args:
            url: Endpoint URL for VM deletion.

        Returns:
            tuple: (success, data or None, status_code) indicating whether the VM was successfully deleted and the status code.
        """
        return self.make_request('DELETE', url)

    def update_vm(self, url, vm_config):
        """
        Update the configuration of an existing VM.

        Args:
            url: Endpoint URL for VM update.
            vm_config: Updated configuration settings for the VM.

        Returns:
            tuple: (success, data or None, status_code) with the update result or error and the status code.
        """
        return self.make_request('PUT', url, data=vm_config)

    def get_vm_status(self, url):
        """
        Retrieve the status of a specific VM from the Proxmox server.

        Args:
            url: Endpoint URL for fetching VM status.

        Returns:
            tuple: (success, data or None, status_code) with the status information or error and the status code.
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

