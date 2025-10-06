"""
Module to handle DLPOLY control files.
"""

# pylint: disable=too-many-branches,too-many-statements,too-many-instance-attributes,too-many-lines
from pathlib import Path
from typing import Any, List, Literal, Sequence, Tuple, Union

from .new_control import NewControl
from .types import OptPath, PathLike
from .utility import DLPData, check_arg

EnsembleTypes = Literal["nve", "nvt", "npt", "nst"]
MeansTypes = Literal[
    "evans", "langevin", "andersen", "berendsen", "hoover", "gst", "ttm", "dpd", "mtk", None
]
COUL_TYPES = (
    "off",
    "ewald",
    "spme",
    "shift",
    "dddp",
    "pairwise",
    "reaction_field",
    "force_shifted",
)


class _FField(DLPData):
    """
    Class handling properties relating to forcefields.

    Attributes
    ----------
    rvdw : float
        Van der Waals' cutoff.
    rcut : float
        Other potentials cutoff.
    rpad : float
        Cutoff skin for haloes.
    rpadset : bool
        Whether `rpad` has been set.
    elec : bool
        Whether to compute electrostatics.
    elec_method : str
        Method to compute electrostatics.
    elec_params : tuple
        Parameters for electrostatics method.
    metal : bool
        Whether using metal-like interactions.
    metal_style : str
        Metal-like interaction method
    vdw : bool
        Whether using Van der Waals' interactions.
    ewald_vdw : bool
        Whether to compute VdW interactions with Ewald.
    vdw_params : dict
        Parameters for VdW interactions.
    polar_method : str
        Method for polarisation.
    polar_t_hole : int
        Number of T Holes in polarisation.
    """

    def __init__(self, *_):
        """
        Instantiate class handling force-field parameters.

        Parameters
        ----------
        *_
           Ignore all parameters, construction only valid through `parse`.
        """
        DLPData.__init__(
            self,
            {
                "rvdw": float,
                "rcut": float,
                "rpad": float,
                "rpadset": bool,
                "elec": bool,
                "elec_method": str,
                "metal": bool,
                "vdw": bool,
                "ewald_vdw": bool,
                "elec_params": tuple,
                "vdw_params": dict,
                "metal_style": str,
                "polar_method": str,
                "polar_t_hole": int,
            },
        )
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

    keysHandled = property(
        lambda self: (
            "reaction",
            "shift",
            "distance",
            "ewald",
            "spme",
            "coulomb",
            "rpad",
            "delr",
            "padding",
            "cutoff",
            "rcut",
            "cut",
            "rvdw",
            "metal",
            "vdw",
            "polar",
            "ewald_vdw",
        )
    )

    def parse(self, key: str, vals: Any):
        """
        Handle key-vals for FField interactions.

        Parameters
        ----------
        key : str
            Key to parse.
        vals : Any
            Values associated with key.
        """
        full_name = {
            "lore": "lorentz-bethelot",
            "fend": "fender-halsey",
            "hoge": "hogervorst",
            "halg": "halgren",
            "wald": "waldman-hagler",
            "tang": "tang-tonnies",
            "func": "functional",
        }

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

    def __str__(self) -> str:
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


class _Ignore(DLPData):
    """
    Class handling properties that can be ignored/disabled.

    Attributes
    ----------
    elec : bool
        Disable electrostatics.
    ind : bool
        Ignore config indices.
    top : bool
        Disable topology information printing.
    vdw : bool
        Disable Van der Waals' interactions.
    vafav : bool
        Disable computing average VAF.
    vom : bool
        Disable centre of mass velocity correction.
    link : bool
        Disable computation of linked-halos.
    strict : bool
        Disable strict checks.
    """

    def __init__(self, *_):
        """
        Instantiate class handling properties that can be ignored/disabled.

        Parameters
        ----------
        *_
           Ignore all parameters, construction only valid through `parse`.
        """
        DLPData.__init__(
            self,
            {
                "elec": bool,
                "ind": bool,
                "str": bool,
                "top": bool,
                "vdw": bool,
                "vafav": bool,
                "vom": bool,
                "link": bool,
                "strict": bool,
            },
        )
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

    def parse(self, _key: None, args: Any):
        """
        Parse ignore parameters.

        Parameters
        ----------
        _key : None
            Always "NO", disabled.
        args : Any
            Flag to disable.
        """
        self[args[0]] = True

    def __str__(self):
        out_str = ""
        for item in self.keys:
            if getattr(self, item):
                out_str += f"no {item}\n"
        return out_str


class _Analysis(DLPData):
    """
    Class handling properties of analysis.

    Attributes
    ----------
    all : tuple[int, int, float]
        Analyse all.
    bon : tuple[int, int, float]
        Analyse bonds.
    ang : tuple[int, int]
        Analyse angles.
    dih : tuple[int, int]
        Analyse dihedrals.
    inv : tuple[int, int]
        Analyse inversions.
    """

    def __init__(self, *_):
        """
        Instantiate class handling properties of analysis.

        Parameters
        ----------
        *_
           Ignore all parameters, construction only valid through `parse`.
        """
        DLPData.__init__(
            self,
            {
                "all": (int, int, float),
                "bon": (int, int, float),
                "ang": (int, int),
                "dih": (int, int),
                "inv": (int, int),
            },
        )
        self.all = (0, 0, 0)
        self.bon = (0, 0)
        self.ang = (0, 0)
        self.dih = (0, 0)
        self.inv = (0, 0)

    keysHandled = property(lambda self: ("ana",))

    def parse(self, args: Tuple[str, ...]):
        """
        Parse analysis line.

        Parameters
        ----------
        args : Tuple[str, ...]
            Analysis parameters.
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


class _Print(DLPData):
    """
    Class handling properties that can be printed.

    Attributes
    ----------
    printevery : int
       Print to OUTPUT every N steps.
    statsevery : int
       Dump STATIS file every N steps.

    rdf : bool
       Whether to compute RDF.
    rdfprint : bool
       Whether to write RDFTMP file.
    rdfevery : int
       Frequency of dumping RDF.

    analysis : bool
       Whether analysis is to be performed.
    analysisprint : bool
       Whether analysis is to be printed.
    analysis_object : _Analysis
       Analysis information.

    vaf : bool
       Whether to compute VAF.
    vafprint : bool
       Whether to write VAF File.
    vafevery : int
       Frequency of dumping VAF.
    vafbin : int
       Number of bins to average VAF over.

    zden : bool
       Compute Z-density.
    zdenevery : int
       Frequency of dumping Z-density.
    zdenprint : bool
       Whether to write ZDEN file.
    """

    def __init__(self, *_):
        """
        Instantiate class handling properties of that can be printed.

        Parameters
        ----------
        *_
           Ignore all parameters, construction only valid through `parse`.
        """
        DLPData.__init__(
            self,
            {
                "rdf": bool,
                "analysis": bool,
                "analysisprint": bool,
                "analysis_object": _Analysis,
                "printevery": int,
                "vaf": bool,
                "zden": bool,
                "rdfevery": int,
                "vafevery": int,
                "vafbin": int,
                "statsevery": int,
                "zdenevery": int,
                "rdfprint": bool,
                "zdenprint": bool,
                "vafprint": bool,
            },
        )

        self.analysis_object = _Analysis()
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

    def parse(self, key: str, args: Tuple[Any, ...]):
        """
        Parse a handled key into object parameters.

        Parameters
        ----------
        key : str
            Key to handle.
        args : Tuple[Any, ...]
            Arguments for key `key`.
        """

        if check_arg(key, "print"):
            if args[0].isdigit():
                self.printevery = args[0]
            else:
                setattr(self, args[0] + "print", True)
                setattr(self, args[0], True)
                if hasattr(self, args[0] + "every"):
                    if not getattr(self, args[0] + "every") > 0:
                        setattr(self, args[0] + "every", 1)
        elif check_arg(key, "stats"):
            self.statsevery = args[0]
        elif check_arg(key, "rdf", "zden"):
            active = check_arg(key, "rdf", "zden")
            setattr(self, active, True)
            setattr(self, active + "every", args[0])
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
            to_print, freq = getattr(self, item), getattr(self, item + "every")
            if to_print and freq:
                out_str += f"print {item}\n"
                out_str += f"{item}  {freq}\n"
        if self.vaf and self.vafevery:
            out_str += "print vaf\n"
            out_str += f"vaf {self.vafevery} {self.vafbin}"
        return out_str


class _IOParam(DLPData):
    """
    Class handling io parameters.

    Attributes
    ----------
    dlp_files : Tuple[str, ...]
        Files handled by `_IOParam`.
    control : str
    field : str
    config : str
    statis : str
    output : str
    history : str
    historf : str
    revive : str
    revcon : str
    revold : str
    rdf : str
    msd : str
    tabvdw : str
    tabbnd : str
    tabang : str
    tabdih : str
    tabinv : str
    tabeam : str
    cor : str
    currents : str

    Methods
    -------
    parse(key, args)
        Parse a handled key into object parameters.
    """

    dlp_files = property(
        lambda self: {
            "control",
            "field",
            "config",
            "statis",
            "output",
            "history",
            "historf",
            "revive",
            "revcon",
            "revold",
            "rdf",
            "msd",
            "tabvdw",
            "tabbnd",
            "tabang",
            "tabdih",
            "tabinv",
            "tabeam",
            "cor",
            "currents",
        }
    )

    def __init__(self, **files_in: PathLike):
        """
        Instantiate class handling parameters related to I/O.

        Parameters
        ----------
        **files_in : PathLike
            Override defaults on instantiation.
        """

        DLPData.__init__(self, {file_type: str for file_type in self.dlp_files})

        control_defined = "control" in files_in and files_in["control"]

        # Set defaults
        for file in self.dlp_files:
            files_in.setdefault(file, file.upper())

        # Get control's path
        if control_defined:
            control = files_in["control"]

            true_control_path = Path(control).absolute().parent

            # Make other paths relative to control (i.e. load them correctly)
            # files = self.dlp_files - {"control"}

            files_in = {file: true_control_path / files_in[file] for file in self.dlp_files}

        for file in ("control", "field", "config", "statis", "output", "revive", "revcon"):
            setattr(self, file, files_in[file])

        for file in ("history", "historf", "revold", "rdf", "msd", "cor", "currents"):
            setattr(self, file, "")

        for file in ("tabvdw", "tabbnd", "tabang", "tabdih", "tabinv", "tabeam"):
            curr = files_in[file]
            setattr(self, file, curr if Path(curr).is_file() else "")

    keysHandled = property(lambda self: ("io",))

    def parse(self, _key: None, args: Tuple[str, Any]):
        """
        Parse an IO line.

        Parameters
        ----------
        _key : None
            Ignored as always "IO".
        args : Tuple[str, Any]
            Arguments to set.
        """
        setattr(self, args[0], args[1])

    def __str__(self):
        out = "\n".join(
            f"io {file} {file_name}"
            for file in self.dlp_files
            if (file_name := getattr(self, file))
        )
        return out


class _EnsembleParam:
    """
    Class containing ensemble data.

    Attributes
    ----------
    validMeans : Dict[str, Tuple[Optional[str], ...]
        Valid possibilities for given means.
    meansArgs : Dict[Tuple[str, Optional[str]], int]
        Number of expected args for given means combination.
    full_name : Dict[str, str]
        Mapping from abbreviated name to full name.
    ensemble : {"nve", "nvt", "npt", "nst", "pmf"}
        MD Ensemble to use.
    means : Optional[str]
        Thermostat/Barostat integrator to use.
    args : Tuple[Any, ...]
        List of ensemble arguments.

    dpd_order : {1, 2}
        Order of dissipative particle dynamics integrator

    area : bool
        Semi-isotropic ensemble constraints.
    orth : bool
        Semi-isotropic ensemble constraints.
    tens : bool
        Semi-isotropic ensemble constraints.
    tension : float
        Constraint value.
    semi : bool
        Semi-isotropic ensemble constraints.
    """

    validMeans = {
        "nve": (None,),
        "pmf": (None,),
        "nvt": ("evans", "langevin", "andersen", "berendsen", "hoover", "gst", "ttm", "dpd"),
        "npt": ("langevin", "berendsen", "hoover", "mtk"),
        "nst": ("langevin", "berendsen", "hoover", "mtk"),
    }
    meansArgs = {
        ("nve", None): 0,
        ("pmf", None): 0,
        ("nvt", "evans"): 0,
        ("nvt", "langevin"): 1,
        ("nvt", "andersen"): 2,
        ("nvt", "berendsen"): 1,
        ("nvt", "hoover"): (1, 2),
        ("nvt", "gst"): 2,
        ("npt", "langevin"): 2,
        ("npt", "berendsen"): 2,
        ("npt", "hoover"): 2,
        ("npt", "mtk"): 2,
        ("nst", "langevin"): range(2, 6),
        ("nst", "berendsen"): range(2, 6),
        ("nst", "hoover"): range(2, 6),
        ("nst", "mtk"): range(2, 6),
    }

    full_name = {
        "lang": "langevin",
        "ander": "andersen",
        "ber": "berendsen",
        "hoover": "hoover",
        "inhomo": "ttm",
        "ttm": "ttm",
        "mtk": "mtk",
        "dpd": "dpd",
        "gst": "gst",
    }

    keysHandled = property(lambda self: ("ensemble",))

    def __init__(self, *argsIn):
        """
        Instantiate class handling ensembles.

        Parameters
        ----------
        *argsIn : Tuple[str, ...]
            Split DLPoly old-style ``ensemble`` line.
        """
        if not argsIn:  # Default to NVE because why not?
            argsIn = "nve"
        args = list(argsIn)[:]  # Make copy
        self._ensemble = args.pop(0)
        self._means = None
        if self.ensemble not in {"nve", "pmf"}:
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
                self.tension = self.args[index + 1]
            if check_arg(arg, "semi"):
                self.semi = True

    @property
    def ensemble(self) -> EnsembleTypes:
        """
        The thermodynamic ensemble.
        """
        return self._ensemble

    @ensemble.setter
    def ensemble(self, ensemble: EnsembleTypes):
        """
        Set the ensemble and ensure is valid. Also reset mean and args ready for subsequent setting.

        Parameters
        ----------
        ensemble : EnsembleTypes
            Type of ensemble.

        Raises
        ------
        ValueError
            If ensemble not in allowed ensembles.
        """
        if ensemble not in _EnsembleParam.validMeans:
            raise ValueError(
                f"Cannot set ensemble to be {ensemble}. "
                f"Valid ensembles {', '.join(_EnsembleParam.validMeans.keys())}."
            )
        self._means = None
        self.args = []
        self._ensemble = ensemble

    @property
    def means(self):
        """The integrator used to maintain the ensemble."""
        return self._means

    @means.setter
    def means(self, means: MeansTypes):
        if means not in _EnsembleParam.validMeans[self.ensemble]:
            raise ValueError(
                f"Cannot set means to be {means}. "
                f"Valid means {', '.join(map(str, _EnsembleParam.validMeans[self.ensemble]))}."
            )
        self.args = []
        self._means = means

    def __str__(self):
        expect = _EnsembleParam.meansArgs[(self.ensemble, self.means)]
        received = len(self.args)
        if (isinstance(expect, (range, tuple)) and received not in expect) or (
            isinstance(expect, int) and received != expect
        ):
            raise IndexError(
                f"Wrong number of args in ensemble {self.ensemble} {self.means}. "
                f"Expected {expect}, received {received}."
            )

        return " ".join((self.ensemble, self.means if self.means else "", *map(str, self.args)))


class _TimingParam(DLPData):
    """
    Class handling time parameters.

    Attributes
    ----------
    close : float
    steps : int
    equil : int
    timestep : float
    variable : bool
    maxdis : float
    mindis : float
    mxstep : float
    job : float
    collect : bool
    dump : int
    """

    def __init__(self, **kwargs):
        """
        Instantiate class for handling parameters related to time.

        Parameters
        ----------
        **kwargs
            Params to initialise defaults from.
        """

        DLPData.__init__(
            self,
            {
                "close": float,
                "steps": int,
                "equil": int,
                "timestep": float,
                "variable": bool,
                "maxdis": float,
                "mindis": float,
                "mxstep": float,
                "job": float,
                "collect": bool,
                "dump": int,
            },
        )
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

    keysHandled = property(
        lambda self: (
            "close",
            "steps",
            "equil",
            "timestep",
            "variable",
            "maxdis",
            "mindis",
            "mxstep",
            "job",
            "collect",
            "dump",
        )
    )

    def parse(self, key: str, args: Union[Any, Sequence[Any]]):
        """
        Parse a handled key into object parameters.

        Parameters
        ----------
        key : str
            Key to parse.
        args : Union[Any, Sequence[Any]]
            Values associated with key.
        """
        if check_arg(
            key, "close", "steps", "equil", "maxdis", "mindis", "mxstep", "job", "collect", "dump"
        ):
            setattr(self, key, args)
        if check_arg(key, "timestep", "variable"):
            if isinstance(args, (list, tuple)):
                word1, *args = args
            elif args:
                word1 = args
            else:
                word1 = ""

            if (key, word1) in {("timestep", "variable"), ("variable", "timestep")}:
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
    """
    Class handling a DLPOLY control file.

    Attributes
    ----------
    source : OptPath
        File data originally read from.

    Notes
    -----
    For meanings of parameters, see DLPoly manual.
    """

    def __init__(self, source: OptPath = None):
        """
        Instantiate old-style DLPoly control taking initial parameters from `source`.

        Parameters
        ----------
        source : OptPath
            File to read data from.
        """
        DLPData.__init__(
            self,
            {
                "l_scr": bool,
                "l_print": int,
                "l_eng": bool,
                "l_rout": bool,
                "l_rin": bool,
                "l_tor": bool,
                "l_dis": int,
                "unit_test": bool,
                "l_vdw": bool,
                "l_fast": bool,
                "ana": _Analysis,
                "app_test": bool,
                "currents": bool,
                "binsize": float,
                "cap": float,
                "densvar": float,
                "eps": float,
                "exclu": bool,
                "heat_flux": bool,
                "rdf": int,
                "coord": (int, int, int),
                "adf": (int, float),
                "zden": int,
                "vaf": bool,
                "mult": int,
                "mxshak": int,
                "pres": (float, ...),
                "regaus": int,
                "replay": str,
                "restart": str,
                "quaternion": float,
                "rlxtol": float,
                "scale": int,
                "slab": bool,
                "shake": float,
                "stack": int,
                "temp": float,
                "yml_statis": bool,
                "yml_rdf": bool,
                "title": str,
                "zero": str,
                "timing": _TimingParam,
                "print": _Print,
                "ffield": _FField,
                "ensemble": _EnsembleParam,
                "ignore": _Ignore,
                "io": _IOParam,
                "subcell": float,
                "impact": (int, int, float, float, float, float),
                "minim": (str, int, float, ...),
                "msdtmp": (int, int),
                "nfold": (int, int, int),
                "optim": (str, float),
                "pseudo": (str, float, float),
                "seed": (int, ...),
                "time_depth": int,
                "time_per_mpi": bool,
                "dftb_driver": bool,
                "disp": (int, int, float),
                "traj": (int, int, int),
                "defe": (int, int, float, str),
                "evb": int,
            },
        )

        self.temp = 300.0
        self.title = "no title"
        self.l_scr = False
        self.l_tor = False
        self.l_eng = False
        self.l_rin = False
        self.l_rout = False
        self.l_dis = False
        self.l_fast = False
        self.io = _IOParam(control=source or "CONTROL")
        self.ignore = _Ignore()
        self.print = _Print()
        self.ffield = _FField()
        self.ensemble = _EnsembleParam("nve")
        self.ana = _Analysis()
        self.timing = _TimingParam(collect=False, steps=0, equil=0, variable=False, timestep=0.001)

        if source is not None:
            self.source = source
            self.read(source)

    @property
    def _handlers(self) -> Tuple[_IOParam, _Ignore, _Print, _FField, _TimingParam, _Analysis]:
        """
        Return tuple of all handlers.

        Returns
        -------
        Tuple[_IOParam, _Ignore, _Print, _FField, _TimingParam, _Analysis]
            Contained handlers.
        """
        return (self.io, self.ignore, self.print, self.ffield, self.timing, self.ana)

    @staticmethod
    def _strip_crap(args: Sequence[str]) -> List[str]:
        """
        Remove unnecessary extra words from argument lists.

        Parameters
        ----------
        args : Sequence[str]
            Argument list to strip.

        Returns
        -------
        List[str]
            Stripped argument list.
        """

        return [
            arg
            for arg in args
            if not check_arg(
                arg,
                "constant",
                "every",
                "sampl",
                "tol",
                "temp",
                "cutoff",
                "tensor",
                "collect",
                "step",
                "forces",
                "sum",
                "time",
                "width",
                "threshold",
                "nbins",
                "rmax",
            )
            or check_arg(arg, "timestep")
        ]

    def read(self, filename: PathLike) -> "Control":
        """
        Read a DLPoly old-style CONTROL file.

        Parameters
        ----------
        filename : PathLike
            Source file to read.

        Returns
        -------
        Control
            Updated object after read.
        """
        with open(filename, "r", encoding="utf-8") as in_file:
            self["title"] = in_file.readline()
            for line in map(str.strip, in_file):
                if line == "finish":
                    break
                if not line or line.startswith("#"):
                    continue
                key, *args = line.split()
                args = self._strip_crap(args)
                if not args:
                    args = []
                key = key.lower()

                for handler in self._handlers:
                    keyhand = check_arg(key, *handler.keysHandled)
                    if keyhand:
                        handler.parse(keyhand, args)
                        break
                else:
                    if check_arg(key, "ensemble"):
                        self.ensemble = _EnsembleParam(*args)
                    else:
                        # Handle partial matching
                        self[key] = args

        return self

    def write(self, filename: PathLike = "CONTROL"):
        """
        Write a DLPoly old-style CONTROL file to file.

        Parameters
        ----------
        filename : PathLike
            File to write to.
        """

        def output(*args: Any):
            """
            Write arguments to file as space-separated strings.
            """
            print(file=out_file, *args)

        with open(filename, "w", encoding="utf-8") as out_file:
            output(self.title)
            for key, val in self.__dict__.items():
                if key in {"title", "filename"} or key.startswith("_"):
                    continue

                if key == "timing":
                    for keyt, valt in self.timing.__dict__.items():
                        match keyt:
                            case "job" | "close":
                                output(f"{keyt} time {valt}")
                            case "timestep" if self.timing.variable:
                                print("variable", keyt, valt, file=out_file)
                            case "timestep" if not self.timing.variable:
                                print(keyt, valt, file=out_file)
                            case "variable":
                                continue
                            case "dump" | "mindis" | "maxdis" | "mxstep" if valt > 0:
                                output(keyt, valt)
                            case "collect" if valt:
                                output(keyt)
                            case "steps" | "equil":
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

    def to_new(self) -> NewControl:
        """
        Convert old-style DLPoly CONTROL to new-style.

        Returns
        -------
        NewControl
            Converted Control data.
        """
        new_control = NewControl()

        def output(key: str, *vals):
            """
            Set key to appropriate values (as tuple).

            Parameters
            ----------
            key : str
                Key to set.
            *vals
                Values to set.
            """
            new_control[key] = vals

        output("title", self.title)
        for key, val in self.__dict__.items():
            match key:
                case "title" | "filename" | ["_", *_]:
                    continue
                case "l_scr" if self.l_scf:
                    output("io_file_output", "SCREEN")
                case "l_tor" if self.l_tor:
                    output("io_file_revcon", "NONE")
                    output("io_file_revive", "NONE")
                case "l_eng" if self.l_eng:
                    output("output_energy", "ON")
                case "l_rout" if self.l_rout:
                    output("io_write_ascii_revive", "ON")
                case "l_rin" if self.l_rin:
                    output("io_read_ascii_revold", "ON")
                case "l_print":
                    output("print_level", val)
                case "l_dis":
                    output("initial_minimum_separation", val, "ang")
                case "l_fast" if self.l_fast:
                    output("unsafe_comms", "ON")
                case "binsize":
                    output("rdf_binsize", val, "ang")
                    output("zden_binsize", val, "ang")
                case "cap":
                    output("equilibration_force_cap", val, "k_B.temp/ang")
                case "densvar":
                    output("density_variance", val, "%")
                case "eps":
                    output("coul_dielectric_constant", val)
                case "exclu":
                    output("coul_extended_exclusion", "ON")
                case "heat_flux":
                    output("heat_flux", "ON")
                case "mxshak":
                    output("shake_max_iter", val)
                case "pres" if isinstance(val, (tuple, list)) and len(val) == 6:
                    output("pressure_tensor", *val, "katm")
                case "pres":
                    output("pressure_hydrostatic", val[0], "katm")
                case "regaus":
                    output("regauss_frequency", val, "steps")
                case "restart" if check_arg(val, "scale"):
                    output("restart", "rescale")
                case "restart" if check_arg(val, "noscale", "rescale"):
                    output("restart", "noscale")
                case "restart" if not val:
                    output("restart", "continue")
                case "restart":
                    output("restart", "clean")
                case "rlxtol" if isinstance(val, (tuple, list)):
                    output("rlx_tol", val[0])
                    output("rlx_cgm_step", val[1])
                case "rlxtol":
                    output("rlx_tol", val)
                case "scale":
                    output("rescale_frequency", val, "steps")
                case "shake":
                    output("shake_tolerance", val, "ang")
                case "stack":
                    output("stack_size", val, "steps")
                case "temp":
                    output("temperature", val, "K")
                case "zero":
                    try:
                        output("reset_temperature_interval", val, "steps")
                    except ValueError:
                        output("reset_temperature_interval", 1, "steps")
                case "print":
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

                case "ffield":
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
                        elec_method = check_arg(val.elec_method, *COUL_TYPES)

                        match (elec_method, val.elec_params):
                            case ("spme" | "ewald", ["precision", prec, *nsplines]):
                                output("coul_method", "spme")
                                output("spme_precision", prec)
                                if nsplines:
                                    output("spme_nsplines", *nsplines)
                            case ("spme" | "ewald", ["sum", alpha, *kvec] | [alpha, *kvec]):
                                output("coul_method", "spme")
                                output("spme_alpha", alpha, "ang^-1")

                                nsplines = None
                                if len(kvec) == 4:
                                    *kvec, nsplines = kvec

                                if kvec:
                                    output("spme_kvec", *kvec)
                                if nsplines:
                                    output("spme_nsplines", nsplines)
                            case ("shift" | "force_shifted", _):
                                output("coul_method", elec_method)
                            case (method, _):
                                output("coul_method", method)

                    match val.metal_style:
                        case "sqrtrho":
                            output("metal_sqrtrho", "ON")
                        case "direct":
                            output("metal_direct", "ON")

                case "ensemble":
                    output("ensemble", val.ensemble)

                    match (val.ensemble, val.means, val.args):
                        case ("nve" | "pmf", _, _):
                            pass
                        case ("nvt", "evans", []):
                            output("ensemble_method", "evans")
                        case ("nvt", "langevin", [friction]):
                            output("ensemble_method", "langevin")
                            output("ensemble_thermostat_friction", friction, "ps^-1")
                        case ("nvt", "andersen", [coupling, softness]):
                            output("ensemble_method", "andersen")
                            output("ensemble_thermostat_coupling", coupling, "ps")
                            output("ensemble_thermostat_softness", softness)
                        case ("nvt", "berendsen" | "hoover" as means, [coupling]):
                            output("ensemble_method", means)
                            output("ensemble_thermostat_coupling", coupling, "ps")
                        case ("nvt", "gst", [coupling, friction]):
                            output("ensemble_method", "gst")
                            output("ensemble_thermostat_coupling", coupling, "ps")
                            output("ensemble_thermostat_friction", friction, "ps^-1")
                        case ("nvt", "dpd", [*drag]):
                            output("ensemble_method", "dpd")
                            output("ensemble_dpd_order", val.dpd_order)
                            if drag:
                                output("ensemble_dpd_drag", drag[0], "Da/ps")
                        case (
                            "nvt",
                            "ttm",
                            [phonon_friction, stopping_friction, stopping_velocity],
                        ):
                            output("ensemble_method", "ttm")
                            output("ttm_e-phonon_friction", phonon_friction, "ps^-1")
                            output("ttm_e-stopping_friction", stopping_friction, "ps^-1")
                            output("ttm_e-stopping_velocity", stopping_velocity, "ang/ps")
                        case ("npt" | "nst", "langevin", [thermostat_friction, barostat_friction]):
                            output("ensemble_method", "langevin")
                            output("ensemble_thermostat_friction", thermostat_friction, "ps^-1")
                            output("ensemble_barostat_friction", barostat_friction, "ps^-1")
                        case (
                            "npt" | "nst",
                            "berendsen" | "hoover" | "mtk" as means,
                            [thermostat_coupling, barostat_coupling],
                        ):
                            output("ensemble_method", means)
                            output("ensemble_thermostat_coupling", thermostat_coupling, "ps")
                            output("ensemble_barostat_coupling", barostat_coupling, "ps")
                        case _:
                            raise Exception(f"{val.ensemble} not compatible with {val.means}.")

                    if val.ensemble == "nst":
                        if val.area:
                            output("ensemble_semi_isotropic", "area")
                        elif val.tens:
                            output("ensemble_semi_isotropic", "tension")
                            output("ensemble_tension", val.tension, "dyn/cm")
                        elif val.orth:
                            output("ensemble_semi_isotropic", "orthorhombic")
                        if val.semi:
                            output("ensemble_semi_orthorhombic", "ON")

                case "ignore":
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

                case "io":
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
                    if not val.rdf.endswith("RDFDAT"):
                        output("io_file_rdf", val.rdf)
                    if not val.msd.endswith("MSDTMP"):
                        output("io_file_msd", val.msd)
                    if not val.tabbnd.endswith("TABBND"):
                        output("io_file_tabbnd", val.tabbnd)
                    if not val.tabang.endswith("TABANG"):
                        output("io_file_tabang", val.tabang)
                    if not val.tabdih.endswith("TABDIH"):
                        output("io_file_tabdih", val.tabdih)
                    if not val.tabinv.endswith("TABINV"):
                        output("io_file_tabinv", val.tabinv)
                    if not val.tabvdw.endswith("TABVDW"):
                        output("io_file_tabvdw", val.tabvdw)
                    if not val.tabeam.endswith("TABEAM"):
                        output("io_file_tabeam", val.tabeam)
                case "defe" if val:
                    output("defects_calculate", "ON")
                    output("defects_start", val[0], "steps")
                    output("defects_interval", val[1], "steps")
                    output("defects_distance", val[2], "ang")
                    if len(val) > 3:
                        output("defects_backup", "ON")

                case "disp" if val:
                    output("displacements_calculate", "ON")
                    output("displacements_start", val[0], "steps")
                    output("displacements_interval", val[1], "steps")
                    output("displacements_distance", val[2], "ang")

                case "impact" if val:
                    output("impact_part_index", val[0])
                    output("impact_time", val[1], "steps")
                    output("impact_energy", val[2], "ke.V")
                    output("impact_direction", *val[3:], "ang/ps")

                case "minim" | "optim":
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

                case "msdtmp" if val:
                    output("msd_calculate", "ON")
                    output("msd_start", val[0], "steps")
                    output("msd_frequency", val[1], "steps")

                case "nfold" if val:
                    output("nfold", *val)

                case "pseudo" if val:
                    output("pseudo_thermostat_method", val[0])
                    output("pseudo_thermostat_width", val[1], "ang")
                    output("pseudo_thermostat_temperature", val[2], "K")

                case "seed":
                    output("random_seed", *val)
                case "traj" if val:
                    output("traj_calculate", "ON")
                    output("traj_start", val[0], "steps")
                    output("traj_interval", val[1], "steps")

                    tmp = ("pos", "pos-vel", "pos-vel-force", "compressed")[val[2]]

                    output("traj_key", tmp)

                case "timing":
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
                case "adf":
                    output("adf_calculate", "ON")
                    output("adf_frequency", val[0], "steps")
                    output("adf_precision", val[1])

                case "coord":
                    output("coord_calculate", "ON")
                    tmp = ("icoord", "ccoord", "full")[val[0]]
                    output("coord_ops", tmp)
                    output("coord_start", val[1], "steps")
                    output("coord_interval", val[2], "steps")

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
