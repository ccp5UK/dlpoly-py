#!/usr/bin/env python3
"""
Module to handle DLPOLY control files
"""


from collections import namedtuple
import collections
import six

IOTypes = namedtuple('IOTypes', 'config field statsout')
Ignore = namedtuple('Ignore', 'elec index strict topology vdw')

# python 3.8+ compatibility
try:
    collectionsAbc = collections.abc
except AttributeError:
    collectionsAbc = collections

class Control():
    """ Class defining a DLPOLY control file """
    params = {'binsize': float, 'cap': float, 'close time': float,
              'collect': bool, 'coulomb': bool, 'cutoff': float,
              'defects': (list, tuple), 'densvar': float,
              'distance': float, 'displacements': (list, tuple),
              'dump': int, 'ensemble': (list, tuple), 'epsilon': float,
              'equilibration': int, 'ewald': (list, tuple), 'exclude': bool,
              'finish': bool, 'impact': (list, tuple), 'integrator': str,
              'io': (list, tuple), 'job time': float, 'maxdis': float,
              'metal': bool, 'mindis': float, 'minimise': (list, tuple),
              'msdtmp': (list, tuple), 'multiple': int, 'mxquat': int,
              'mxshak': int, 'mxstep': float, 'nfold': (list, tuple),
              'ignore': (list, tuple), 'optimise': (list, tuple),
              'pressure': float, 'print': int, 'print rdf': bool,
              'print zden': bool, 'psuedo': (list, tuple), 'quaternion': float,
              'rdf': int, 'reaction': (list, tuple), 'regauss': int, 'replay': bool,
              'restart': (list, tuple), 'rlxtol': float, 'rvdw': float, 'scale': int,
              'seed': (list, tuple), 'shift': (list, tuple), 'slab': bool,
              'stack': bool, 'stats': bool, 'steps': bool, 'temperature': float,
              'title': str, 'trajectory': (list, tuple), 'timestep': float,
              'variable': float, 'vdw': str, 'zden': int, 'zero': bool}

    def __init__(self, **d):
        self.temperature = 300.0
        self.finish = True
        self.title = 'no title'
        self.io = type('ioParam', (),
                       {'field': 'FIELD', 'config': 'CONFIG', 'outstats': 'STATIS',
                        '__str__': lambda self: (f'io field {self.field}\n'
                                                 f'io config {self.config}\n'
                                                 f'io outstats {self.outstats}')})
        self.ensemble = dict(type='nve', flavour='langevin', aniso='',
                           f=0.5, f1=0.5, f2=0.5, f3=0.5, gamma=0.5, semi=False)
        self.pressure = 0.0
        self.collect = False
        self.steps = 10
        self.equilibration = 5
        self.print = 1
        self.stats = 1
        self.cutoff = 0.0
        self.variable = False
        self.timestep = 0.001

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        if key not in Control.params:
            raise KeyError('Param {} not valid param name in control file.'.format(key))
        if not isinstance(val, Control.params[key]):
            raise ValueError(
                'Type of {} not valid, must be {}'.format(type(val).__name__,
                                                          Control.params[key].__name__))
        setattr(self, key, val)

    params = property(lambda self: [key for key in Control.params])

    def write(self, filename="CONTROL"):
        ctrl = self.adddire('title', nokey=True)

        for key, val in self.d.items():
            if key not in ['finish', 'title']:
                if key == 'ensemble':
                    ctrl += self.addensemble(val)
                elif key in ['rdf', 'analysis', 'vaf', 'zden']:
                    ctrl += self.addprint(key)
                elif key in ['job', 'close']:
                    ctrl += self.addattrib(key, 'time')
                elif key == 'io':
                    ctrl += self.addio(val)
                elif key == 'variable':
                    x = 0
                elif key == 'timestep':
                    ctrl += self.addtimestep(val)
                else:
                    ctrl += self.adddire(key)

        ctrl += self.adddire('finish', nokey=True)
        with open(filename, "w") as outFile:
          outFile.write(ctrl)

if __name__ == '__main__':
    pass
