# -*- coding: utf-8 -*-


from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        pass
