# -*- coding: utf-8 -*-


from abc import ABC, abstractmethod


class Command(ABC):
    @abstractmethod
    def init(self, sub_parser, common_parser):
        pass
