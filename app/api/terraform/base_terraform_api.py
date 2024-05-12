# api/base_terraform_api.py
from abc import ABC, abstractmethod

class BaseTerraformAPI(ABC):

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def apply(self):
        pass

    @abstractmethod
    def destroy(self):
        pass

#nahyt hedha mel parametre w zid thabet  destroy_config