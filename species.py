"""
DLPOLY Species class
"""

class Species():
    """ Class defining a DLPOLY species type """
    params = {'element': str, 'id': int, 'charge': float,
              'mass': float, 'frozen': bool, 'repeats': int}

    def __init__(self, name="X", id=1, charge=0.0, mass=1.0, frozen=False, repeats=1):
        self.element = name
        self.id = id
        self.charge = charge
        self.mass = mass
        self.frozen = frozen
        self.repeats = repeats

    def __str__(self):
        return "{0:8s} {1:f} {2:f} {3:d} {4:d}\n".format(self.element, self.mass,
                                                         self.charge, self.repeats,
                                                         int(self.frozen))

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        map_types(self.params[key], val)
        setattr(self, key, val)

    params = property(lambda self: [key for key in Species.params])
