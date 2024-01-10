#!/usr/bin/env python3
"""
Module to handle DLPOLY control files
"""

from pathlib import Path
from .new_control import NewControl
from .utility import DLPData, check_arg


class FField(DLPData):
    """ Class defining properties relating to forcefields """
    def __init__(self, *_):
        DLPData.__init__(self, {"rvdw": float, "rcut": float, "rpad": float, "rpadset": bool,
                                "elec": bool, "elec_method": str, "metal": bool, "vdw": bool,
                                "ewald_vdw": bool, "elec_params": tuple, "vdw_params": dict,
                                "metal_style": str, "polar_method": str, "polar_t_hole": int})
        self.elec = False
        self.elec_method = "coul"
        self.elec_params = ("",)

        self.metal = False
        self.metal_style = "TAB"

        self.vdw = False
        self.vdw_params = {}

        self.rcut = 0.0
        self.rvdw = 0.0
        self.rpad = 0.0
        self.rpadset = False

        self.ewald_vdw = False

        self.polar_method = ""
        self.polar_t_hole = 0

    keysHandled = property(lambda self: ("reaction", "shift", "distance", "ewald", "spme",
                                         "coulomb", "rpad", "delr", "padding", "cutoff", "rcut",
                                         "cut", "rvdw", "metal", "vdw", "polar", "ewald_vdw"))

    def parse(self, key, vals):
        """ Handle key-vals for FField types

        :param key: Key to parse
        :param vals: Value to assign

        """
        full_name = {"lore": "lorentz-bethelot", "fend": "fender-halsey", "hoge": "hogervorst",
                     "halg": "halgren", "wald": "waldman-hagler", "tang": "tang-tonnies", "func":
                     "functional"}

        if check_arg(key, "spme"):
            key = "ewald"

        if check_arg(key, "reaction", "shift", "distan", "ewald", "coul"):
            vals = [val for val in vals if val != "field"]
            self.elec = True
            self.elec_method = key
            self.elec_params = vals
        elif check_arg(key, "rpad", "delr", "padding"):
            self.rpad = vals
            if check_arg(key, "delr"):
                self.rpad /= 4
            self.rpadset = True
        elif check_arg(key, "cutoff", "rcut", "cut"):
            self.rcut = vals
        elif check_arg(key, "rvdw"):
            self.rvdw = vals
        elif check_arg(key, "metal"):
            self.metal = True
            self.metal_style = vals
        elif check_arg(key, "vdw"):
            self.vdw = True
            while vals:
                val = vals.pop(0)
                if check_arg(val, "direct"):
                    self.vdw_params["direct"] = ""
                if check_arg(val, "mix"):
                    self.vdw_params["mix"] = full_name[check_arg(vals.pop(0), *full_name.keys())]
                if check_arg(val, "shift"):
                    self.vdw_params["shift"] = ""
        elif key == "polar":
            while vals:
                val = vals.pop()
                if check_arg(val, "scheme", "type", "dump", "factor"):
                    continue
                if check_arg(val, "charmm"):
                    self.polar_method = "charmm"
                elif check_arg(val, "thole"):
                    self.polar_t_hole = val.pop()
        elif key == "ewald_vdw":
            self.ewald_vdw = True

    def __str__(self):
        out_str = ""
        if self.elec:
            out_str += f"{self.elec_method} {' '.join(self.elec_params)}\n"
        if self.vdw:
            for key, val in self.vdw_params:
                out_str += f"vdw {key} {val}\n"
        if self.metal:
            out_str += f"metal {' '.join(self.metal_style)}\n"
        out_str += f"rcut {self.rcut}\n"
        out_str += f"rvdw {self.rvdw}\n"
        out_str += f"rpad {self.rpad}\n" if self.rpadset else ""
        return out_str


class Ignore(DLPData):
    """ Class definining properties that can be ignored """
    def __init__(self, *_):
        DLPData.__init__(self, {"elec": bool, "ind": bool, "str": bool,
                                "top": bool, "vdw": bool, "vafav": bool,
                                "vom": bool, "link": bool, "strict": bool})
        self.elec = False
        self.ind = False
        self.str = False
        self.top = False
        self.vdw = False
        self.vafav = False
        self.vom = False
        self.link = False
        self.strict = False

    keysHandled = property(lambda self: ("no",))

    def parse(self, _key, args):
        """ Parse disable/ignores

        :param _key: "NO", ignored
        :param args: Arg to assign

        """
        self[args[0]] = True

    def __str__(self):
        out_str = ""
        for item in self.keys:
            if getattr(self, item):
                out_str += f"no {item}\n"
        return out_str


class Analysis(DLPData):
    """ Class defining properties of analysis """
    def __init__(self, *_):
        DLPData.__init__(self, {"all": (int, int, float),
                                "bon": (int, int, float),
                                "ang": (int, int),
                                "dih": (int, int),
                                "inv": (int, int)})
        self.all = (0, 0, 0)
        self.bon = (0, 0)
        self.ang = (0, 0)
        self.dih = (0, 0)
        self.inv = (0, 0)

    keysHandled = property(lambda self: ("ana",))

    def parse(self, args):
        """ Parse analysis line

        :param args: Args to parse

        """
        self[args[0]] = args[1:]

    # def __str__(self):
        # if any(self.all > 0):
        #     return "analyse all every {} nbins {} rmax {}".format(*self.all)

        # outstr = ""
        # for analtype in ("bonds", "angles", "dihedrals", "inversions"):
        #     freq, nbins, rmax = getattr(self, analtype)
        #     if any(args > 0):
        #         outstr += f"analyse {analtype} every {freq} nbins {nbins} rmax {rmax}\n"
        # else
        #                    "analyse {} every {} nbind {}\n".format(analtype, *args))
        # return outstr


class Print(DLPData):
    """ Class definining properties that can be printed """
    def __init__(self, *_):
        DLPData.__init__(self, {"rdf": bool, "analysis": bool, "analysisprint": bool,
                                "analysis_object": Analysis, "printevery": int,
                                "vaf": bool, "zden": bool, "rdfevery": int, "vafevery": int,
                                "vafbin": int, "statsevery": int, "zdenevery": int,
                                "rdfprint": bool, "zdenprint": bool, "vafprint": bool})

        self.analysis_object = Analysis()
        self.rdf = False
        self.vaf = False
        self.zden = False
        self.analysis = False

        self.analysisprint = False
        self.rdfprint = False
        self.zdenprint = False
        self.vafprint = False

        self.printevery = 0
        self.statsevery = 0
        self.rdfevery = 0
        self.vafevery = 0
        self.vafbin = 0
        self.zdenevery = 0

    keysHandled = property(lambda self: ("print", "rdf", "zden", "stats", "analyse", "vaf"))

    def parse(self, key, args):
        """ Parse a split print line and see what it actually says

        :param key: Key to parse
        :param args: Values to assign

        """

        if check_arg(key, "print"):
            if args[0].isdigit():
                self.printevery = args[0]
            else:
                setattr(self, args[0]+"print", True)
                setattr(self, args[0], True)
                if hasattr(self, args[0]+"every"):
                    if not getattr(self, args[0]+"every") > 0:
                        setattr(self, args[0]+"every", 1)
        elif check_arg(key, "stats"):
            self.statsevery = args[0]
        elif check_arg(key, "rdf", "zden"):
            active = check_arg(key, "rdf", "zden")
            setattr(self, active, True)
            setattr(self, active+"every", args[0])
        elif check_arg(key, "ana"):
            self.analysis_object.parse(args)
        elif check_arg(key, "vaf"):
            self.vaf = True
            self.vafevery, self.vafbin = args

    def __str__(self):
        out_str = ""
        if self.printevery > 0:
            out_str += f"print every {self.printevery}\n"
        if self.statsevery > 0:
            out_str += f"stats {self.statsevery}\n"
        if self.analysis:
            out_str += "print analysis\n"
            out_str += str(self.analysis_object)
        for item in ("rdf", "vaf", "zden"):
            to_print, freq = getattr(self, item), getattr(self, item+"every")
            if to_print and freq:
                out_str += f"print {item}\n"
                out_str += f"{item}  {freq}\n"
        if self.vaf and self.vafevery:
            out_str += "print vaf\n"
            out_str += f"vaf {self.vafevery} {self.vafbin}"
        return out_str


class IOParam(DLPData):
    """ Class defining io parameters """

    dlp_files = property(lambda self: {"control", "field", "config", "statis", "output", "history",
                                       "historf", "revive", "revcon", "revold", "rdf", "msd",
                                       "tabvdw", "tabbnd", "tabang", "tabdih", "tabinv", "tabeam"})

    def __init__(self, **files_in):

        DLPData.__init__(self, {file_type: str for file_type in self.dlp_files})

        control_defined = 'control' in files_in

        # Set defaults
        files_in = {file: files_in.get(file, file.upper())
                    for file in self.dlp_files}

        # Get control's path
        if control_defined:
            control = files_in['control']

            true_control_path = Path(control).absolute().parent
            # Make other paths relative to control (i.e. load them correctly)
            # files = self.dlp_files - {"control"}

            files_in = {file: true_control_path / files_in[file]
                        for file in self.dlp_files}

        for file in ('control', 'field', 'config', 'statis',
                     'output', 'revive', 'revcon'):
            setattr(self, file, files_in[file])

        for file in ('history', 'historf', 'revold', 'rdf', 'msd'):
            setattr(self, file, "")

        for file in ('tabvdw', 'tabbnd', 'tabang', 'tabdih', 'tabinv', 'tabeam'):
            curr = files_in[file]
            setattr(self, file, curr if Path(curr).is_file() else "")

    keysHandled = property(lambda self: ("io",))

    def parse(self, _key, args):
        """ Parse an IO line

        :param _key: "IO", ignored
        :param args: Value to assign

        """
        setattr(self, args[0], args[1])

    def __str__(self):
        out = '\n'.join(f"io {file} {file_name}"
                        for file in self.dlp_files
                        if (file_name := getattr(self, file)))
        return out


class EnsembleParam:
    """ Class containing ensemble data """
    validMeans = {"nve": (None), "pmf": (None),
                  "nvt": ("evans", "langevin", "andersen", "berendsen",
                          "hoover", "gst", "ttm", "dpd"),
                  "npt": ("langevin", "berendsen", "hoover", "mtk"),
                  "nst": ("langevin", "berendsen", "hoover", "mtk")}
    meansArgs = {("nve", None): 0, ("pmf", None): 0,
                 ("nvt", "evans"): 0, ("nvt", "langevin"): 1, ("nvt", "andersen"): 2,
                 ("nvt", "berendsen"): 1, ("nvt", "berendsen"): 1,
                 ("nvt", "hoover"): (1, 2), ("nvt", "gst"): 2,
                 ("npt", "langevin"): 2, ("npt", "berendsen"): 2, ("npt", "berendsen"): 2,
                 ("npt", "hoover"): 2, ("npt", "mtk"): 2,
                 ("nst", "langevin"): range(2, 6), ("nst", "berendsen"): range(2, 6),
                 ("nst", "hoover"): range(2, 6), ("nst", "mtk"): range(2, 6)}

    full_name = {"lang": "langevin", "ander": "andersen", "ber": "berendsen", "hoover": "hoover",
                 "inhomo": "ttm", "ttm": "ttm", "mtk": "mtk", "dpd": "dpd", "gst": "gst"}

    keysHandled = property(lambda self: ("ensemble",))

    def __init__(self, *argsIn):
        if not argsIn:          # Default to NVE because why not?
            argsIn = ("nve")
        args = list(argsIn)[:]  # Make copy
        self._ensemble = args.pop(0)
        self._means = None
        if self.ensemble not in ("nve", "pmf"):
            trial = args.pop(0)
            test = check_arg(trial, *self.full_name)
            self.means = self.full_name.get(test, trial)
            if trial == "dpds2":
                self.dpd_order = 2
            else:
                self.dpd_order = 1
        self.args = args

        self.area = self.orth = self.tens = self.semi = False

        for index, arg in enumerate(self.args):
            if check_arg(arg, "area"):
                self.area = True
            if check_arg(arg, "orth"):
                self.orth = True
            if check_arg(arg, "tens"):
                self.tens = True
                self.tension = self.args[index+1]
            if check_arg(arg, "semi"):
                self.semi = True

    @property
    def ensemble(self):
        """ The thermodynamic ensemble """
        return self._ensemble

    @ensemble.setter
    def ensemble(self, ensemble):
        """ Set ensemble and check if valid """
        if ensemble not in EnsembleParam.validMeans:
            raise ValueError(f"Cannot set ensemble to be {ensemble}. "
                             f"Valid ensembles {', '.join(EnsembleParam.validMeans.keys())}.")
        self._means = None
        self.args = []
        self._ensemble = ensemble

    @property
    def means(self):
        """ The integrator used to maintain the ensemble """
        return self._means

    @means.setter
    def means(self, means):
        if means not in EnsembleParam.validMeans[self.ensemble]:
            raise ValueError(f"Cannot set means to be {means}. "
                             f"Valid means {', '.join(EnsembleParam.validMeans[self.ensemble])}.")
        self.args = []
        self._means = means

    def __str__(self):
        expect = EnsembleParam.meansArgs[(self.ensemble, self.means)]
        received = len(self.args)
        if ((isinstance(expect, (range, tuple)) and received not in expect) or
                (isinstance(expect, int) and received != expect)):
            raise IndexError(f"Wrong number of args in ensemble {self.ensemble} {self.means}. "
                             f"Expected {expect}, received {received}.")

        return " ".join((self.ensemble,
                         self.means if self.means else '',
                         *map(str, self.args))
                        )


class TimingParam(DLPData):
    """ Class defining io parameters """
    def __init__(self, **kwargs):
        DLPData.__init__(self, {"close": float, "steps": int, "equil": int, "timestep": float,
                                "variable": bool, "maxdis": float, "mindis": float, "mxstep": float,
                                "job": float, "collect": bool, "dump": int})
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

    keysHandled = property(lambda self: ("close", "steps", "equil", "timestep", "variable",
                                         "maxdis", "mindis", "mxstep", "job", "collect", "dump"))

    def parse(self, key, args):
        """ Parse a split timing line and see what it actually says

        :param key: Key to parse
        :param args: Values to assign

        """
        if check_arg(key,
                     "close",
                     "steps",
                     "equil",
                     "maxdis",
                     "mindis",
                     "mxstep",
                     "job",
                     "collect",
                     "dump"):
            setattr(self, key, args)
        if check_arg(key, "timestep", "variable"):
            if isinstance(args, (list, tuple)):
                word1 = args.pop(0)
            elif args:
                word1 = args
            else:
                word1 = ""

            if (key, word1) in (("timestep", "variable"), ("variable", "timestep")):
                self.variable = True
                self.timestep = args
            elif key == "variable":
                self.variable = args
            else:
                self.timestep = word1

    def __str__(self):
        out_str = ""
        return out_str


class Control(DLPData):
    """ Class defining a DLPOLY control file

        :param source: File to parse
    """
    def __init__(self, source=None):
        DLPData.__init__(self, {"l_scr": bool, "l_print": int, "l_eng": bool, "l_rout": bool,
                                "l_rin": bool, "l_tor": bool, "l_dis": int, "unit_test": bool,
                                "l_vdw": bool, "l_fast": bool, "ana": Analysis,
                                "app_test": bool, "currents": bool,
                                "binsize": float, "cap": float,
                                "densvar": float, "eps": float, "exclu": bool,
                                "heat_flux": bool, "rdf": int,
                                "coord": (int, int, int), "adf": (int, float),
                                "zden": int, "vaf": bool,
                                "mult": int, "mxshak": int, "pres": (float, ...),
                                "regaus": int, "replay": str, "restart": str, "quaternion": float,
                                "rlxtol": float, "scale": int, "slab": bool, "shake": float,
                                "stack": int, "temp": float, "yml_statis": bool, "yml_rdf": bool,
                                "title": str, "zero": str, "timing": TimingParam,
                                "print": Print, "ffield": FField, "ensemble": EnsembleParam,
                                "ignore": Ignore, "io": IOParam, "subcell": float,
                                "impact": (int, int, float, float, float, float),
                                "minim": (str, int, float, ...), "msdtmp": (int, int),
                                "nfold": (int, int, int), "optim": (str, float),
                                "pseudo": (str, float, float), "seed": (int, ...),
                                "time_depth": int, "time_per_mpi": bool, "dftb_driver": bool,
                                "disp": (int, int, float), "traj": (int, int, int),
                                "defe": (int, int, float, str), "evb": int})

        self.temp = 300.0
        self.title = "no title"
        self.l_scr = False
        self.l_tor = False
        self.l_eng = False
        self.l_rin = False
        self.l_rout = False
        self.l_dis = False
        self.l_fast = False
        self.io = IOParam(control=source)
        self.ignore = Ignore()
        self.print = Print()
        self.ffield = FField()
        self.ensemble = EnsembleParam("nve")
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
        """ Return iterable of handlers """
        return (self.io, self.ignore, self.print, self.ffield, self.timing, self.ana)

    @staticmethod
    def _strip_crap(args):

        return [arg for arg in args if
                not check_arg(arg, "constant", "every", "sampl", "tol",
                              "temp", "cutoff", "tensor", "collect",
                              "step", "forces", "sum", "time", "width", "threshold",
                              "nbins", "rmax")
                or check_arg(arg, "timestep")]

    def read(self, filename):
        """ Read a control file

        :param filename: File to read

        """
        with open(filename, "r", encoding="utf-8") as in_file:
            self["title"] = in_file.readline()
            for line in in_file:
                line = line.strip()
                if line == "finish":
                    break
                if not line or line.startswith("#"):
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
                    if check_arg(key, "ensemble"):
                        self.ensemble = EnsembleParam(*args)
                    else:
                        # Handle partial matching
                        self[key] = args

        return self

    def write(self, filename="CONTROL"):
        """ Write the control out to a file

        :param filename: Output file

        """
        def output(*args):
            print(file=out_file, *args)

        with open(filename, "w", encoding="utf-8") as out_file:
            output(self.title)
            for key, val in self.__dict__.items():
                if key in ("title", "filename") or key.startswith("_"):
                    continue
                if key == "timing":
                    for keyt, valt in self.timing.__dict__.items():
                        if keyt in ("job", "close"):
                            output(f"{keyt} time {valt}")
                        elif keyt == "timestep":
                            if self.timing.variable:
                                print("variable", keyt, valt, file=out_file)
                            else:
                                print(keyt, valt, file=out_file)
                        elif keyt == "variable":
                            continue
                        elif keyt in ("dump", "mindis", "maxdix", "mxstep") and valt > 0:
                            output(keyt, valt)
                        elif keyt == "collect" and valt:
                            output(keyt)
                        elif keyt in ("steps", "equil"):
                            output(keyt, valt)
                elif isinstance(val, bool):
                    if val and (key != "variable"):
                        output(key)
                    continue
                elif val in self._handlers:
                    output(val)
                elif isinstance(val, (tuple, list)):
                    output(key, " ".join(map(str, val)))
                else:
                    output(key, val)
            output("finish")

    def to_new(self):
        """ Return control in new style

        :returns: New control
        :rtype: NewControl

        """
        new_control = NewControl()

        def output(key, *vals):
            new_control[key] = vals

        output("title", self.title)
        for key, val in self.__dict__.items():
            if key in ("title", "filename") or key.startswith("_"):
                continue

            if key == "l_scr" and self.l_scr:
                output("io_file_output", "SCREEN")
            elif key == "l_tor" and self.l_tor:
                output("io_file_revcon", "NONE")
                output("io_file_revive", "NONE")
            elif key == "l_eng" and self.l_eng:
                output("output_energy", "ON")
            elif key == "l_rout" and self.l_rout:
                output("io_write_ascii_revive", "ON")
            elif key == "l_rin" and self.l_rin:
                output("io_read_ascii_revold", "ON")
            elif key == "l_print":
                output("print_level", val)
            elif key == "l_dis":
                output("initial_minimum_separation", val, "ang")
            elif key == "l_fast" and self.l_fast:
                output("unsafe_comms", "ON")
            elif key == "binsize":
                output("rdf_binsize", val, "ang")
                output("zden_binsize", val, "ang")
            elif key == "cap":
                output("equilibration_force_cap", val, "k_B.temp/ang")
            elif key == "densvar":
                output("density_variance", val, "%")
            elif key == "eps":
                output("coul_dielectric_constant", val)
            elif key == "exclu":
                output("coul_extended_exclusion", "ON")
            elif key == "heat_flux":
                output("heat_flux", "ON")
            elif key == "mxshak":
                output("shake_max_iter", val)
            elif key == "pres":
                if isinstance(val, (tuple, list)) and len(val) == 6:
                    output("pressure_tensor", *val, "katm")
                else:
                    output("pressure_hydrostatic", val[0], "katm")

            elif key == "regaus":
                output("regauss_frequency", val, "steps")
            elif key == "restart":
                if check_arg(val, 'scale'):
                    output("restart", "rescale")
                elif check_arg(val, "noscale", "unscale"):
                    output("restart", "noscale")
                elif not val:
                    output("restart", "continue")
                else:
                    output("restart", "clean")
            elif key == "rlxtol":
                if isinstance(val, (tuple, list)):
                    output("rlx_tol", val[0])
                    output("rlx_cgm_step", val[1])
                else:
                    output("rlx_tol", val)

            elif key == "scale":
                output("rescale_frequency", val, "steps")
            elif key == "shake":
                output("shake_tolerance", val, "ang")
            elif key == "stack":
                output("stack_size", val, "steps")
            elif key == "temp":
                output("temperature", val, "K")
            elif key == "zero":
                try:
                    output("reset_temperature_interval", val, "steps")
                except ValueError:
                    output("reset_temperature_interval", 1, "steps")
            elif key == "print":

                output("print_frequency", val.printevery, "steps")
                output("stats_frequency", val.statsevery, "steps")

                if val.rdfprint:
                    output("rdf_print", "ON")

                if val.rdf:
                    if not val.rdfprint:
                        output("rdf_print", "OFF")

                    output("rdf_calculate", "ON")
                    output("rdf_frequency", val.rdfevery, "steps")

                if val.vafprint:
                    output("vaf_print", "ON")

                if val.vaf:
                    if not val.vafprint:
                        output("vaf_print", "OFF")
                    output("vaf_calculate", "ON")
                    output("vaf_frequency", val.vafevery, "steps")
                    output("vaf_binsize", val.vafbin, "steps")

                if val.zdenprint:
                    output("zden_print", "ON")

                if val.zden:
                    if not val.zdenprint:
                        output("zden_print", "OFF")
                    output("zden_calculate", "ON")
                    output("zden_frequency", val.zdenevery, "steps")

            elif key == "ffield":
                if val.vdw and not self.ignore.vdw:
                    if "direct" in val.vdw_params:
                        output("vdw_method", "direct")
                    if "mix" in val.vdw_params:
                        output("vdw_mix_method", val.vdw_params["mix"])
                    if "shift" in val.vdw_params:
                        output("vdw_force_shift", "ON")

                if val.rvdw:
                    output("vdw_cutoff", val.rvdw, "ang")

                if val.rpadset:
                    output("padding", val.rpad, "ang")
                if val.rcut:
                    output("cutoff", val.rcut, "ang")

                if val.elec:

                    if val.elec_method == "shift":
                        val.elec_method = "force_shifted"

                    output("coul_method", val.elec_method)
                    if check_arg(val.elec_method, "ewald", "spme"):

                        if check_arg(val.elec_params[0], "precision"):
                            output("ewald_precision", val.elec_params[1])
                            if len(val.elec_params) > 2:
                                output("ewald_nsplines", val.elec_params[2])

                        else:
                            if check_arg(val.elec_params[0], "sum"):
                                parms = list(val.elec_params[1:])
                            else:
                                parms = list(val.elec_params)

                            output("ewald_alpha", parms.pop(0), "ang^-1")
                            if len(parms) >= 3:
                                output("ewald_kvec", parms.pop(0), parms.pop(0), parms.pop(0))
                            else:
                                continue
                            if parms:
                                output("ewald_nsplines", parms.pop(0))

                if val.metal_style == "sqrtrho":
                    output("metal_sqrtrho", "ON")
                elif val.metal_style == "direct":
                    output("metal_direct", "ON")

            elif key == "ensemble":
                output("ensemble", val.ensemble)
                if val.ensemble not in ("nve", "pmf"):
                    output("ensemble_method", val.means)

                if val.ensemble == "nvt":
                    if check_arg(val.means, "evans"):
                        continue

                    if check_arg(val.means, "langevin"):
                        output("ensemble_thermostat_friction", val.args[0], "ps^-1")
                    elif check_arg(val.means, "andersen"):
                        output("ensemble_thermostat_coupling", val.args[0], "ps")
                        output("ensemble_thermostat_softness", val.args[1])
                    elif check_arg(val.means, "berendsen", "hoover"):
                        output("ensemble_thermostat_coupling", val.args[0], "ps")
                    elif check_arg(val.means, "gst"):
                        output("ensemble_thermostat_coupling", val.args[0], "ps")
                        output("ensemble_thermostat_friction", val.args[1], "ps^-1")
                    elif check_arg(val.means, "dpd"):
                        output("ensemble_dpd_order", val.dpd_order)
                        if val.args:
                            output("ensemble_dpd_drag", val.args[0], 'Da/ps')
                    elif check_arg(val.means, "ttm"):
                        output("ttm_e-phonon_friction", val.args[0], "ps^-1")
                        output("ttm_e-stopping_friction", val.args[1], "ps^-1")
                        output("ttm_e-stopping_velocity", val.args[2], "ang/ps")

                if val.ensemble in ("npt", "nst"):
                    if check_arg(val.means, "langevin"):
                        output("ensemble_thermostat_friction", val.args[0], "ps^-1")
                        output("ensemble_barostat_friction", val.args[1], "ps^-1")
                    elif check_arg(val.means, "berendsen", "hoover", "mtk"):
                        output("ensemble_thermostat_coupling", val.args[0], "ps")
                        output("ensemble_barostat_coupling", val.args[1], "ps")

                if val.ensemble == "nst":
                    if val.area:
                        output('ensemble_semi_isotropic', 'area')
                    elif val.tens:
                        output('ensemble_semi_isotropic', 'tension')
                        output('ensemble_tension', val.tension, 'dyn/cm')
                    elif val.orth:
                        output('ensemble_semi_isotropic', 'orthorhombic')
                    if val.semi:
                        output('ensemble_semi_orthorhombic', 'ON')

            elif key == "ignore":
                if val.elec:
                    output("coul_method", "OFF")
                if val.ind:
                    output("ignore_config_indices", "ON")
                if val.str:
                    output("strict_checks", "OFF")
                if val.top:
                    output("print_topology_info", "OFF")
                if val.vdw:
                    output("vdw_method", "OFF")
                if val.vafav:
                    output("vaf_averaging", "OFF")
                if val.vom:
                    output("fixed_com", "OFF")
                if val.link:
                    continue

            elif key == "io":
                if not val.field.endswith("FIELD"):
                    output("io_file_field", val.field)
                if not val.config.endswith("CONFIG"):
                    output("io_file_config", val.config)
                if not val.statis.endswith("STATIS"):
                    output("io_file_statis", val.statis)
                if not val.history.endswith("HISTORY"):
                    output("io_file_history", val.history)
                if not val.historf.endswith("HISTORF"):
                    output("io_file_historf", val.historf)
                if not val.revive.endswith("REVIVE"):
                    output("io_file_revive", val.revive)
                if not val.revcon.endswith("REVCON") and not self.l_tor:
                    output("io_file_revcon", val.revcon)
                if not val.revold.endswith("REVOLD") and not self.l_tor:
                    output("io_file_revold", val.revold)
                if not val.rdf.endswith('RDFDAT'):
                    output('io_file_rdf', val.rdf)
                if not val.msd.endswith('MSDTMP'):
                    output('io_file_msd', val.msd)
                if not val.tabbnd.endswith('TABBND'):
                    output('io_file_tabbnd', val.tabbnd)
                if not val.tabang.endswith('TABANG'):
                    output('io_file_tabang', val.tabang)
                if not val.tabdih.endswith('TABDIH'):
                    output('io_file_tabdih', val.tabdih)
                if not val.tabinv.endswith('TABINV'):
                    output('io_file_tabinv', val.tabinv)
                if not val.tabvdw.endswith('TABVDW'):
                    output('io_file_tabvdw', val.tabvdw)
                if not val.tabeam.endswith('TABEAM'):
                    output('io_file_tabeam', val.tabeam)
            elif key == "defe":
                if val:
                    output("defects_calculate", "ON")
                    output("defects_start", val[0], "steps")
                    output("defects_interval", val[1], "steps")
                    output("defects_distance", val[2], "ang")
                    if len(val) > 3:
                        output("defects_backup", "ON")

            elif key == "disp":
                if val:
                    output("displacements_calculate", "ON")
                    output("displacements_start", val[0], "steps")
                    output("displacements_interval", val[1], "steps")
                    output("displacements_distance", val[2], "ang")

            elif key == "impact":
                if val:
                    output("impact_part_index", val[0])
                    output("impact_time", val[1], "steps")
                    output("impact_energy", val[2], "ke.V")
                    output("impact_direction", *val[3:], "ang/ps")

            elif key in ("minim", "optim"):

                crit = val.pop(0)
                tol = freq = step = 0
                if key == "minim" and val:
                    freq = val.pop(0)
                if val:
                    tol = val.pop(0)
                if val:
                    step = val.pop(0)

                if check_arg(crit, "forc"):
                    output("minimisation_criterion", "force")
                    criterion_unit = "internal_f"
                elif check_arg(crit, "ener"):
                    output("minimisation_criterion", "energy")
                    criterion_unit = "internal_e"
                elif check_arg(crit, "dist"):
                    output("minimisation_criterion", "distance")
                    criterion_unit = "internal_l"

                if tol:
                    output("minimisation_tolerance", tol, criterion_unit)
                if freq:
                    output("minimisation_frequency", freq, "steps")
                if step:
                    output("minimisation_step_length", step, "ang")

            elif key == "msdtmp":
                if val:
                    output("msd_calculate", "ON")
                    output("msd_start", val[0], "steps")
                    output("msd_frequency", val[1], "steps")

            elif key == "nfold":
                if val:
                    output("nfold", *val)

            elif key == "pseudo":
                if val:
                    output("pseudo_thermostat_method", val[0])
                    output("pseudo_thermostat_width", val[1], "ang")
                    output("pseudo_thermostat_temperature", val[2], "K")

            elif key == "seed":
                output("random_seed", *val)
            elif key == "traj":
                if val:
                    output("traj_calculate", "ON")
                    output("traj_start", val[0], "steps")
                    output("traj_interval", val[1], "steps")
                    if val[2] == 0:
                        tmp = 'pos'
                    elif val[2] == 1:
                        tmp = 'pos-vel'
                    elif val[2] == 2:
                        tmp = 'pos-vel-force'
                    elif val[2] == 3:
                        tmp = 'compressed'

                    output("traj_key", tmp)

            elif key == "timing":
                output("time_run", val.steps, "steps")
                output("time_equilibration", val.equil, "steps")

                if val.dump:
                    output("data_dump_frequency", val.dump, "steps")

                if val.job > 0.1:
                    output("time_job", val.job, "s")
                if val.close > 0.1:
                    output("time_close", val.close, "s")
                if val.collect:
                    output("record_equilibration", "ON")

                if val.variable:
                    output("timestep_variable", "ON")
                    if val.mindis:
                        output("timestep_variable_min_dist", val.mindis, "ang")
                    if val.maxdis:
                        output("timestep_variable_max_dist", val.maxdis, "ang")
                    if val.mxstep:
                        output("timestep_variable_max_delta", val.mxstep, "ps")

                output("timestep", val.timestep, "ps")
            elif key == "adf":

                output("adf_calculate", "ON")
                output("adf_frequency", val[0], "steps")
                output("adf_precision", val[1])

            elif key == "coord":

                output("coord_calculate", "ON")
                if val[0] == 0:
                    tmp = "icoord"
                elif val[0] == 1:
                    tmp = "ccoord"
                elif val[0] == 2:
                    tmp = "full"
                output("coord_ops", tmp)
                output("coord_interval", val[2], "steps")
                output("coord_start", val[1], "steps")

        return new_control


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        CONT = Control(sys.argv[1])
    else:
        CONT = Control("CONTROL")

    if len(sys.argv) > 2:
        CONT.write(sys.argv[2])
    else:
        CONT.write("new_control")
