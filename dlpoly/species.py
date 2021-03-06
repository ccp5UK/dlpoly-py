"""
DLPOLY Species class
"""

from dlpoly.utility import DLPData


class Species(DLPData):
    """ Class defining a DLPOLY species type """
    def __init__(self, name="X", index=1, charge=0.0, mass=1.0, frozen=False, repeats=1):
        DLPData.__init__(self, {'element': str, 'index': int, 'charge': float,
                                'mass': float, 'frozen': bool, 'repeats': int})
        self.element = name
        self.index = index
        self.charge = charge
        self.mass = mass
        self.frozen = frozen
        self.repeats = repeats

    def __str__(self):
        return "{0:8s} {1:f} {2:f} {3:d} {4:d}".format(self.element, self.mass, self.charge,
                                                       self.repeats, int(self.frozen))
