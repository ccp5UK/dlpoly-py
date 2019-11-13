#!/usr/bin/env python3
"""
Module to handle DLPOLY config files
"""

class Specie():
    """ Class defining a DLPOLY specie type """
    params = {'element': str, 'id':int, 'charge': float,
            'mass':float, 'fronzen':bool,'repeats':int}

    def __init__(self, **d):
        self.element = 'X'
        self.id = 1
        self.charge = 0.0
        self.mass = 1.0
        self.frozen = False
        self.repeats = 1
     

    def __str__(self):
       return "{0:8s} {1:f} {2:f} {3:d} {4:d}\n".format(self.element,self.mass,self.charge,self.repeats, 1 if self.frozen else 0 )
    
    def __getitem__(self, key):
       return getattr(self, key)

    def __setitem__(self, key, val):
        if key not in Specie.params:
            raise KeyError('Param {} not valid param name in specie description.'.format(key))
        if not isinstance(val, Specie.params[key]):
            raise ValueError(
                'Type of {} not valid, must be {}'.format(type(val).__name__,
                                                          Specie.params[key].__name__))
        setattr(self, key, val)

    params = property(lambda self: [key for key in Specie.params])

class Atom():
    """ Class defining a DLPOLY atom type """

class Config():
    """ Class defining a DLPOLY config file """


if __name__ == '__main__':
    pass
