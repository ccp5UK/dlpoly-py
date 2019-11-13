#!/usr/bin/env python3
"""
Module to handle DLPOLY control files
"""

class IOParam:
    """ Class defining io parameters """
    def __init__(self):
        self.field = "FIELD"
        self.config = "CONFIG"
        self.outstats = "STATIS"

    def __str__(self):
        return (f'field {self.field}\n' # First IO is key
                f'io config {self.config}\n'
                f'io outstats {self.outstats}')

class EnsembleParam:
    """ Class containing ensemble data """
    means = {"nve": (None),
             "nvt": ("evans", "langevin", "andersen", "berendsen", "hoover", "gst"),
             "npt": ("langevin", "berendsen", "hoover", "mtk"),
             "nst": ("langevin", "berendsen", "hoover", "mtk",
                     "area", "tens", "tenssemi", "ortho", "orthosemi")}
    def __init__(self, *argsIn):
        args = list(argsIn)[:] # Make copy
        print(args)
        self._ensemble = args.pop(0)
        self._means, self.args = self.args_setter(args)

    @property
    def ensemble(self):
        return self._ensemble

    @ensemble.setter
    def ensemble(self, ensemble):
        """ Set ensemble and check if valid """
        if ensemble not in EnsembleParam.means:
            raise ValueError('Cannot set ensemble to be {}. Valid ensembles {}.'.format(
                ensemble, ", ".join(EnsembleParam.means.keys())))
        self._ensemble = ensemble

    @property
    def means(self):
        return self._means

    @means.setter
    def means(self, means):
        if means not in EnsembleParam.means[self.ensemble]:
            raise ValueError('Cannot set means to be {}. Valid means {}.'.format(
                means, ", ".join(EnsembleParam.means[self.ensemble])))
        self._means = means

    def args_setter(self, args):

        if self.ensemble == "nve":
            return None, []
        if not args:
            raise ValueError('No arguments provided')
        means = None
        if "tens" in args:
            means = args.pop(args.index("tens"))
        if "area" in args:
            means = args.pop(args.index("area"))
        if "orth" in args:
            means = args.pop(args.index("orth"))
        if "semi" in args:
            means += args.pop(args.index("semi"))
        if means is None:
            means = args.pop(0)
        return means, args

    def __str__(self):
        outStr = str(self.ensemble)
        return f'{self.ensemble} {self.means if self.means else ""} {" ".join(self.args) if self.args else ""}'

class Control:
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

    def __init__(self, filename=None):
        self.temperature = 300.0
        self.finish = True
        self.title = 'no title'
        self.io = IOParam()
        self.ensemble = EnsembleParam("nve")
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
            self.read_config(filename)

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
        """ Write the control out to a file """
        with open(filename, 'w') as outFile:
            for key, val in self.__dict__.items():
                print(key, val)

if __name__ == '__main__':
    cont = Control()
    cont.write("geoff")
