"""
Module containing utility functions supporting the DLPOLY Python Workflow
"""


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
