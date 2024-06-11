from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, Optional

class BaseProxmoxAPI(ABC):

    @abstractmethod
    def login(self, url: str) -> Tuple[bool, Optional[Dict], Optional[int]]:
        pass

    @abstractmethod
    def list_vms(self, url: str) -> Tuple[bool, Optional[Dict], Optional[int]]:
        pass

    @abstractmethod
    def create_vm(self, url: str, vm_config: Dict[str, Any]) -> Tuple[bool, Optional[Dict], Optional[int]]:
        pass

    @abstractmethod
    def destroy_vm(self, url: str) -> Tuple[bool, Optional[Dict], Optional[int]]:
        pass

    @abstractmethod
    def update_vm(self, url: str, vm_config: Dict[str, Any]) -> Tuple[bool, Optional[Dict], Optional[int]]:
        pass

    @abstractmethod
    def get_vm_status(self, url: str) -> Tuple[bool, Optional[Dict], Optional[int]]:
        pass

    @abstractmethod
    def get_node_statistics(self, url: str) -> Tuple[bool, Optional[Dict], Optional[int]]:
        pass

    @abstractmethod
    def start_vm(self, url: str) -> Tuple[bool, Optional[Dict], Optional[int]]:
        pass

    @abstractmethod
    def stop_vm(self, url: str) -> Tuple[bool, Optional[Dict], Optional[int]]:
        pass
