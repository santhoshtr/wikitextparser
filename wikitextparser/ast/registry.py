from abc import ABCMeta
from typing import Dict


class Nodes(ABCMeta):
    registry: Dict[str, type] = {}

    def __init__(cls, name, bases, attrs):
        """
        Here the name of the class is used as key but it could be any class
        parameter.
        """
        if name not in ["Node", "Leaf", "Tree"]:
            Nodes.registry[cls.NAME] = cls

    @classmethod
    def get_registry(cls) -> Dict[str, type]:
        return cls.registry
