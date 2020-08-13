#!/usr/bin/env python3
'''
Module to handle DLPOLY control files
'''

import os.path
from .utility import DLPData, check_arg


class FField(DLPData):
    ''' Class defining properties relating to forcefields '''
    def __init__(self, *_):
        DLPData.__init__(self, {'rvdw': float, 'rcut': float, 'rpad': float,
                                'elec': bool, 'elecMethod': str, 'metal': bool, 'vdw': bool, 'ewaldVdw': bool,
                                'elecParams': tuple, 'vdwParams': dict, 'metalStyle': str,
                                'polarMethod': str, 'polarTHole': int})
        self.elec = False
        self.elecMethod = 'coul'
        self.elecParams = ('',)

        self.metal = False
        self.metalStyle = 'TAB'

        self.vdw = False
        self.vdwParams = {}

        self.rcut = 0.0
        self.rvdw = 0.0
        self.rpad = 0.0

        self.ewaldVdw = False

        self.polarMethod = ""
        self.polarTHole = 0

    keysHandled = property(lambda self: ('reaction', 'shift', 'distance', 'ewald', 'coulomb',
                                         'rpad', 'delr', 'padding', 'cutoff', 'rcut', 'cut', 'rvdw',
                                         'metal', 'vdw', 'polar', 'ewald_vdw'))

    def parse(self, key, vals):
        ''' Handle key-vals for FField types '''

        fullName = {'lore': 'lorentz-bethelot', 'fend': 'fender-halsey', 'hoge': 'hogervorst',
                    'halg': 'halgren', 'wald': 'waldman-hagler', 'tang': 'tang-tonnies', 'func': 'functional'}

        if check_arg(key, 'reaction', 'shift', 'distan', 'ewald', 'coul'):
            vals = [val for val in vals if val != "field"]
            self.elec = True
            self.elecMethod = key
            self.elecParams = vals
        elif check_arg(key, 'rpad', 'delr', 'padding'):
            self.rpad = vals
            if check_arg(key, 'delr'):
                self.rpad *= 4
        elif check_arg(key, 'cutoff', 'rcut', 'cut'):
            self.rcut = vals
        elif check_arg(key, 'rvdw'):
            self.rvdw = vals
        elif check_arg(key, 'metal'):
            self.metal = True
            self.metalStyle = vals
        elif check_arg(key, 'vdw'):
            self.vdw = True
            while vals:
                val = vals.pop(0)
                if check_arg(val, 'direct'):
                    self.vdwParams['direct'] = ''
                if check_arg(val, 'mix'):
                    self.vdwParams['mix'] = fullName[check_arg(vals.pop(0), *fullName.keys())]
                if check_arg(val, 'shift'):
                    self.vdwParams['shift'] = ''
        elif key == 'polar':
            while vals:
                val = vals.pop()
                if check_arg(val, 'scheme', 'type', 'dump', 'factor'):
                    continue
                if check_arg(val, 'charmm'):
                    self.polarMethod = 'charmm'
                elif check_arg(val, 'thole'):
                    self.polarTHole = val.pop()
        elif key == 'ewald_vdw':
            self.ewaldVdw = True

    def __str__(self):
        outStr = ''
        if self.elec:
            outStr += '{} {}\n'.format(self.elecMethod, ' '.join(self.elecParams))
        if self.vdw:
            outStr += 'vdw {}\n'.format('{} {}'.format(key, val) for key, val in self.vdwParams)
        if self.metal:
            outStr += 'metal {}\n'.format(' '.join(self.metalStyle))
        outStr += 'rcut {}\n'.format(self.rcut)
        outStr += 'rvdw {}\n'.format(self.rvdw)
        outStr += 'rpad {}\n'.format(self.rpad)
        return outStr


class Ignore(DLPData):
    ''' Class definining properties that can be ignored '''
    def __init__(self, *_):
        DLPData.__init__(self, {'elec': bool, 'ind': bool, 'str': bool,
                                'top': bool, 'vdw': bool, 'vafav': bool,
                                'vom': bool, 'link': bool, 'strict': bool})
        self.elec = False
        self.ind = False
        self.str = False
        self.top = False
        self.vdw = False
        self.vafav = False
        self.vom = False
        self.link = False
        self.strict = False

    keysHandled = property(lambda self: ('no',))

    def parse(self, _key, args):
        ''' Parse disable/ignores '''
        setattr(self, args[0], True)

    def __str__(self):
        outStr = ''
        for item in self.keys:
            if getattr(self, item):
                outStr += f'no {item}\n'
        return outStr


class Analysis(DLPData):
    ''' Class defining properties of analysis '''
    def __init__(self, *_):
        DLPData.__init__(self, {'all': (int, int, float),
                                'bon': (int, int, float),
                                'ang': (int, int),
                                'dih': (int, int),
                                'inv': (int, int)})
        self.all = (0, 0, 0)
        self.bon = (0, 0)
        self.ang = (0, 0)
        self.dih = (0, 0)
        self.inv = (0, 0)

    keysHandled = property(lambda self: ('ana',))

    def parse(self, args):
        ''' Parse analysis line '''
        setattr(self, check_arg(args[0], self.keys), args[1:])

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
    def __init__(self, *_):
        DLPData.__init__(self, {'rdf': bool, 'analysis': bool, 'analObj': Analysis, 'printevery': int,
                                'vaf': bool, 'zden': bool, 'rdfevery': int, 'vafevery': int,
                                'vafbin': int, 'statsevery': int, 'zdenevery': int})

        self.analysis = False
        self.analObj = Analysis()
        self.rdf = False
        self.vaf = False
        self.zden = False

        self.printevery = 0
        self.statsevery = 0
        self.rdfevery = 0
        self.vafevery = 0
        self.vafbin = 0
        self.zdenevery = 0

    keysHandled = property(lambda self: ('print', 'rdf', 'zden', 'stats', 'analyse', 'vaf'))

    def parse(self, key, args):
        ''' Parse a split print line and see what it actually says '''
        if check_arg(key, 'print'):
            if args[0].isdigit():
                self.printevery = args[0]
            else:
                setattr(self, args[0], True)
                if not hasattr(self, args[0]+'every'):
                    setattr(self, args[0]+'every', 1)
        elif check_arg(key, 'rdf', 'zden', 'stats'):
            setattr(self, check_arg(key, 'rdf', 'zden', 'stats')+'every', args[0])
        elif check_arg(key, 'ana'):
            self.analObj.parse(args)
        elif check_arg(key, 'vaf'):
            self.vafevery, self.vafbin = args

    def __str__(self):
        outStr = ''
        if self.printevery > 0:
            outStr += f'print every {self.printevery}\n'
        if self.statsevery > 0:
            outStr += f'stats {self.statsevery}\n'
        if self.analysis:
            outStr += 'print analysis\n'
            outStr += str(self.analObj)
        for item in ('rdf', 'vaf', 'zden'):
            toPrint, freq = getattr(self, item), getattr(self, item+'every')
            if toPrint and freq:
                outStr += f'print {item}\n'
                outStr += f'{item}  {freq}\n'
        if self.vaf and self.vafevery:
            outStr += 'print vaf\n'
            outStr += f'vaf {self.vafevery} {self.vafbin}'
        return outStr


class IOParam(DLPData):
    ''' Class defining io parameters '''
    def __init__(self, control='CONTROL', field='FIELD',
                 config='CONFIG', statis='STATIS',
                 output='OUTPUT', history='HISTORY',
                 historf='HISTORF', revive='REVIVE',
                 revcon='REVCON', revold='REVOLD',
                 rdf='RDFDAT', msd='MSDTMP',
                 tabvdw='TABLE', tabbnd='TABBND',
                 tabang='TABANG', tabdih='TABDIH',
                 tabinv='TABINV', tabeam='TABEAM'):

        DLPData.__init__(self, {'control': str, 'field': str,
                                'config': str, 'statis': str,
                                'output': str, 'history': str,
                                'historf': str, 'revive': str,
                                'revcon': str, 'revold': str,
                                'rdf': str, 'msd': str,
                                'tabvdw': str, 'tabbnd': str,
                                'tabang': str, 'tabdih': str,
                                'tabinv': str, 'tabeam': str})

        # Get control's path
        if control is not None:
            controlTruepath = os.path.dirname(os.path.abspath(control))
            # Make other paths relative to control (i.e. load them correctly)
            field, config, statis, output, history, historf, revive, revcon, revold, rdf, msd, \
                tabvdw, tabbnd, tabang, tabdih, tabinv, tabeam = \
                map(lambda path: os.path.abspath(os.path.join(controlTruepath, path)),
                    (field, config, statis, output, history, historf, revive, revcon, revold,
                     rdf, msd, tabvdw, tabbnd, tabang, tabdih, tabinv, tabeam))

        self.control = control
        self.field = field
        self.config = config
        self.statis = statis
        self.output = output
        self.history = ""
        self.historf = ""
        self.revive = revive
        self.revcon = revcon
        self.revold = ""
        self.rdf = ""
        self.msd = ""

        self.tabvdw = tabvdw if os.path.isfile(tabvdw) else ""
        self.tabbnd = tabbnd if os.path.isfile(tabbnd) else ""
        self.tabang = tabang if os.path.isfile(tabang) else ""
        self.tabdih = tabdih if os.path.isfile(tabdih) else ""
        self.tabinv = tabinv if os.path.isfile(tabinv) else ""
        self.tabeam = tabeam if os.path.isfile(tabeam) else ""

    keysHandled = property(lambda self: ('io',))

    def parse(self, _key, args):
        ''' Parse an IO line '''
        setattr(self, args[0], args[1])

    def __str__(self):
        out = (f'io field {self.field}\n'   # First IO is key
               f'io config {self.config}\n'
               f'io statis {self.statis}\n'
               f'io revive {self.revive}\n'
               f'io revcon {self.revcon}\n')

        if self.revold:
            out += f'io revold {self.revold}\n'
        if self.history:
            out += f'io history {self.history}\n'
        if self.historf:
            out += f'io historf {self.historf}\n'
        if self.msd:
            out += f'io msd {self.msd}\n'
        if self.rdf:
            out += f'io rdf {self.rdf}\n'
        if self.tabvdw:
            out += f'io tabvdw {self.tabvdw}\n'
        if self.tabbnd:
            out += f'io tabbnd {self.tabbnd}\n'
        if self.tabang:
            out += f'io tabang {self.tabang}\n'
        if self.tabdih:
            out += f'io tabdih {self.tabdih}\n'
        if self.tabinv:
            out += f'io tabinv {self.tabinv}\n'
        if self.tabeam:
            out += f'io tabeam {self.tabeam}\n'

        return out


class EnsembleParam:
    ''' Class containing ensemble data '''
    validMeans = {'nve': (None), 'pmf': (None),
                  'nvt': ('evans', 'langevin', 'andersen', 'berendsen',
                          'hoover', 'gst', 'ttm', 'dpd'),
                  'npt': ('langevin', 'berendsen', 'hoover', 'mtk'),
                  'nst': ('langevin', 'berendsen', 'hoover', 'mtk')}
    meansArgs = {('nve', None): 0, ('pmf', None): 0,
                 ('nvt', 'evans'): 0, ('nvt', 'langevin'): 1, ('nvt', 'andersen'): 2,
                 ('nvt', 'berendsen'): 1, ('nvt', 'berendsen'): 1,
                 ('nvt', 'hoover'): (1, 2), ('nvt', 'gst'): 2,
                 ('npt', 'langevin'): 2, ('npt', 'berendsen'): 2, ('npt', 'berendsen'): 2,
                 ('npt', 'hoover'): 2, ('npt', 'mtk'): 2,
                 ('nst', 'langevin'): range(2, 6), ('nst', 'berendsen'): range(2, 6),
                 ('nst', 'hoover'): range(2, 6), ('nst', 'mtk'): range(2, 6)}

    fullName = {'lang': 'langevin', 'ander': 'andersen', 'ber': 'berendsen',
                'hoover': 'hoover', 'inhomo': 'ttm'}

    keysHandled = property(lambda self: ('ensemble',))

    def __init__(self, *argsIn):
        if not argsIn:
            if self.ensemble == 'nve':
                argsIn = ('nve')
            if self.ensemble == 'pmf':
                argsIn = ('pmf')
        args = list(argsIn)[:]  # Make copy

        self._ensemble = args.pop(0)
        self._means = None
        if self.ensemble not in ['nve', 'pmf']:
            test = args.pop(0)
            for abbrev in self.fullName:
                if test.startswith(abbrev):
                    test = self.fullName[abbrev]
            self._means = test
        self.args = args

        for index, arg in enumerate(self.args):
            if check_arg(arg, 'semi'):
                self.semi = True
                self.args.pop(index)
            elif check_arg(arg, 'orth'):
                self.orth = True
                self.args.pop(index)
            elif check_arg(arg, 'tens'):
                self.tens = True
                self.args.pop(index)

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

        return '{} {} {}'.format(self.ensemble,
                                 self.means if self.means else '',
                                 ' '.join(map(str, self.args)) if self.args else '')


class TimingParam(DLPData):
    ''' Class defining io parameters '''
    def __init__(self, **kwargs):
        DLPData.__init__(self, {'close': int, 'steps': int, 'equil': int, 'timestep': float, 'variable': bool,
                                'maxdis': float, 'mindis': float, 'mxstep': float, 'job': int, 'collect': bool,
                                'dump': int})
        self.close = 0
        self.steps = 0
        self.equil = 0
        self.timestep = 0.0
        self.variable = False
        self.maxdis = 0.0
        self.mindis = 0.0
        self.mxstep = 0.0
        self.job = 0
        self.collect = False
        self.dump = 0

        for key, val in kwargs.items():
            self.parse(key, val)

    keysHandled = property(lambda self: ('close', 'steps', 'equil', 'timestep', 'variable',
                                         'maxdis', 'mindis', 'mxstep', 'job', 'collect', 'dump'))

    def parse(self, key, args):
        ''' Parse a split timing line and see what it actually says '''

        if check_arg(key, 'close', 'steps', 'equil', 'maxdis', 'mindis', 'mxstep', 'job', 'collect', 'dump'):
            setattr(self, key, args)
        if check_arg(key, 'timestep', 'variable'):
            if isinstance(args, (list, tuple)):
                word1 = args.pop()
            elif args:
                word1 = args
            else:
                word1 = ''

            if ((key == 'timestep' and word1 == 'variable') or
                    (key == 'variable' and word1 == 'timestep')):
                self.variable = True
                self.timestep = args
            elif key == 'variable':
                self.variable = args
            else:
                self.timestep = word1

    def __str__(self):
        outStr = ''
        return outStr


class Control(DLPData):
    ''' Class defining a DLPOLY control file '''
    def __init__(self, source=None):
        DLPData.__init__(self, {'l_scr': bool, 'l_print': int, 'l_eng': bool, 'r_rout': bool,
                                'l_rin': bool, 'l_tor': bool, 'l_dis': int, 'unit_test': bool,
                                'l_vdw': bool, 'ana': Analysis, 'app_test': bool, 'currents': bool,
                                'binsize': float, 'cap': float,
                                'densvar': float, 'eps': float, 'exclu': bool,
                                'heat_flux': bool, 'rdf': int, 'coord': (int, int, int), 'adf': (int, float),
                                'zden': int, 'vaf': bool, 'mult': int, 'mxshak': int, 'pres': (float, ...),
                                'regaus': int, 'replay': str, 'restart': str, 'quaternion': float,
                                'rlxtol': float, 'scale': int, 'slab': bool, 'shake': float,
                                'stack': int, 'temp': float, 'yml_statis': bool, 'yml_rdf': bool,
                                'title': str, 'zero': int, 'timing': TimingParam,
                                'print': Print, 'ffield': FField, 'ensemble': EnsembleParam,
                                'ignore': Ignore, 'io': IOParam, 'subcell': float,
                                'impact': (int, int, float, float, float, float),
                                'minim': (str, int, float), 'msdtmp': (int, int),
                                'nfold': (int, int, int), 'optim': (str, float),
                                'pseudo': (str, float, float), 'seed': (int, ...),
                                'time_depth': int, 'time_per_mpi': bool, 'dftb_driver': bool,
                                'disp': (int, int, float), 'traj': (int, int, int),
                                'defe': (int, int, float, str)})
        self.temp = 300.0
        self.title = 'no title'
        self.l_scr = False
        self.l_tor = False
        self.io = IOParam(control=source)
        self.ignore = Ignore()
        self.print = Print()
        self.ffield = FField()
        self.ensemble = EnsembleParam('nve')
        self.ana = Analysis()
        self.timing = TimingParam(collect=False,
                                  steps=0,
                                  equil=0,
                                  variable=False,
                                  timestep=0.001)

        if source is not None:
            self.source = source
            self.read(source)

    @property
    def _handlers(self):
        ''' Return iterable of handlers '''
        return (self.io, self.ignore, self.print, self.ffield, self.timing, self.ana)

    @staticmethod
    def _strip_crap(args):
        return [arg for arg in args if not check_arg(arg, 'constant', 'every', 'sampl', 'tol',
                                                     'temp', 'cutoff', 'tensor', 'collect',
                                                     'steps', 'forces', 'sum', 'time')]

    def read(self, filename):
        ''' Read a control file '''
        with open(filename, 'r') as inFile:
            self['title'] = inFile.readline()
            for line in inFile:
                line = line.strip()
                if line == 'finish':
                    break
                if not line or line.startswith('#'):
                    continue
                key, *args = line.split()
                args = self._strip_crap(args)
                if not args:
                    args = ""
                key = key.lower()

                for handler in self._handlers:
                    keyhand = check_arg(key, *handler.keysHandled)
                    if keyhand:
                        handler.parse(keyhand, args)
                        break
                else:
                    if check_arg(key, 'ensemble'):
                        self.ensemble = EnsembleParam(*args)
                    else:
                        # Handle partial matching
                        self[check_arg(key, *self.keys)] = args

        return self

    def write(self, filename='CONTROL'):
        ''' Write the control out to a file '''

        def output(*args):
            print(file=outFile, *args)

        with open(filename, 'w') as outFile:
            output(self.title)
            for key, val in self.__dict__.items():
                if key in ('title', 'filename') or key.startswith('_'):
                    continue
                if key == 'timing':
                    for keyt, valt in self.timing.__dict__.items():
                        if keyt in ('job', 'close'):
                            output(f'{keyt} time {valt}')
                        elif keyt == 'timestep':
                            if self.timing.variable:
                                print('variable', keyt, valt, file=outFile)
                            else:
                                print(keyt, valt, file=outFile)
                        elif keyt == 'variable':
                            continue
                        elif keyt in ('dump', 'mindis', 'maxdix', 'mxstep') and valt > 0:
                            output(keyt, valt)
                        elif keyt == 'collect' and valt:
                            output(keyt)
                        elif keyt in ('steps', 'equil'):
                            output(keyt, valt)
                elif isinstance(val, bool):
                    if val and (key != 'variable'):
                        output(key)
                    continue
                elif val in self._handlers:
                    output(val)
                elif isinstance(val, (tuple, list)):
                    output(key, ' '.join(map(str, val)))
                else:
                    output(key, val)
            output('finish')

    def write_new(self, filename='CONTROL'):
        ''' Write control in new style '''

        def output(key, *vals):
            print(key, *(f' {val}' for val in vals), file=outFile)

        with open(filename, 'w') as outFile:
            output('title', self.title)
            for key, val in self.__dict__.items():
                if key in ('title', 'filename') or key.startswith('_'):
                    continue

                if key == 'l_scr':
                    output('io_file_output', 'SCREEN')
                elif key == 'l_print':
                    output('print_level', val)
                elif key == 'l_eng':
                    output('output_energy', 'ON')
                elif key == 'l_rout':
                    output('io_write_ascii_revive', 'ON')
                elif key == 'l_rin':
                    output('io_read_ascii_revold', 'ON')
                elif key == 'l_dis':
                    output('initial_minimum_separation', val, 'ang')
                elif key == 'l_tor':
                    output('io_file_revcon', 'NONE')
                    output('io_file_revive', 'NONE')
                elif key == 'unit_test':
                    output('unit_test', 'ON')
                elif key == 'binsize':
                    output('rdf_binsize', val)
                    output('zden_binsize', val)
                elif key == 'cap':
                    output('equilibration_force_cap', val, 'kT/angs')
                elif key == 'densvar':
                    output('density_variance', val, '%')
                elif key == 'eps':
                    output('coul_dielectric_constant', val)
                elif key == 'equil':
                    output('time_equilibration', val, 'steps')
                elif key == 'exclu':
                    output('coul_extended_exclusion', 'ON')
                elif key == 'heat_flux':
                    output('heat_flux', 'ON')
                elif key == 'mxshak':
                    output('shake_max_iter', val)
                elif key == 'pres':
                    if isinstance(val, (tuple, list)):
                        output('pressure_tensor', *val, 'katm')
                    else:
                        output('pressure_hydrostatic', val, 'katm')

                elif key == 'regauss':
                    output('regauss_frequency', val, 'steps')
                elif key == 'restart':
                    output('restart', val)
                elif key == 'rlxtol':
                    output('rlx_tol', val[0])
                    output('rlx_cgm_step', val[1])
                elif key == 'scale':
                    output('rescale_frequency', val)
                elif key == 'shake':
                    output('shake_tolerance', val, 'ang')
                elif key == 'quaternion':
                    output('quaternion_tolerance', val, 'ang')
                elif key == 'stack':
                    output('stack_size', val, 'steps')
                elif key == 'temp':
                    output('temperature', val, 'K')
                elif key == 'zero':
                    output('reset_temperature_interval', val, 'steps')
                elif key == 'print':
                    # DLPData.__init__(self, {'rdf': bool, 'printevery': int,
                    #                         'vaf': bool, 'zden': bool, 'rdfevery': int, 'vafevery': int,
                    #                         'vafbin': int, 'statsevery': int, 'zdenevery': int})

                    output('print_frequency', val.printevery, 'steps')
                    output('stats_frequency', val.statsevery, 'steps')

                    if val.rdf:
                        output('rdf_calculate', 'ON')
                        output('rdf_print', 'ON')
                        output('rdf_frequency', val.rdfevery, 'steps')

                    if val.vaf:
                        output('vaf_calculate', 'ON')
                        output('vaf_print', 'ON')
                        output('vaf_frequency', val.vafevery, 'steps')
                        output('vaf_binsize', val.vafbin, 'steps')

                    if val.zden:
                        output('zden_calculate', 'ON')
                        output('zden_print', 'ON')
                        output('zden_frequency', val.zdenevery, 'steps')

                elif key == 'ffield':
                    # if key in ('reaction', 'shift', 'distan', 'ewald', 'coulomb'):
                    #     vals = [val for val in vals if val != "field"]
                    #     self.elec = True
                    #     self.elecMethod = key
                    #     self.elecParams = vals

                    if val.vdw and not self.ignore.vdw:
                        if 'direct' in val.vdwParams:
                            output('vdw_method', 'direct')
                        if 'mix' in val.vdwParams:
                            output('vdw_mix_method', val.vdwParams['mix'])
                        if 'shift' in val.vdwParams:
                            output('vdw_force_shift', 'ON')
                        if val.rvdw:
                            output('vdw_cutoff', val.rvdw, 'ang')

                    if val.rpad:
                        output('padding', val.rpad, 'ang')
                    if val.rcut:
                        output('cutoff', val.rcut, 'ang')

                    if val.elec:
                        output('coul_method', val.elecMethod)
                    if val.metalStyle == 'sqrtrho':
                        output('metal_sqrtrho', 'ON')
                    elif val.metalStyle == 'direct':
                        output('metal_direct', 'ON')

                elif key == 'ensemble':
                    output('ensemble', val.ensemble)
                    output('ensemble_method', val.means)

                    if val.ensemble == 'nvt':
                        if val.means == 'langevin':
                            output('ensemble_thermostat_friction', val.args[0], 'ps^-1')
                        elif val.means == 'andersen':
                            output('ensemble_thermostat_coupling', val.args[0], 'ps')
                            output('ensemble_thermostat_softness', val.args[1])
                        elif val.means in ('berendsen', 'hoover'):
                            output('ensemble_thermostat_coupling', val.args[0], 'ps')

                elif key == 'ignore':

                    # DLPData.__init__(self, {'elec': bool, 'ind': bool, 'str': bool,
                    #                         'top': bool, 'vdw': bool, 'vafav': bool,
                    #                         'vom': bool, 'link': bool})
                    if val.elec:
                        output('coul_method', 'OFF')
                    if val.ind:
                        output('ignore_config_indices', 'ON')
                    if val.str:
                        output('strict_checks', 'OFF')
                    if val.top:
                        output('print_topology_info', 'OFF')
                    if val.vdw:
                        output('vdw_method', 'OFF')
                    if val.vafav:
                        output('vaf_averaging', 'OFF')
                    if val.vom:
                        output('fixed_com', 'OFF')
                    if val.link:
                        continue

                elif key == 'io':
                    if not val.output.endswith('OUTPUT') and not self.l_scr:
                        output('io_file_output', val.output)
                    if not val.field.endswith('FIELD'):
                        output('io_file_field', val.field)
                    if not val.field.endswith('CONFIG'):
                        output('io_file_config', val.config)
                    if not val.statis.endswith('STATIS'):
                        output('io_file_statis', val.statis)
                    if not val.history.endswith('HISTORY'):
                        output('io_file_history', val.history)
                    if not val.historf.endswith('HISTORF'):
                        output('io_file_historf', val.historf)
                    if not val.revive.endswith('REVIVE'):
                        output('io_file_revive', val.revive)
                    if not val.revcon.endswith('REVCON') and not self.l_tor:
                        output('io_file_revcon', val.revcon)
                    if not val.revold.endswith('REVOLD') and not self.l_tor:
                        output('io_file_revold', val.revold)

                elif key == 'defe':
                    if val:
                        output('defects_calculate', 'ON')
                        output('defects_start', val[0], 'steps')
                        output('defects_interval', val[1], 'steps')
                        output('defects_distance', val[2], 'ang')
                        if len(val) > 3:
                            output('defects_backup', 'ON')

                elif key == 'disp':
                    if val:
                        output('displacements_calculate', 'ON')
                        output('displacements_start', val[0], 'steps')
                        output('displacements_interval', val[1], 'steps')
                        output('displacements_distance', val[2], 'ang')

                elif key == 'impact':
                    if val:
                        output('impact_part_index', val[0])
                        output('impact_time', val[1], 'steps')
                        output('impact_energy', val[2], 'ke.V')
                        output('impact_direction', *val[3:], 'ang/ps')

                elif key == 'minim':
                    if val:
                        output('minimisation_criterion', val[0])
                        output('minimisation_tolerance', val[1], 'ang')
                        output('minimisation_step_length', val[2], 'ang')
                        output('minimisation_frequency', val[3], 'steps')

                elif key == 'optim':
                    if val:
                        output('minimisation_criterion', val[0])
                        output('minimisation_tolerance', val[1], 'ang')
                        output('minimisation_step_length', val[2], 'ang')
                        output('minimisation_frequency', val[3], 'steps')

                elif key == 'msdtmp':
                    if val:
                        output('msd_calculate', 'ON')
                        output('msd_start', val[0])
                        output('msd_frequence', val[1])

                elif key == 'nfold':
                    continue

                elif key == 'pseudo':
                    if val:
                        output('pseudo_thermostat_method', 'ON')
                        output('pseudo_thermostat_width', val[0], 'ang')
                        output('pseudo_thermostat_temperature', val[1], 'K')

                elif key == 'seed':
                    output('random_seed', *val)
                elif key == 'traj':
                    if val:
                        output('traj_calculate', 'ON')
                        output('traj_start', val[0], 'steps')
                        output('traj_interval', val[1], 'steps')
                        output('traj_key', val[2])

                elif key == 'timing':

                    if val.dump:
                        output('dump_frequency', val.dump, 'steps')
                    if val.steps:
                        output('time_run', val.steps, 'steps')
                    output('time_job', val.job, 's')
                    output('time_close', val.close, 's')
                    if val.collect:
                        output('record_equilibration', 'ON')

                    if val.variable:
                        output('timestep_variable', 'ON')
                        if val.mindis:
                            output('timestep_variable_min_dist', val.mindis, 'ang')
                        if val.maxdis:
                            output('timestep_variable_max_dist', val.maxdis, 'ang')
                        if val.mxstep:
                            output('timestep_variable_max_delta', val.mxstep, 'ps')

                    output('timestep', val.timestep, 'ps')


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        CONT = Control(sys.argv[1])
    else:
        CONT = Control('CONTROL')

    if len(sys.argv) > 2:
        CONT.write(sys.argv[2])
    else:
        CONT.write('new_control')
