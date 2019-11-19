"""
Module containing utility functions supporting the DLPOLY Python Workflow
"""

import itertools

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
        

def map_types(targetTypes, vals):
    """ Map argument types to their respective types """
    if not isinstance(targetTypes, tuple):
        try:
            val = targetTypes(vals)
        except TypeError:
            raise ValueError(
                'Type of {} ({}) not valid, must be castable to {}'.format(vals, type(vals).__name__,
                                                                           Control.params[key].__name__))
    else:
        try:
            val = [targetType(item) for item, targetType in zip(vals, targetTypes[key])]
        except TypeError:
            raise ValueError(
                'Type of {} ({}) not valid, must be castable to {}'.format(vals,
                                                                           [type(x).__name__ for x in vals],
                                                                           [x.__name__ for x in  targetTypes]))
    return val
