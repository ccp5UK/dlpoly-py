#!/usr/bin/env python3
'''
Module to handle DLPOLY control files
'''

from dlpoly.utility import DLPData


class Ignore(DLPData):
    ''' Class definining properties that can be ignored '''
    def __init__(self, *args):
        DLPData.__init__(self, {'elec': bool, 'index': bool, 'strict': bool,
                                'topology': bool, 'vdw': bool, 'vafaveraging': bool})
        self.elec = False
        self.index = False
        self.strict = False
        self.topology = False
        self.vdw = False
        self.vafaveraging = False

    def __str__(self):
        outStr = ''
        for item in self.keys:
            if getattr(self, item):
                outStr += f'no {item}\n'
        return outStr


class Analysis(DLPData):
    ''' Class defining properties of analysis '''
    def __init__(self, *args):
        DLPData.__init__(self, {'all': (int, int, float),
                                'bonds': (int, int, float),
                                'angles': (int, int),
                                'dihedrals': (int, int),
                                'inversions': (int, int)})
        self.all = (0, 0, 0)
        self.bonds = (0, 0)
        self.angles = (0, 0)
        self.dihedrals = (0, 0)
        self.inversions = (0, 0)

    def parse(self, args):
        setattr(self, args[0], args[1:])

    def __str__(self):
        if any(self.all > 0):
            return 'analyse all every {} nbins {} rmax {}'.format(*self.all)

        outstr = ''
        for analtype in ('bonds', 'angles', 'dihedrals', 'inversions'):
            args = getattr(self, analtype)
            if any(args > 0):
                outstr += ('analyse {} every {} nbins {} rmax {}\n'.format(analtype, *args) if len(args) > 2 else
                           'analyse {} every {} nbind {}\n'.format(analtype, *args))
        return outstr


class Print(DLPData):
    ''' Class definining properties that can be printed '''
    def __init__(self, *args):
        DLPData.__init__(self, {'rdf': bool, 'analysis': bool, 'analObj': Analysis, 'printevery': int,
                                'vaf': bool, 'zden': bool, 'rdfevery': int, 'vafevery': int,
                                'vafbin': int, 'zdenevery': int})
        self.analysis = False
        self.analObj = Analysis()
        self.rdf = False
        self.vaf = False
        self.zden = False

        self.printevery = 0
        self.rdfevery = 0
        self.vafevery = 0
        self.vafbin = 0
        self.zdenevery = 0

    def parse_print(self, key, args):
        ''' Parse a split print line and see what it actually says '''
        if key == 'print':
            if args[0].isdigit():
                self.printevery = args[0]
            else:
                setattr(self, args[0], True)
                setattr(self, args[0]+'every', 1)
        elif key in ('rdf', 'zden', 'stats'):
            setattr(self, key+'every', args[0])
        elif key == 'analyse':
            self.analObj.parse(args)
        elif key == 'vaf':
            self.vafevery, self.vafbin = args

    def __str__(self):
        outStr = ''
        if self.printevery > 0:
            outStr += 'every {}\n'.format(self.printevery)
        if self.analysis:
            outStr += 'print analysis\n'
            outStr += str(self.analObj)
        for item in ('rdf', 'vaf', 'zden'):
            toPrint, freq = getattr(self, item), getattr(self, item+'every')
            if toPrint and freq:
                outStr += 'print {}\n'.format(item)
                outStr += '{} every {}\n'.format(item, freq)
        if self.vaf and self.vafevery:
            outStr += 'print vaf\n'
            outStr += 'vaf every {} {}'.format(self.vafevery, self.vafbin)
        return outStr


class IOParam(DLPData):
    ''' Class defining io parameters '''
    def __init__(self, control='CONTROL', field='FIELD',
                 config='CONFIG', outstats='STATIS', *args):
        DLPData.__init__(self, {'control': str, 'field': str,
                                'config': str, 'outstats': str})
        self.control = control
        self.field = field
        self.config = config
        self.outstats = outstats

    def __str__(self):
        return (f'io field {self.field}\n'   # First IO is key
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
                 ('nvt', 'berendsen'): 1, ('nvt', 'ber'): 1,
                 ('nvt', 'hoover'): (1, 2), ('nvt', 'gst'): 2,
                 ('npt', 'langevin'): 2, ('npt', 'berendsen'): 2, ('npt', 'ber'): 2,
                 ('npt', 'hoover'): 2, ('npt', 'mtk'): 2,
                 ('nst', 'langevin'): range(2, 6), ('nst', 'berendsen'): range(2, 6),
                 ('nst', 'hoover'): range(2, 6), ('nst', 'mtk'): range(2, 6)}

    def __init__(self, *argsIn):
        if not argsIn:
            argsIn = ('nve')
        args = list(argsIn)[:]  # Make copy

        self._ensemble = args.pop(0)
        if self.ensemble != 'nve':
            self._means = args.pop(0)
        self.args = args

    @property
    def ensemble(self):
        ''' The thermodynamic ensemble '''
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
        ''' The integrator used to maintain the ensemble '''
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

        return 'ensemble {} {} {}'.format(self.ensemble,
                                          self.means if self.means else '',
                                          ' '.join(map(str, self.args)) if self.args else '')


class Control(DLPData):
    ''' Class defining a DLPOLY control file '''
    def __init__(self, source=None):
        DLPData.__init__(self, {'binsize': float, 'cap': float, 'close': int,
                                'collect': bool, 'coulomb': bool, 'cutoff': float,
                                'densvar': float, 'distance': float,
                                'dump': int, 'ensemble': EnsembleParam, 'epsilon': float,
                                'equilibration': int, 'ewald': tuple, 'exclude': bool,
                                'heat_flux': bool, 'integrator': str,
                                'io': IOParam, 'job': int, 'maxdis': float,
                                'metal': bool, 'mindis': float, 'multiple': int, 'mxquat': int,
                                'mxshak': int, 'mxstep': float, 'cut': float,
                                'ignore': Ignore, 'pressure': float,
                                'press': float, 'print': Print, 'print rdf': bool,
                                'print zden': bool, 'quaternion': float,
                                'rdf': int, 'regauss': int, 'replay': bool,
                                'restart': str, 'rlxtol': float, 'rpad': float, 'rvdw': float,
                                'scale': int, 'slab': bool, 'shake': float,
                                'stack': int, 'stats': int, 'steps': int, 'temperature': float,
                                'title': str, 'timestep': float,
                                'variable': bool, 'vdw': str, 'zden': int, 'zero': bool,
                                'defects': (int, int, float), 'displacements': (int, int, float),
                                'impact': (int, int, float, float, float, float),
                                'minimise': (str, int, float), 'msdtemp': (int, int),
                                'nfold': (int, int, int), 'optimise': (str, float),
                                'pseudo': (str, float, float), 'seed': (int, int),
                                'trajectory': (int, int, int)})
        self.temperature = 300.0
        self.title = 'no title'
        self.io = IOParam(control=source)
        self.ignore = Ignore()
        self.print = Print()
        self.ensemble = EnsembleParam('nve')
        self.pressure = 0.0
        self.collect = False
        self.stats = 1
        self.steps = 10
        self.equilibration = 5
        self.cutoff = 0.0
        self.variable = False
        self.timestep = 0.001
        if source is not None:
            self.source = source
            self.read(source)

    @staticmethod
    def _strip_crap(args):
        return [arg for arg in args if arg not in ('constant', 'every', 'sampling', 'tolerance',
                                                   'timestep', 'temperature', 'cutoff', 'history',
                                                   'field', 'steps', 'forces', 'sum', 'time')]

    def read(self, filename):
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
                args = self._strip_crap(args)
                key = key.lower()
                if key == 'io':
                    setattr(self.io, args[0], args[1])
                elif key == 'no':
                    setattr(self.ignore, args[0], True)
                elif key in ('analyse', 'print', 'rdf', 'vaf', 'zden'):
                    self.print.parse_print(key, args)
                elif key == 'ensemble':
                    self.ensemble = EnsembleParam(*args)
                else:
                    self[key] = args
        return self

    def write(self, filename='CONTROL'):
        ''' Write the control out to a file '''
        with open(filename, 'w') as outFile:
            print(self.title, file=outFile)
            for key, val in self.__dict__.items():
                if key in ('title', 'filename') or key.startswith('_'):
                    continue
                if isinstance(val, bool):
                    if val:
                        print(key, file=outFile)
                    continue
                elif isinstance(val, (IOParam, EnsembleParam, Ignore)):
                    print(val, file=outFile)
                elif isinstance(val, (tuple, list)):
                    print(key, ' '.join(val), file=outFile)
                else:
                    print(key, val, file=outFile)
            print('finish', file=outFile)


if __name__ == '__main__':
    CONT = Control('CONTROL')
    CONT.write('geoff')
