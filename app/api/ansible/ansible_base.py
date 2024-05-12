from abc import ABC, abstractmethod

class AnsibleBase(ABC):
    @abstractmethod
    def deploy_playbook(self, playbook_name):
        pass

    @abstractmethod
    def execute_playbook(self, playbook_name):
        pass
