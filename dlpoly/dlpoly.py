""" Module containing main DLPOLY class.
"""

import subprocess
from pathlib import Path
import os
import shutil
from .new_control import (NewControl, is_new_control)
from .control import Control
from .config import Config
from .field import Field
from .statis import Statis
from .rdf import RDF
from .msd import MSD
from .cli import get_command_args
from .utility import (copy_file, next_file, is_mpi, file_get_set_factory)
from .correlations import Correlations
from .currents import Currents


class DLPoly:
    """ Main class of a DLPOLY runnable set of instructions """
    __version__ = "5.0"  # which version of dlpoly supports

    def __init__(self, control=None, config=None, field=None, statis=None, output=None,
                 dest_config=None, rdf=None, msd=None, correlations=None, workdir=None,
                 default_name=None, exe=None):
        # Default to having a control
        self.control = NewControl()
        self.config = None
        self.dest_config = dest_config
        self.default_name = default_name
        self.field = None
        self.statis = None
        self.msd = None
        self.rdf = None
        self.correlations = None
        self.currents = None
        self.exe = exe
        self.workdir = workdir

        if default_name is None:
            self.default_name = "dlprun"

        if control is not None:
            self.load_control(control)
        if config is not None:
            self.load_config(config)
        if field is not None:
            self.load_field(field)
        if statis is not None:
            self.load_statis(statis)
        if rdf is not None:
            self.load_rdf(rdf)
        if msd is not None:
            self.load_msd(msd)
        if correlations is not None:
            self.load_correlations(correlations)

        # Override output
        if output is not None:
            self.control.io_file_output = output

    control_file = property(*file_get_set_factory("control"))
    field_file = property(*file_get_set_factory("field"))
    vdw_file = property(*file_get_set_factory("tabvdw"))
    eam_file = property(*file_get_set_factory("tabeam"))
    config_file = property(*file_get_set_factory("config"))
    statis_file = property(*file_get_set_factory("statis"))
    rdf_file = property(*file_get_set_factory("rdf"))
    msd_file = property(*file_get_set_factory("msd"))
    correlations_file = property(*file_get_set_factory("cor"))
    currents_file = property(*file_get_set_factory("currents"))

    def redir_output(self, direc=None):
        """ Redirect output to direc and update self for later parsing """

        def get_file_def(filetype, default):
            """ Get default filename if filename not specified """
            if path := getattr(self.control, filetype, False):
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
                direc / Path(get_file_def("io_file_history", "HISTORY")).name)

        if self.control.io_file_historf:
            self.control.io_file_historf = str(direc / Path(self.control.io_file_historf).name)

        if getattr(self.control, "restart", "clean") != "clean" or self.control.io_file_revold:
            self.control.io_file_revold = str(
                direc / Path(get_file_def("io_file_revold", "REVOLD")).name)

        if getattr(self.control, "rdf_print", False):
            self.control.io_file_rdf = str(
                direc / Path(get_file_def("io_file_rdf", "RDFDAT")).name)

        if getattr(self.control, "correlation_observable", False):
            self.control.io_file_cor = str(
                direc / Path(get_file_def("io_file_cor", "COR")).name)

        if hasattr(self.control, "msdtmp") or self.control.io_file_msd:
            self.control.io_file_msd = str(
                direc / Path(get_file_def("io_file_msd", "MSDTMP")).name)

    @staticmethod
    def _update_file(direc, in_file, dest_name=None):
        if dest_name is None:
            dest_name = in_file
        dest_name = Path(dest_name)

        out_file = direc / dest_name.name
        copy_file(in_file, out_file)
        return out_file

    def copy_input(self, direc=None):
        """ Copy input field and config to the working location """
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
        if self.control.io_file_tabbnd:
            self.control.io_file_tabbnd = self._update_file(direc, self.control.io_file_tabbnd)
        if self.control.io_file_tabang:
            self.control.io_file_tabang = self._update_file(direc, self.control.io_file_tabang)
        if self.control.io_file_tabdih:
            self.control.io_file_tabdih = self._update_file(direc, self.control.io_file_tabdih)
        if self.control.io_file_tabinv:
            self.control.io_file_tabinv = self._update_file(direc, self.control.io_file_tabinv)

    def write(self, control=True, config=True, field=True, prefix='', suffix=''):
        """ Write each of the components to file """
        if control:
            self.control.write(prefix+self.control_file+suffix)
        if config and self.config:
            self.config.write(prefix+self.config_file+suffix)
        if field and self.field:
            self.field.write(prefix+self.field_file+suffix)

    def load_control(self, source=None):
        """ Load control file into class """
        if source is None:
            source = self.control_file

        source = Path(source)

        if source.is_file():
            if is_new_control(source):
                self.control = NewControl(source)
            else:
                self.control = Control(source).to_new()
            self.control_file = source
        else:
            print(f"Unable to find file: {source.absolute()}")

    def load_field(self, source=None):
        """ Load field file into class """
        if source is None:
            source = self.field_file

        source = Path(source)

        if source.is_file():
            self.field = Field(source)
            self.field_file = source
        else:
            print(f"Unable to find file: {source.absolute()}")

    def load_config(self, source=None):
        """ Load config file into class """
        if source is None:
            source = self.config_file

        source = Path(source)

        if source.is_file():
            self.config = Config(source)
            self.config_file = source
        else:
            print(f"Unable to find file: {source.absolute()}")

    def load_statis(self, source=None):
        """ Load statis file into class """
        if source is None:
            source = self.statis_file

        source = Path(source)

        if source.is_file():
            self.statis = Statis(source)
            self.statis_file = source
        else:
            print(f"Unable to find file: {source.absolute()}")

    def load_rdf(self, source=None):
        """ Load statis file into class """
        if source is None:
            source = self.rdf_file

        source = Path(source)

        if source.is_file():
            self.rdf = RDF(source)
            self.rdf_file = source
        else:
            print(f"Unable to find file: {source.absolute()}")

    def load_msd(self, source=None):
        """Load msd file into class"""
        if source is None:
            source = self.msd_file

        source = Path(source)

        if source.is_file():
            self.msd = MSD(source)
            self.msd_file = source
        else:
            print(f"Unable to find file: {source.absolute()}")

    def load_correlations(self, source=None):
        """ Load correlations file into class """
        if source is None:
            source = self.correlations_file

        source = Path(source)

        if source.is_file():
            self.correlations = Correlations(source)
            self.correlations_file = source
        else:
            print(f"Unable to find file: {source.absolute()}")

    def load_currents(self, source=None):
        """Load currents file into class"""
        if source is None:
            source = self.currents_file

        source = Path(source)

        if source.is_file():
            self.currents = Currents(source)
            self.currents_file = source
        else:
            print(f"Unable to find file: {source.absolute()}")

    @property
    def exe(self):
        """ executable name to be used to run DLPOLY"""
        return self._exe

    @exe.setter
    def exe(self, exe):
        """ set the executable name"""
        if exe is not None and (exepath := Path(exe)).exists():
            self._exe = exepath
        else:
            if exe is None:  # user has not provided exe name
                exe = "DLPOLY.Z"

            if exepath := os.environ.get("DLP_EXE", None):
                self._exe = Path(exepath)
            elif exepath := shutil.which(exe):
                self._exe = Path(exepath)
            else:  # Assume in folder
                self._exe = Path(exe)

        try:
            proc = subprocess.Popen([self.exe, '-h'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)
            result, _ = proc.communicate()
            if f"Usage: {self.exe}" not in result.decode("utf-8"):
                print(f"{self.exe.absolute()} is not DLPoly, run may not work")
        except FileNotFoundError:
            print(f"{self.exe.absolute()} does not exist, run may not work")

    @property
    def workdir(self):
        """ Directory in which to do work """
        return self._workdir

    @workdir.setter
    def workdir(self, workdir):
        if workdir is None:
            self._workdir = None
        else:
            self._workdir = Path(workdir)

    def run(self, executable=None, modules=(),
            numProcs=1, mpi='mpirun -n', outputFile=None,
            pre_run="", post_run="", run_check=30, debug=False):
        """ this is very primitive one allowing the checking
        for the existence of files and alteration of control parameters """

        # If we're defaulting to default name
        # Get last runname + 1 for this one
        if self.workdir is None:
            self.workdir = next_file(self.default_name)

        if not self.workdir.exists():
            self.workdir.mkdir(parents=True)
        else:
            print(f"Folder {self.workdir} exists, over-writing.")

        dlpexe = executable
        if executable is None:
            dlpexe = self.exe

        control_file = self.workdir / self.control_file.name
        self.copy_input()
        self.redir_output()
        self.control.write(control_file)

        if outputFile is None:
            outputFile = next_file(self.control.io_file_output)

        if is_mpi():
            from mpi4py.MPI import (COMM_WORLD, COMM_SELF)
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

            if pre_run or post_run:  # Windows will not work here
                script_file = self.workdir / "env.sh"
                with open(script_file, "w", encoding="utf-8") as out_file:
                    out_file.write(f"{pre_run}\n")
                    out_file.write(f"{run_command}\n")
                    out_file.write(f"{post_run}\n")
                run_command = f"sh {script_file}"

            proc = subprocess.Popen(run_command.split(),
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)

            if (debug):
                if proc.stdout is not None:
                    print("STDOUT: \n{}".format(proc.stdout.read().decode("utf-8")))
                if proc.stderr is not None:
                    print("STDERR: \n{}".format(proc.stderr.read().decode("utf-8")))

            _, error_code = proc.communicate()

        return error_code


def main():
    """ Run the main program """
    arg_list = get_command_args()
    dlp_run = DLPoly(control=arg_list.control, config=arg_list.config,
                     field=arg_list.field, statis=arg_list.statis,
                     workdir=arg_list.workdir)
    dlp_run.run(executable=arg_list.dlp)


if __name__ == "__main__":
    main()
