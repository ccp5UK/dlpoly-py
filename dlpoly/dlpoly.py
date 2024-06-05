"""
Module containing main DLPOLY class.
"""

import os
import shlex
import shutil
import subprocess
from functools import cached_property
from os import PathLike
from pathlib import Path
from typing import Literal, Optional, Sequence, Type

from .cli import get_command_args
from .config import Config
from .control import Control
from .correlations import Correlations
from .currents import Currents
from .field import Field
from .input import ANG, BND, DIH, EAM, INV, VDW
from .msd import MSD
from .new_control import NewControl, is_new_control
from .rdf import RDF
from .statis import Statis
from .types import OptPath
from .utility import copy_file, is_mpi, next_file, DLPFile

FileTypes = Literal["field", "config", "statis", "history",
                    "historf", "revive", "revcon", "revold",
                    "rdf", "msd"]


class DLPoly:
    """
    Main class of a DLPOLY runnable set of instructions.

    Attributes
    ----------
    control : Control
        Main DLPoly control object.
    config : Config
        Atomic configuration.
    field : Field
        DLPoly field file.

    dest_config : PathLike
        Location to copy configuration to.
    default_name : str
        Base name for workdir.
        If this directory exists, a number will be appended to this
        to make the workdir name.
    """
    __version__ = "5.0"  # which version of dlpoly supports

    OUTPUT_FILES = ("statis", "msd", "rdf", "correlations", "currents")

    def __init__(
            self, *,
            control: OptPath = None,
            config: OptPath = None,
            field: OptPath = None,
            statis: OptPath = None,
            output: OptPath = None,
            dest_config: OptPath = None,
            workdir: OptPath = None,
            default_name: str = "dlprun",
            exe: OptPath = None,
            rdf: OptPath = None,
            msd: OptPath = None,
            correlations: OptPath = None,
            currents: OptPath = None,
            vdw_file: OptPath = None,
            eam_file: OptPath = None,
            bnd_file: OptPath = None,
            ang_file: OptPath = None,
            dih_file: OptPath = None,
            inv_file: OptPath = None
    ):
        """
        Main class of a DLPOLY runnable set of instructions.

        Parameters
        ----------
        control : OptPath
            Main control file to load.
        config : OptPath
            Main config file to load.
        field : OptPath
            Main field file to load.
        statis : OptPath
            Statis file to load.
        output : OptPath
            File to write output log to.

        Other Parameters
        ----------------
        dest_config : OptPath
            Configuration to write to when task is `run`.
        workdir : OptPath
            Directory where tasks should be copied before running.
            Will be cleared if already exists.
        default_name : str
            Base-name for `workdir` (if `workdir` is `None`),
            If already exists, will append numbers and create new name.
            Default is "dlprun".
        exe : OptPath
            Location of DLPOLY executable.

        rdf : OptPath
            RDF file to load.
        msd : OptPath
            MSD file to load.
        correlations : OptPath
            Correlations file to load.
        currents : OptPath
            Currents file to load.

        vdw_file : OptPath
            Input TABVDW location.
        eam_file : OptPath
            Input TABEAM location.
        bnd_file : OptPath
            Input TABBND location.
        ang_file : OptPath
            Input TABANG location.
        dih_file : OptPath
            Input TABDIH location.
        inv_file : OptPath
            Input TABINV location.
        """

        # Default to having a control
        self.control = NewControl()
        self.dest_config = dest_config
        self.default_name = default_name
        self.config = None
        self.field = None
        self.exe = exe
        self.workdir = workdir

        self.load_control(control)

        for (cls, source) in ((Config, config),
                              (Field, field),
                              (Statis, statis),
                              (RDF, rdf),
                              (MSD, msd),
                              (Correlations, correlations),
                              (Currents, currents),
                              (VDW, vdw_file),
                              (EAM, eam_file),
                              (BND, bnd_file),
                              (ANG, ang_file),
                              (DIH, dih_file),
                              (INV, inv_file)):
            self.load_file(cls, source)

        # Override output
        if output is not None:
            self.control.io_file_output = output

    control_file = DLPFile()
    field_file = DLPFile()
    vdw_file = DLPFile('tabvdw')
    eam_file = DLPFile('tabeam')
    bnd_file = DLPFile('tabbnd')
    ang_file = DLPFile('tabang')
    dih_file = DLPFile('tabdih')
    inv_file = DLPFile('tabinv')
    config_file = DLPFile()
    statis_file = DLPFile()
    rdf_file = DLPFile()
    msd_file = DLPFile()
    correlations_file = DLPFile('cor')
    currents_file = DLPFile()

    @cached_property
    def statis(self) -> Statis:
        """
        Load statis and return it.
        """
        self.load_statis(required=True)
        return self.statis

    @cached_property
    def rdf(self) -> RDF:
        """
        Load rdf and return it.
        """
        self.load_rdf(required=True)
        return self.rdf

    @cached_property
    def msd(self) -> MSD:
        """
        Load msd and return it.
        """
        self.load_msd(required=True)
        return self.msd

    @cached_property
    def currents(self) -> Currents:
        """
        Load currents and return it.
        """
        self.load_currents(required=True)
        return self.currents

    @cached_property
    def correlations(self) -> Correlations:
        """
        Load correlations and return it.
        """
        self.load_correlations(required=True)
        return self.correlations

    def redir_output(self, direc: OptPath = None):
        """
        Redirect output to direc and update self for later parsing.

        Parameters
        ----------
        direc : OptPath
            Directory to redirect to.
        """

        def get_file_def(filetype: FileTypes, default: PathLike) -> PathLike:
            """
            Get default filename if filename not specified.

            Parameters
            ----------
            filetype : FileTypes
                File type to load.
            default : PathLike
                Name if `filetype` not set.

            Returns
            -------
            PathLike
                Filename from `Control` if set else `default`.
            """
            if path := getattr(self.control,
                               f"io_file_{filetype}", False):
                return path
            return default

        if direc is None:
            direc = self.workdir.absolute()
        else:
            direc = Path(direc).absolute()

        # Set the path to be: direc/filename, stripping off all unnecessary pathing
        self.control.io_file_statis = str(direc / self.statis_file.name)
        self.control.io_file_revive = str(direc / Path(self.control.io_file_revive).name)
        self.control.io_file_revcon = str(direc / Path(self.control.io_file_revcon).name)

        if getattr(self.control, "traj_calculate", False) or self.control.io_file_history:
            self.control.io_file_history = str(
                direc / Path(get_file_def("history", "HISTORY")).name)

        if self.control.io_file_historf:
            self.control.io_file_historf = str(direc / Path(self.control.io_file_historf).name)

        if getattr(self.control, "restart", "clean") != "clean" or self.control.io_file_revold:
            self.control.io_file_revold = str(
                direc / Path(get_file_def("revold", "REVOLD")).name)

        if getattr(self.control, "rdf_print", False):
            self.control.io_file_rdf = str(
                direc / Path(get_file_def("rdf", "RDFDAT")).name)

        if getattr(self.control, "correlation_observable", False):
            self.control.io_file_cor = str(
                direc / Path(get_file_def("cor", "COR")).name)

        if getattr(self.control, "currents_calculate", False):
            self.control.io_file_currents = str(
                direc / Path(get_file_def("currents", "CURRENTS")).name)

        if hasattr(self.control, "msdtmp") or self.control.io_file_msd:
            self.control.io_file_msd = str(
                direc / Path(get_file_def("msd", "MSDTMP")).name)

    @staticmethod
    def _update_file(direc: PathLike, in_file: PathLike, dest_name: OptPath = None) -> Path:
        """
        Redirect a `in_file` to a new `direc`tory.

        Parameters
        ----------
        direc : PathLike
            Directory to put as destination.
        in_file : PathLike
            File to redirect.
        dest_name : OptPath
            Name of file to write in directory. Default is `in_file`.

        Returns
        -------
        Path
            Path of file after redirection.
        """
        if dest_name is None:
            dest_name = in_file
        dest_name = Path(dest_name)

        out_file = direc / dest_name.name
        copy_file(in_file, out_file)
        return out_file

    def copy_input(self, direc: OptPath = None):
        """
        Copy input field, config, and TAB files to the working location.

        Parameters
        ----------
        direc : OptPath
            Directory to copy to. Default is `workdir`.
        """
        if direc is None:
            direc = self.workdir

        try:
            shutil.copy(self.field_file, direc)
        except shutil.SameFileError:
            pass

        if self.dest_config is None:
            self.config_file = self._update_file(direc, self.config_file)

        else:
            self.config_file = self._update_file(direc, self.config_file, self.dest_config)
        self.field_file = self._update_file(direc, self.field_file)

        if self.vdw_file:
            self.vdw_file = self._update_file(direc, self.vdw_file)
        if self.eam_file:
            self.eam_file = self._update_file(direc, self.eam_file)
        if self.bnd_file:
            self.bnd_file = self._update_file(direc, self.bnd_file)
        if self.ang_file:
            self.ang_file = self._update_file(direc, self.ang_file)
        if self.dih_file:
            self.dih_file = self._update_file(direc, self.dih_file)
        if self.inv_file:
            self.inv_file = self._update_file(direc, self.inv_file)

    def write(self,
              control: bool = True,
              config: bool = True,
              field: bool = True,
              prefix: str = '',
              suffix: str = ''):
        """
        Write necessary DLPoly input files to disc.

        Parameters
        ----------
        control : bool
            Whether to write control.
        config : bool
            Whether to write config.
        field : bool
            Whether to write field.
        prefix : str
            Prefix to add to file name(s).
        suffix : str
            Suffix to add to file name(s).
        """
        if control:
            self.control.write(prefix+self.control_file+suffix)
        if config and self.config:
            self.config.write(prefix+self.config_file+suffix)
        if field and self.field:
            self.field.write(prefix+self.field_file+suffix)

    def load_control(self,
                     source: OptPath = None,
                     quiet: Optional[bool] = None,
                     required: bool = False):
        """
        Load control file into class.

        Parameters
        ----------
        source : OptPath
            Source of control file. Default is `self.control_file`.
        quiet : Optional[bool]
            Whether to print warning if file not found.
            Default is `True` if `source` passed, else `False`.
        required : bool
            Whether to raise error if file not found. Default is `False`.

        Raises
        ------
        FileNotFoundError
            If `required` and `source` not found.
        """
        if quiet is None:  # If we haven't defined quiet or a source, should be quiet
            quiet = source is None

        if source is None:

            source = self.control_file

        source = Path(source)

        if source.is_file():
            if is_new_control(source):
                self.control = NewControl(source)
            else:
                self.control = Control(source).to_new()
            self.control_file = source
        elif required:
            raise FileNotFoundError(f"Required control file does not exist at {source}")
        elif not quiet:
            print(f"Unable to find file: {source.absolute()}")

    def load_file(self,
                  cls: Type,
                  source: OptPath = None,
                  quiet: Optional[bool] = None,
                  required: bool = False):
        """
        Load file based on class descriptor.

        Parameters
        ----------
        cls : Type
            Type of file being set.
            `cls` determines which `Control` argument is read/set.
        source : OptPath
            Source of file. Default is `self.{cls.__name__}_file`.
        quiet : Optional[bool]
            Whether to ``print`` warning if file not found.
            Default is `True` if `source` passed, else `False`.
        required : bool
            Whether to raise error if file not found. Default is `False`.

        Raises
        ------
        FileNotFoundError
            If `required` is ``True`` and `source` not found.
        """
        cls_name = cls.__name__.lower()
        fld_name = cls_name+"_file"
        if quiet is None:  # If we haven't defined quiet or a source, should be quiet
            quiet = source is None

        if source is None:
            source = getattr(self, fld_name)

        source = Path(source)
        if source.is_file():
            setattr(self, cls_name, cls(source))
            setattr(self, fld_name, source)
        elif required:
            raise FileNotFoundError(f"Required {cls_name} file does not exist at {source}")
        elif not quiet:
            print(f"Unable to find file: {source.absolute()}")

    def load_field(self, source: OptPath = None, quiet: bool = False,
                   required: bool = False):
        """
        Load field file into class.

        Parameters
        ----------
        source : OptPath
            Source of control file. Default is `self.control_file`.
        quiet : Optional[bool]
            Whether to print warning if file not found.
            Default is `True` if `source` passed, else `False`.
        required : bool
            Whether to raise error if file not found. Default is `False`.

        Raises
        ------
        FileNotFoundError
            If `required` is ``True`` and `source` not found.
        """
        self.load_file(Field, source, quiet, required)

    def load_config(self, source: OptPath = None, quiet: bool = False,
                    required: bool = False):
        """
        Load config file into class.

        Parameters
        ----------
        source : OptPath
            Source of control file. Default is `self.control_file`.
        quiet : Optional[bool]
            Whether to print warning if file not found.
            Default is `True` if `source` passed, else `False`.
        required : bool
            Whether to raise error if file not found. Default is `False`.

        Raises
        ------
        FileNotFoundError
            If `required` is ``True`` and `source` not found.
        """
        self.load_file(Config, source, quiet, required)

    def load_statis(self, source: OptPath = None, quiet: bool = False,
                    required: bool = False):
        """
        Load statis file into class.

        Parameters
        ----------
        source : OptPath
            Source of control file. Default is `self.control_file`.
        quiet : Optional[bool]
            Whether to print warning if file not found.
            Default is `True` if `source` passed, else `False`.
        required : bool
            Whether to raise error if file not found. Default is `False`.

        Raises
        ------
        FileNotFoundError
            If `required` is ``True`` and `source` not found.
        """
        self.load_file(Statis, source, quiet, required)

    def load_rdf(self, source: OptPath = None, quiet: bool = False,
                 required: bool = False):
        """
        Load statis file into class.

        Parameters
        ----------
        source : OptPath
            Source of control file. Default is `self.control_file`.
        quiet : Optional[bool]
            Whether to print warning if file not found.
            Default is `True` if `source` passed, else `False`.
        required : bool
            Whether to raise error if file not found. Default is `False`.

        Raises
        ------
        FileNotFoundError
            If `required` is ``True`` and `source` not found.
        """
        self.load_file(RDF, source, quiet, required)

    def load_msd(self, source: OptPath = None, quiet: bool = False,
                 required: bool = False):
        """
        Load msd file into class.

        Parameters
        ----------
        source : OptPath
            Source of control file. Default is `self.control_file`.
        quiet : Optional[bool]
            Whether to print warning if file not found.
            Default is `True` if `source` passed, else `False`.
        required : bool
            Whether to raise error if file not found. Default is `False`.

        Raises
        ------
        FileNotFoundError
            If `required` is ``True`` and `source` not found.
        """
        self.load_file(MSD, source, quiet, required)

    def load_correlations(self, source: OptPath = None, quiet: bool = False,
                          required: bool = False):
        """
        Load correlations file into class.

        Parameters
        ----------
        source : OptPath
            Source of control file. Default is `self.control_file`.
        quiet : Optional[bool]
            Whether to print warning if file not found.
            Default is `True` if `source` passed, else `False`.
        required : bool
            Whether to raise error if file not found. Default is `False`.

        Raises
        ------
        FileNotFoundError
            If `required` is ``True`` and `source` not found.
        """
        self.load_file(Correlations, source, quiet, required)

    def load_currents(self, source: OptPath = None, quiet: bool = False,
                      required: bool = False):
        """
        Load currents file into class.

        Parameters
        ----------
        source : OptPath
            Source of control file. Default is `self.control_file`.
        quiet : Optional[bool]
            Whether to print warning if file not found.
            Default is `True` if `source` passed, else `False`.
        required : bool
            Whether to raise error if file not found. Default is `False`.

        Raises
        ------
        FileNotFoundError
            If `required` is ``True`` and `source` not found.
        """
        self.load_file(Currents, source, quiet, required)

    @property
    def exe(self) -> Path:
        """
        Executable name to be used to run DLPOLY.
        """
        return self._exe

    @exe.setter
    def exe(self, exe: PathLike):
        """
        Set the executable name.

        Checks in order:
           - `exe` as Path to executable
           - Environment variable (``DLP_EXE``)
           - ``which`` `exe`
           - `exe` in current folder.

        Tries to run it as DLPoly.

        Parameters
        ----------
        exe : PathLike
           Executable to try.

        Raises
        ------
        FileNotFound
            If `exe` is invalid or DLPoly can't be found.
        """
        if exe is not None and (exepath := Path(exe)).exists():
            self._exe = exepath
        else:
            # user has not provided exe name
            exe = exe or "DLPOLY.Z"

            if exepath := os.environ.get("DLP_EXE", None):
                self._exe = Path(exepath)
            elif exepath := shutil.which(exe):
                self._exe = Path(exepath)
            else:  # Assume in folder
                self._exe = Path(exe)

        try:
            with subprocess.Popen([self.exe, '-V'],
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT) as proc:
                result, _ = proc.communicate()

            if "DL_POLY" not in result.decode("utf-8"):
                print(f"{self.exe.absolute()} is not DLPoly, run may not work")
        except FileNotFoundError:
            print(f"{self.exe.absolute()} does not exist, run may not work")

    @property
    def workdir(self):
        """
        Folder in which inputs are copied and outputs are written to.
        """
        return self._workdir

    @workdir.setter
    def workdir(self, workdir: PathLike):
        self._workdir = Path(workdir) if workdir else None

    def _clear_caches(self):
        """
        Clear cached output files.
        """
        for outfile in self.OUTPUT_FILES:
            try:
                delattr(self, outfile)
            except AttributeError:
                pass

    def run(self, *,
            executable: OptPath = None,
            numProcs: int = 1,
            mpi: str = 'mpirun -n',
            outputFile: OptPath = None,
            load_outputs: bool = False,
            modules: Sequence[str] = (),
            pre_run: str = "",
            post_run: str = "",
            run_check: int = 30,
            debug: bool = False) -> int:
        """
        Perform a DLPoly run with the current setup.

        Parameters
        ----------
        executable : OptPath
            Executable to run DLPoly.
        numProcs : int
            Number of processors to run calculation (if MPI).
        mpi : str
            Shell command to launch MPI.
        outputFile : OptPath
            File to write log to.
        load_outputs : bool
            Delete stored outputs to force loading of new ones.

        Returns
        -------
        int
            Returned error code from job.

        Other Parameters
        ----------------
        modules : Sequence[str]
            Modules to load on a linux system for running.
        pre_run : str
            Shell commands to run prior to executing DLPoly.
        post_run : str
            Shell commands to run after executing DLPoly.
        run_check : int, UNUSED
            Timeout for shell run to ensure DLPoly has not failed.
        debug : bool
            Print stdout and stderr of DLPoly process to screen.

        Raises
        ------
        SystemError
            If on Windows system and attempting to use `modules`,
            `pre_run` or `post_run`.
        """
        # If we're defaulting to default name
        # Get last runname + 1 for this one
        if self.workdir is None:
            self.workdir = next_file(self.default_name)

        if not self.workdir.exists():
            self.workdir.mkdir(parents=True)
        else:
            print(f"Folder {self.workdir} exists, over-writing.")

        dlpexe = executable if executable is not None else self.exe

        control_file = self.workdir / self.control_file.name
        self.copy_input()
        self.redir_output()
        self.control.write(control_file)

        if outputFile is None:
            outputFile = next_file(self.control.io_file_output)

        if is_mpi():
            from mpi4py.MPI import COMM_SELF, COMM_WORLD
            from mpi4py.MPI import Exception as MPIException

            error_code = 0
            if COMM_WORLD.Get_rank() == 0:
                try:
                    COMM_SELF.Spawn(dlpexe,
                                    [f"-c {control_file}", f"-o {outputFile}"],
                                    maxprocs=numProcs)
                except MPIException as err:
                    error_code = err.Get_error_code()

            error_code = COMM_WORLD.Bcast(error_code, 0)

        else:
            run_command = f"{dlpexe} -c {control_file} -o {outputFile}"

            if numProcs > 1:
                run_command = f"{mpi} {numProcs} {run_command}"

            if modules:
                pre_run = f"module purge && module load {' '.join(modules)}\n{pre_run}"

            if pre_run or post_run:
                if os.name == "nt":
                    raise SystemError("Script file runs cannot run on Windows,"
                                      "Cannot use `pre_run` or `post_run` or `modules`")

                script_file = self.workdir / "env.sh"
                with open(script_file, "w", encoding="utf-8") as out_file:
                    print(pre_run, file=out_file)
                    print(run_command, file=out_file)
                    print(post_run, file=out_file)
                run_command = f"sh {script_file}"

            with subprocess.Popen(shlex.split(run_command),
                                  stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT) as proc:

                if debug:
                    if proc.stdout is not None:
                        print(f"STDOUT: \n{proc.stdout.read().decode('utf-8')}")
                    if proc.stderr is not None:
                        print(f"STDERR: \n{proc.stderr.read().decode('utf-8')}")
                proc.communicate()
                error_code = proc.returncode

        # Clear cached output files
        if load_outputs and not error_code:
            self._clear_caches()

        return error_code


def main():
    """
    Run the main program from command line arguments.
    """
    arg_list = get_command_args()
    dlp_run = DLPoly(control=arg_list.control, config=arg_list.config,
                     field=arg_list.field, statis=arg_list.statis,
                     workdir=arg_list.workdir)
    dlp_run.run(executable=arg_list.dlp)


if __name__ == "__main__":
    main()
