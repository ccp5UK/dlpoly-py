#!/usr/bin/env python3
'''
Module to handle DLPOLY control files
'''

from dlpoly.utility import DLPData


class FField(DLPData):
    ''' Class defining properties relating to forcefields '''
    def __init__(self, *args):
        DLPData.__init__(self, {'rvdw': float, 'rcut': float, 'rpad': float,
                                'elec': bool, 'elecMethod': str, 'metal': bool, 'vdw': bool, 'elecParams': tuple,
                                'vdwParams': tuple, 'metalStyle': str, 'keysHandled': tuple})
        self.elec = False
        self.elecMethod = 'coulomb'
        self.elecParams = ('',)

        self.metal = False
        self.metalStyle = 'TAB'

        self.vdw = False
        self.vdwParams = ('TAB')

        self.rcut = 0.0
        self.rvdw = 0.0
        self.rpad = 0.0

    keysHandled = property(lambda self: ('reaction', 'shift', 'distance', 'ewald', 'coulomb',
                                         'rpad', 'delr', 'padding', 'cutoff', 'rcut', 'cut', 'rvdw',
                                         'metal', 'vdw'))

    def parse(self, key, vals):
        ''' Handle key-vals for FField types '''
        if key in ('reaction', 'shift', 'distance', 'ewald', 'coulomb'):
            self.elec = True
            self.elecMethod = key
            self.elecParams = vals
        elif key in ('rpad', 'delr', 'padding'):
            self.rpad = vals
            if key == 'delr':
                self.rpad *= 4
        elif key in ('cutoff', 'rcut', 'cut'):
            self.rcut = vals
        elif key == 'rvdw':
            self.rvdw = vals
        elif key == 'metal':
            self.metal = True
            self.metalStyle = vals
        elif key == 'vdw':
            self.vdw = True
            self.vdwParams = vals

    def __str__(self):
        outStr = ''
        if self.elec:
            outStr += '{} {}\n'.format(self.elecMethod, ' '.join(self.elecParams))
        if self.vdw:
            outStr += 'vdw {}\n'.format(' '.join(self.vdwParams))
        if self.metal:
            outStr += 'metal {}\n'.format(' '.join(self.metalStyle))
        outStr += 'rcut {}\nrvdw {}\nrpad {}\n'.format(self.rcut, self.rvdw, self.rpad)
        return outStr


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

    keysHandled = property(lambda self: ('no',))

    def parse(self, key, args):
        setattr(self, args[0], True)

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
        # if any(self.all > 0):
        #     return 'analyse all every {} nbins {} rmax {}'.format(*self.all)

        outstr = ''
        # for analtype in ('bonds', 'angles', 'dihedrals', 'inversions'):
        #     args = getattr(self, analtype)
        #     if any(args > 0):
        #         outstr += ('analyse {} every {} nbins {} rmax {}\n'.format(analtype, *args) if len(args) > 2 else
        #                    'analyse {} every {} nbind {}\n'.format(analtype, *args))
        return outstr


class Print(DLPData):
    ''' Class definining properties that can be printed '''
    def __init__(self, *args):
        DLPData.__init__(self, {'rdf': bool, 'analysis': bool, 'analObj': Analysis, 'printevery': int,
                                'vaf': bool, 'zden': bool, 'rdfevery': int, 'vafevery': int,
                                'vafbin': int, 'statsevery': int, 'zdenevery': int, 'keysHandled': tuple})

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

    keysHandled = property(lambda self: ('print', 'rdf', 'zden', 'stats', 'analyse', 'vaf'))

    def parse(self, key, args):
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
            outStr += 'print {}\n'.format(self.printevery)
        if self.analysis:
            outStr += 'print analysis\n'
            outStr += str(self.analObj)
        for item in ('rdf', 'vaf', 'zden'):
            toPrint, freq = getattr(self, item), getattr(self, item+'every')
            if toPrint and freq:
                outStr += 'print {}\n'.format(item)
                outStr += '{}  {}\n'.format(item, freq)
        if self.vaf and self.vafevery:
            outStr += 'print vaf\n'
            outStr += 'vaf {} {}'.format(self.vafevery, self.vafbin)
        return outStr


class IOParam(DLPData):
    ''' Class defining io parameters '''
    def __init__(self, control='CONTROL', field='FIELD',
                 config='CONFIG', statis='STATIS',
                 output='OUTPUT', history='HISTORY',
                 historf='HISTORF', revive='REVIVE',
                 revcon='REVCON', revold='REVOLD'):
        DLPData.__init__(self, {'control': str, 'field': str,
                                'config': str, 'outstat': str,
                                'output': str, 'history': str,
                                'historf': str, 'revive': str,
                                'revcon': str, 'revold': str})

        self.control = control
        self.field = field
        self.config = config
        self.outstat = statis
        self.output = output
        self.history = history
        self.historf = historf
        self.revive = revive
        self.revcon = revcon
        self.revold = revold

    keysHandled = property(lambda self: ('io',))

    def parse(self, _, args):
        ''' Parse an IO line '''
        setattr(self, args[0], args[1])

    def __str__(self):
        return (f'io field {self.field}\n'   # First IO is key
                f'io config {self.config}\n'
                f'io statis {self.outstat}\n'
                f'io output {self.output}\n'
                f'io history {self.history}\n'
                f'io historf {self.historf}\n'
                f'io revive {self.revive}\n'
                f'io revcon {self.revcon}\n'
                f'io revold {self.revold}\n')


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

    keysHandled = property(lambda self: ('ensemble',))

    def __init__(self, *argsIn):
        if not argsIn:
            argsIn = ('nve')
        args = list(argsIn)[:]  # Make copy

        self._ensemble = args.pop(0)
        self._means = None
        if self.ensemble != 'nve':
            self._means = args.pop(0)
        self.args = args

    @property
    def ensemble(self):
        ''' The thermodynamic ensemble '''
        return self._ensemble

    def parse(self, _, args):
        self = EnsembleParam(*args)

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

        return '{} {} {}'.format(self.ensemble,
                                 self.means if self.means else '',
                                 ' '.join(map(str, self.args)) if self.args else '')


class Control(DLPData):
    ''' Class defining a DLPOLY control file '''
    def __init__(self, source=None):
        DLPData.__init__(self, {'binsize': float, 'cap': float, 'close': int, 'collect': bool, 'densvar': float,
                                'dump': int, 'epsilon': float, 'equilibration': int, 'exclude': bool,
                                'heat_flux': bool, 'integrator': str, 'job': int, 'maxdis': float,
                                'metal': bool, 'mindis': float, 'multiple': int, 'mxquat': int,
                                'mxshak': int, 'mxstep': float, 'pressure': float, 'press': float,
                                'quaternion': float, 'regauss': int, 'replay': bool, 'restart': str,
                                'rlxtol': float, 'scale': int, 'slab': bool, 'shake': float,
                                'stack': int, 'stats': int, 'steps': int, 'temperature': float,
                                'title': str, 'timestep': float, 'variable': bool, 'zero': bool,
                                'print': Print, 'ffield': FField, 'ensemble': EnsembleParam, 'ignore': Ignore,
                                'io': IOParam,
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
        self.ffield = FField()
        self.ensemble = EnsembleParam('nve')
        self.collect = False
        self.stats = 1
        self.steps = 10
        self.equilibration = 5
        self.variable = False
        self.timestep = 0.001
        if source is not None:
            self.source = source
            self.read(source)

    @property
    def handlers(self):
        ''' Return iterable of handlers '''
        return (self.io, self.ignore, self.print, self.ffield)

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
                for handler in self.handlers:
                    if key in handler.keysHandled:
                        handler.parse(key, args)
                        break
                else:
                    if key == 'ensemble':
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
                if key in ('job', 'close'):
                    print('{} time {}'.format(key, val), file=outFile)
                elif isinstance(val, bool):
                    if val and (key != 'variable'):
                        print(key, file=outFile)
                    continue
                elif val in self.handlers:
                    print(val, file=outFile)
                elif isinstance(val, (tuple, list)):
                    print(key, ' '.join(val), file=outFile)
                else:
                    if key == 'timestep' and self.variable:
                        print('variable', key, val, file=outFile)
                    else:
                        print(key, val, file=outFile)
            print('finish', file=outFile)


if __name__ == '__main__':
    CONT = Control('CONTROL')
    CONT.write('geoff')
