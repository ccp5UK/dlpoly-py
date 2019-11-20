"""
Module containing utility functions supporting the DLPOLY Python Workflow
"""

import itertools
from abc import ABC

COMMENT_CHAR = "#"

def peek(iterable):
    """ Test generator without modifying """
    try:
        first = next(iterable)
    except StopIteration:
        return None
    return itertools.chain([first], iterable)

def read_line(inFile):
    """ Read a line, stripping comments and blank lines """
    line = None
    while not line:
        line = inFile.readline().split(COMMENT_CHAR)[0].strip()
        if line is None:
            raise IOError("Attempted to read line at EOF")
    return line

class DLPData(ABC):
    """ Abstract datatype for handling automatic casting and restricted assignment """
    def __init__(self, dataTypes):
        self._dataTypes = dataTypes

    dataTypes = property(lambda self: self._dataTypes)
    keys = property(lambda self: [key for key in self.dataTypes])
    className = property(lambda self: type(self).__name__)

    def __setattr__(self, key, val):
        if key == "_dataTypes":
            return
        if key not in self.dataTypes:
            print("Param {} not allowed in {} definition".format(key, self.className.lower()))
            return

        val = self._map_types(key, val)
        self.__dict__[key] = val

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        setattr(self, key, val)

    def _map_types(self, key, vals):
        """ Map argument types to their respective types """
        if not isinstance(self.dataTypes[key], tuple):
            try:
                val = self.dataTypes[key](vals)
            except TypeError:
                print('Type of {} ({}) not valid, must be castable to {}'.format(vals, type(vals).__name__,
                                                                                 self.dataTypes[key].__name__))
        else:
            try:
                val = [targetType(item) for item, targetType in zip(vals, self.dataTypes[key][key])]
            except TypeError:
                print('Type of {} ({}) not valid, must be castable to {}'.format(vals,
                                                                                 [type(x).__name__ for x in vals],
                                                                                 [x.__name__ for x in self.dataTypes[key]]))
        return val
