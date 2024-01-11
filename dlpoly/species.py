"""
DLPOLY Species class
"""

from .utility import DLPData


class Species(DLPData):
    """ Class defining a DLPOLY species type

        :param name: Species label
        :param index: CONFIG Index
        :param charge: Charge
        :param mass: Mass
        :param frozen: Num frozen
        :param repeats: Number of occurences

        """
    def __init__(self,
                 name: str = "X",
                 index: int = 1,
                 charge: float = 0.0,
                 mass: float = 1.0,
                 frozen: int = 0,
                 repeats: int = 1):

        DLPData.__init__(self, {'element': str, 'index': int, 'charge': float,
                                'mass': float, 'frozen': int, 'repeats': int})
        self.element = name
        self.index = index
        self.charge = charge
        self.mass = mass
        self.frozen = frozen
        self.repeats = repeats

    def __str__(self):
        return f"{self.element:8s} {self.mass:f} {self.charge:f} {self.repeats:d} {self.frozen:d}"
