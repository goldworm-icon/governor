# -*- coding: utf-8 -*-


from abc import ABC, abstractmethod
from typing import Tuple


class Command(ABC):
    def __init__(self, name: str, readonly: bool):
        self._name = name
        self._readonly = readonly

    @property
    def name(self) -> str:
        return self._name.lower()

    @property
    def readonly(self) -> bool:
        """
        If this command does not change the state of blockchain, return True
        :return: bool
        """
        return self._readonly

    @property
    def key(self) -> Tuple[bool, str]:
        return not self._readonly, self._name

    @abstractmethod
    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        pass
