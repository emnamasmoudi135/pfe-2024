from abc import ABC, abstractmethod

class BaseProxmoxAPI(ABC):

    @abstractmethod
    def login(self):
        pass

    @abstractmethod
    def list_vms(self):
        pass

    @abstractmethod
    def create_vm(self, vm_config):
        pass

    @abstractmethod
    def destroy_vm(self, node, vmid):
        pass

    @abstractmethod
    def update_vm(self, node, vmid, vm_config):
        pass

    @abstractmethod
    def get_vm_status(self, node, vmid):
        pass
