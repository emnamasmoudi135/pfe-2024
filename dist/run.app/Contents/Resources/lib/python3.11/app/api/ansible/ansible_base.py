from abc import ABC, abstractmethod
from typing import Tuple, Optional, Any

class AnsibleBase(ABC):

    @abstractmethod
    def add_and_deploy_playbook(self, playbook_name: str, playbook_content: str) -> Tuple[bool, Optional[Any], Optional[int]]:
        pass

    @abstractmethod
    def execute_playbook(self, playbook_name: str) -> Tuple[bool, Optional[str], Optional[int]]:
        pass

    @abstractmethod
    def modify_playbook(self, playbook_name: str) -> Tuple[bool, Optional[str], Optional[int]]:
        pass

    @abstractmethod
    def list_playbooks(self) -> Tuple[bool, Optional[list[str]], Optional[int]]:
        pass

    @abstractmethod
    def delete_playbook(self, playbook_name: str) -> Tuple[bool, Optional[str], Optional[int]]:
        pass

    @abstractmethod
    def modify_hosts_file(self, new_content: str) -> Tuple[bool, Optional[str], Optional[int]]:
        pass

    @abstractmethod
    def playbook_detail(self, playbook_name: str) -> Tuple[bool, Optional[Any], Optional[int]]:
        pass
