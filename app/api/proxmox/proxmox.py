import requests
import urllib3
from requests.exceptions import HTTPError
from .BaseProxmoxApi import BaseProxmoxAPI
from contextlib import contextmanager
from typing import Any, Dict, Tuple, Optional, Generator

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ProxmoxAPI(BaseProxmoxAPI):

    def __init__(self, app: Any) -> None:
        """
        Initialize the ProxmoxAPI instance with the application context.

        Args:
            app: The application context containing configuration such as Proxmox URL and credentials.
        """
        self.app = app
        self.base_url: str = app.config['PROXMOX_URL']
        self.session: requests.Session = requests.Session()
        self.session.verify = False  # Disable SSL verification

    def make_request(self, method: str, url: str, **kwargs: Any) -> Tuple[bool, Optional[Dict], Optional[int]]:
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
            return False, None, http_err.response.status_code
        except Exception:
            return False, None, 500 
        
    @contextmanager
    def login_context(self, url: str) -> Generator['ProxmoxAPI', None, None]:
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

    def login(self, url: str) -> Tuple[bool, Optional[Dict], Optional[int]]:
        payload = {
            'username': self.app.config['PROXMOX_USER'],
            'password': self.app.config['PROXMOX_PASSWORD'],
        }
        success, data, status_code = self.make_request('POST', url, data=payload)
        if success and data:
            self.session.cookies.set('PVEAuthCookie', data['ticket'])
            self.session.headers.update({'CSRFPreventionToken': data['CSRFPreventionToken']})
        return success, data, status_code
    
    def list_vms(self, url: str) -> Tuple[bool, Optional[Dict], Optional[int]]:
        return self.make_request('GET', url)

    def create_vm(self, url: str, vm_config: Dict[str, Any]) -> Tuple[bool, Optional[Dict], Optional[int]]:
        return self.make_request('POST', url, json=vm_config)

    def destroy_vm(self, url: str) -> Tuple[bool, Optional[Dict], Optional[int]]:
        return self.make_request('DELETE', url)

    def update_vm(self, url: str, vm_config: Dict[str, Any]) -> Tuple[bool, Optional[Dict], Optional[int]]:
        return self.make_request('PUT', url, data=vm_config)

    def get_vm_status(self, url: str) -> Tuple[bool, Optional[Dict], Optional[int]]:
        return self.make_request('GET', url)

def get_proxmox_api(app: Any) -> ProxmoxAPI:
    """
    Factory function to create a new instance of ProxmoxAPI with the provided application context.

    Args:
        app: The application context to use.

    Returns:
        ProxmoxAPI: A new instance of ProxmoxAPI.
    """
    return ProxmoxAPI(app)
