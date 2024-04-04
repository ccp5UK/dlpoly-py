'''
Module to handle miscellaneous input files
'''

from abc import ABC, abstractmethod

from .types import PathLike, OptPath


class Input(ABC):

    def __init__(self, source: OptPath = None):
        self.source = source

    @abstractmethod
    def read(self, source: PathLike):
        self.source = source


class VDW(Input):

    def read(self, source: PathLike = "TABVDW"):
        self.source = source


class EAM(Input):

    def read(self, source: PathLike = "TABEAM"):
        self.source = source


class BND(Input):

    def read(self, source: PathLike = "TABBND"):
        self.source = source


class ANG(Input):

    def read(self, source: PathLike = "TABANG"):
        self.source = source


class DIH(Input):

    def read(self, source: PathLike = "TABDIH"):
        self.source = source


class INV(Input):

    def read(self, source: PathLike = "TABINV"):
        self.source = source
