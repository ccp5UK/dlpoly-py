'''
Module containing utility functions supporting the DLPOLY Python Workflow
'''

import math
import itertools
import numpy as np
from abc import ABC
import shutil

COMMENT_CHAR = '#'


def copy_file(inpf, od):
    """ copy a file in a folder, avoiding same file error"""
    try:
        shutil.copy(inpf, od)
    except shutil.SameFileError:
        pass


def peek(iterable):
    ''' Test generator without modifying '''
    try:
        first = next(iterable)
    except StopIteration:
        return None
    return itertools.chain([first], iterable)


def parse_line(line):
    ''' Handle comment chars and whitespace '''
    return line.split(COMMENT_CHAR)[0].strip()


def read_line(inFile):
    ''' Read a line, stripping comments and blank lines '''
    line = None
    for line in inFile:
        line = parse_line(line)
        if line:
            break
    else:
        line = None
    return line


def build_3d_rotation_matrix(alpha=0., beta=0., gamma=0., units='rad'):
    ''' Build a rotation matrix in degrees or radians '''
    if units == 'deg':
        alpha, beta, gamma = map(lambda x: x*math.pi/180, (alpha, beta, gamma))
    salp, sbet, sgam = map(np.sin, (alpha, beta, gamma))
    calp, cbet, cgam = map(np.cos, (alpha, beta, gamma))
    matrix = np.asarray([[cbet*cgam, cgam*salp*sbet - calp*sgam, calp*cgam*sbet + salp*sgam],
                         [cbet*sgam, calp*cgam+salp*sbet*sgam, calp*sbet*sgam-cgam*salp],
                         [-1.*sbet, cbet*salp, calp*cbet]], dtype=float)
    return matrix


class DLPData(ABC):
    ''' Abstract datatype for handling automatic casting and restricted assignment '''

    def __init__(self, dataTypes):
        self._dataTypes = dataTypes

    dataTypes = property(lambda self: self._dataTypes)
    keys = property(lambda self: [key for key in self.dataTypes if key != 'keysHandled'])
    className = property(lambda self: type(self).__name__)

    def dump(self):
        for key in self.keys:
            print(key, self[key])

    def __setattr__(self, key, val):
        if key == '_dataTypes':  # Protect datatypes

            if not hasattr(self, '_dataTypes'):
                self.__dict__[key] = {**val, 'keysHandled': tuple}
            else:
                print('Cannot alter dataTypes')
            return

        if key == 'source':  # source is not really a keyword
            return

        if key not in self.dataTypes:
            print('Param {} not allowed in {} definition'.format(key, self.className.lower()))
            return

        val = self._map_types(key, val)
        self.__dict__[key] = val

    def __getitem__(self, key):
        """ Fuzzy matching on get/set item """
        key = check_arg(key, *self.keys)
        return getattr(self, str(key))

    def __setitem__(self, keyIn, val):
        """ Fuzzy matching on get/set item """
        key = check_arg(keyIn, *self.keys)
        if not key:
            raise KeyError(f'"{keyIn}" is not a member of {type(self).__name__}')
        setattr(self, key, val)

    def _map_types(self, key, vals):
        ''' Map argument types to their respective types '''
        dType = self._dataTypes[key]
        if isinstance(vals, (tuple, list)) and not isinstance(dType, (tuple, bool)) and dType is not tuple:
            if not vals:
                pass
            elif len(vals) == 1:
                vals = vals[0]
            else:
                for arg in vals:
                    try:
                        vals = arg
                        break
                    except TypeError:
                        pass
                else:
                    raise TypeError('No arg of {} ({}) for key {} valid, must be castable to {}'.format(
                        vals,
                        [type(x).__name__ for x in vals], key,
                        dType.__name__))

        if isinstance(dType, tuple):

            if isinstance(vals, (int, float, str)):
                vals = (vals,)

            try:
                if ... in dType:
                    loc = dType.index(...)
                    if loc != len(dType)-1:
                        pre, ellided, post = dType[:loc], dType[loc-1], dType[loc+1:]
                        val = ([targetType(item) for item, targetType in zip(vals[:loc], pre)] +
                               [ellided(item) for item in vals[loc:-len(post)]] +
                               [targetType(item) for item, targetType in zip(vals[-len(post):], post)])
                    else:
                        pre, ellided = dType[:loc], dType[loc-1]
                        val = ([targetType(item) for item, targetType in zip(vals[:loc], pre)] +
                               [ellided(item) for item in vals[loc:]])

                else:
                    val = [targetType(item) for item, targetType in zip(vals, dType)]
            except TypeError:
                print('Type of {} ({}) not valid, must be castable to {}'.format(vals,
                                                                                 [type(x).__name__ for x in vals],
                                                                                 [x.__name__ for x in dType]))

        elif isinstance(vals, dType):  # Already right type
            val = vals
        elif dType is bool:  # If present true unless explicitly false
            val = vals not in (0, False)

        else:
            # print(key, vals)
            try:
                val = self._dataTypes[key](vals)
            except TypeError as err:
                print(err)
                print('Type of {} ({}) not valid, must be castable to {}'.format(vals, type(vals).__name__,
                                                                                 dType.__name__))
        return val


def check_arg(key, *args):
    for arg in args:
        if key.startswith(arg):
            return arg
    return False
