#!/usr/bin/env python3
'''
Module to handle DLPOLY control files
'''
class Ignore:
    ''' Class definining properties that can be ignored '''
    __slots__ = ('elec', 'index', 'strict', 'topology', 'vdw')
    def __init__(self):
        self.elec = False
        self.index = False
        self.strict = False
        self.topology = False
        self.vdw = False

    def __str__(self):
        outStr = ''
        for item in self.__slots__:
            if getattr(self, item):
                outStr += f'no {item}\n'
        return outStr

class IOParam:
    ''' Class defining io parameters '''
    __slots__ = ('field', 'config', 'outstats')
    def __init__(self):
        self.field = 'FIELD'
        self.config = 'CONFIG'
        self.outstats = 'STATIS'

    def __str__(self):
        return (f'io field {self.field}\n' # First IO is key
                f'io config {self.config}\n'
                f'io outstats {self.outstats}')

class EnsembleParam:
    ''' Class containing ensemble data '''
    validMeans = {'nve': (None),
                  'nvt': ('evans', 'langevin', 'andersen', 'berendsen', 'hoover', 'gst'),
                  'npt': ('langevin', 'berendsen', 'hoover', 'mtk'),
                  'nst': ('langevin', 'berendsen', 'hoover', 'mtk')}
    meansArgs = {('nve', None): 0,
                 ('nvt', 'evans'): 0, ('nvt', 'langevin'): 1, ('nvt', 'andersen'): 2,
                 ('nvt', 'berendsen'): 1, ('nvt', 'hoover'): (1,2), ('nvt', 'gst'): 2,
                 ('npt', 'langevin'): 2, ('npt', 'berendsen'): 2, ('npt', 'hoover'): 2, ('npt', 'mtk'): 2,
                 ('nst', 'langevin'): range(2, 6), ('nst', 'berendsen'): range(2, 6), ('nst', 'hoover'): range(2, 6), ('nst', 'mtk'): range(2, 6)}
    def __init__(self, *argsIn):
        args = list(argsIn)[:] # Make copy
        self._ensemble = args.pop(0)
        if self.ensemble != 'nve':
            self._means = args.pop(0)
        self.args = args

    @property
    def ensemble(self):
        return self._ensemble

    @ensemble.setter
    def ensemble(self, ensemble):
        ''' Set ensemble and check if valid '''
        if ensemble not in EnsembleParam.validMeans:
            raise ValueError('Cannot set ensemble to be {}. Valid ensembles {}.'.format(
                ensemble, ', '.join(EnsembleParam.validMeans.keys())))
        self._means = None
        self.args = []
        self._ensemble = ensemble

    @property
    def means(self):
        return self._means

    @means.setter
    def means(self, means):
        if means not in EnsembleParam.validMeans[self.ensemble]:
            raise ValueError('Cannot set means to be {}. Valid means {}.'.format(
                means, ', '.join(EnsembleParam.validMeans[self.ensemble])))
        self.args = []
        self._means = means

    def __str__(self):
        expect = EnsembleParam.meansArgs[(self.ensemble, self.means)]
        received = len(self.args)
        if ((isinstance(expect, (range, tuple)) and received not in expect) or
                (isinstance(expect, int) and received != expect)):
            raise IndexError('Wrong number of args in ensemble {} {}. Expected {}, received {}.'.format(
                self.ensemble, self.means, expect, received))

        return f'ensemble {self.ensemble} {self.means if self.means else ""} {" ".join(map(str, self.args)) if self.args else ""}'

class Control:
    ''' Class defining a DLPOLY control file '''
    params = {'binsize': float, 'cap': float, 'close': float,
              'collect': bool, 'coulomb': bool, 'cutoff': float,
              'densvar': float, 'distance': float,
              'dump': int, 'ensemble': tuple, 'epsilon': float,
              'equilibration': int, 'ewald': tuple, 'exclude': bool,
              'heat_flux': bool, 'integrator': str,
              'io': tuple, 'job': float, 'maxdis': float,
              'metal': bool, 'mindis': float, 'multiple': int, 'mxquat': int,
              'mxshak': int, 'mxstep': float,
              'ignore': tuple, 'pressure': float, 'print': int, 'print rdf': bool,
              'print zden': bool, 'quaternion': float,
              'rdf': int, 'regauss': int, 'replay': bool,
              'restart': str, 'rlxtol': float, 'rpad': float, 'rvdw': float,
              'scale': int, 'slab': bool,
              'stack': int, 'stats': int, 'steps': int, 'temperature': float,
              'title': str, 'timestep': float,
              'variable': float, 'vdw': str, 'zden': int, 'zero': bool,
              'defects': (int, int, float), 'displacements': (int, int, float),
              'impact': (int, int, float, float, float, float),
              'minimise': (str, int, float), 'msdtemp': (int, int),
              'nfold': (int, int, int), 'optimise': (str, float),
              'pseudo': (str, float, float), 'seed': (int, int),
              'trajectory': (int, int, int)}

    def __init__(self, filename=None):
        self.temperature = 300.0
        self.title = 'no title'
        self.io = IOParam()
        self.ignore = Ignore()
        self.ensemble = EnsembleParam('nve')
        self.pressure = 0.0
        self.collect = False
        self.steps = 10
        self.equilibration = 5
        self.print = 1
        self.stats = 1
        self.cutoff = 0.0
        self.variable = False
        self.timestep = 0.001
        if filename:
            self.read_control(filename)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, val):
        if key not in Control.params:
            raise KeyError('Param {} not valid param name in control file.'.format(key))

        targetType = Control.params[key]
        if not isinstance(targetType, tuple):
            try:
                val = targetType(val)
            except TypeError:
                raise ValueError(
                    'Type of {} ({}) not valid, must be castable to {}'.format(val, type(val).__name__,
                                                              Control.params[key].__name__))
        else:
            try:
                val = [targetType(item) for item, targetType in zip(val, Control.listTypes[key])]
            except TypeError:
                raise ValueError(
                    'Type of {} ({}) not valid, must be castable to {}'.format(val,
                        [type(x).__name__ for x in val],
                        [x.__name__ for x in  Control.listTypes[key]]))

        setattr(self, key, val)

    keywords = property(lambda self: [key for key in Control.params])

    def read_control(self, filename):
        ''' Read a control file '''
        with open(filename, 'r') as inFile:
            self['title'] = inFile.readline()
            for line in inFile:
                line = line.strip()
                if line == 'finish':
                    break
                if not line or line.startswith('#') or line.startswith('l_'):
                    continue
                key, *args = line.split()
                key = key.lower()
                if key == 'io':
                    setattr(self.io, args[0], args[1])
                elif key == 'no':
                    setattr(self.ignore, args[0], True)
                elif key == 'ensemble':
                    self.ensemble = EnsembleParam(*args)
                else:
                    if len(args) == 1:
                        args = args[0]
                    self[key] = args

    def write(self, filename='CONTROL'):
        ''' Write the control out to a file '''
        with open(filename, 'w') as outFile:
            print(self.title, file=outFile)
            for key, val in self.__dict__.items():
                if key in ('title'):
                    continue
                if isinstance(val, bool):
                    if val:
                        print(key, file=outFile)
                    continue
                elif isinstance(val, (IOParam, EnsembleParam, Ignore)):
                    print(val, file=outFile)
                else:
                    print(key, val, file=outFile)
            print('finish', file=outFile)

if __name__ == '__main__':
    cont = Control('CONTROL')
    print(cont.ensemble.args)
    print(cont.ensemble)
    cont.ensemble.ensemble = 'nvt'
    cont.ensemble.means = 'langevin'
    cont.ensemble.args = [0.5]
    cont.write('geoff')
