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
from .rdf import rdf
from .cli import get_command_args
from .utility import (copy_file, next_file, is_mpi)


class DLPoly:
    """ Main class of a DLPOLY runnable set of instructions """
    __version__ = "4.10"  # which version of dlpoly supports

    def __init__(self, control=None, config=None, field=None, statis=None, output=None,
                 dest_config=None, rdf=None, workdir=None, default_name=None, exe=None):
        # Default to having a control
        self.control = NewControl()
        self.config = None
        self.dest_config = dest_config
        self.default_name = default_name
        self.field = None
        self.statis = None
        self.rdf = None
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

        # Override output
        if output is not None:
            self.control.io_file_output = output

    def redir_output(self, direc=None):
        """ Redirect output to direc and update self for later parsing """
        if direc is None:
            direc = self.workdir.absolute()
        else:
            direc = Path(direc).absolute()

        # Set the path to be: direc/filename, stripping off all unnecessary pathing
        self.control.io_file_statis = str(direc / self.statisFile.name)
        self.control.io_file_revive = str(direc / Path(self.control.io_file_revive).name)
        self.control.io_file_revcon = str(direc / Path(self.control.io_file_revcon).name)

        if hasattr(self.control, 'traj') and not self.control.io_file_history:
            self.control.io_file_history = 'HISTORY'
        if self.control.io_file_history:
            self.control.io_file_history = str(direc / Path(self.control.io_file_history).name)

        if self.control.io_file_historf:
            self.control.io_file_historf = str(direc / Path(self.control.io_file_historf).name)

        if hasattr(self.control, 'restart') and not self.control.io_file_revold:
            self.control.io_file_revold = 'REVOLD'
        if self.control.io_file_revold:
            self.control.io_file_revold = str(direc / Path(self.control.io_file_revold).name)

        if hasattr(self.control, 'rdf_print') and \
           self.control.rdf_print and \
           not self.control.io_file_rdf:
            self.control.io_file_rdf = 'RDFDAT'
        if self.control.io_file_rdf:
            self.control.io_file_rdf = str(direc / Path(self.control.io_file_rdf).name)

        if hasattr(self.control, 'msdtmp') and not self.control.io_file_msd:
            self.control.io_file_msd = 'MSDTMP'
        if self.control.io_file_msd:
            self.control.io_file_msd = str(direc / Path(self.control.io_file_msd).name)

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
            shutil.copy(self.fieldFile, direc)
        except shutil.SameFileError:
            pass

        if self.dest_config is None:
            self.configFile = self._update_file(direc, self.configFile)

        else:
            self.configFile = self._update_file(direc, self.configFile, self.dest_config)

        self.fieldFile = self._update_file(direc, self.fieldFile)

        if self.vdwFile:
            self.vdwFile = self._update_file(direc, self.vdwFile)
        if self.eamFile:
            self.eamFile = self._update_file(direc, self.eamFile)
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
            self.control.write(prefix+self.controlFile+suffix)
        if config and self.config:
            self.config.write(prefix+self.configFile+suffix)
        if field and self.field:
            self.field.write(prefix+self.fieldFile+suffix)

    def load_control(self, source=None):
        """ Load control file into class """
        if source is None:
            source = self.controlFile

        source = Path(source)

        if source.is_file():
            if is_new_control(source):
                self.control = NewControl(source)
            else:
                self.control = Control(source).to_new()
            self.controlFile = source
        else:
            print(f"Unable to find file: {source.absolute()}")

    def load_field(self, source=None):
        """ Load field file into class """
        if source is None:
            source = self.fieldFile

        source = Path(source)

        if source.is_file():
            self.field = Field(source)
            self.fieldFile = source
        else:
            print(f"Unable to find file: {source.absolute()}")

    def load_config(self, source=None):
        """ Load config file into class """
        if source is None:
            source = self.configFile

        source = Path(source)

        if source.is_file():
            self.config = Config(source)
            self.configFile = source
        else:
            print(f"Unable to find file: {source.absolute()}")

    def load_statis(self, source=None):
        """ Load statis file into class """
        if source is None:
            source = self.statisFile

        source = Path(source)

        if source.is_file():
            self.statis = Statis(source)
            self.statisFile = source
        else:
            print(f"Unable to find file: {source.absolute()}")

    def load_rdf(self, source=None):
        """ Load statis file into class """
        if source is None:
            source = self.rdfFile

        source = Path(source)

        if source.is_file():
            self.rdf = rdf(source)
            self.rdfFile = source
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
            proc = subprocess.Popen([exe, '-h'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            result, _ = proc.communicate()
            if f"Usage: {os.path.basename(exe)}" not in result:
                print(f"{exe} is not DLPoly, run may not work")
        except FileNotFoundError:
            print(f"{exe} does not exist, run may not work")

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

    @property
    def controlFile(self):
        """ Path to control file """
        return Path(self.control.io_file_control)

    @controlFile.setter
    def controlFile(self, control):
        self.control.io_file_control = str(control)

    @property
    def fieldFile(self):
        """ Path to field file """
        return Path(self.control.io_file_field)

    @fieldFile.setter
    def fieldFile(self, field):
        self.control.io_file_field = str(field)

    @property
    def vdwFile(self):
        """ Path to TABLE for vdw file """
        return Path(self.control.io_file_tabvdw)

    @vdwFile.setter
    def vdwFile(self, vdw):
        self.control.io_file_tabvdw = str(vdw)

    @property
    def eamFile(self):
        """ Path to TABEAM for eam file """
        return Path(self.control.io_file_tabeam)

    @eamFile.setter
    def eamFile(self, eam):
        self.control.io_file_tabeam = str(eam)

    @property
    def configFile(self):
        """ Path to config file """
        return Path(self.control.io_file_config)

    @configFile.setter
    def configFile(self, config):
        self.control.io_file_config = str(config)

    @property
    def statisFile(self):
        """ Path to statis file """
        return Path(self.control.io_file_statis)

    @statisFile.setter
    def statisFile(self, statis):
        self.control.io_file_statis = str(statis)

    @property
    def rdfFile(self):
        """ Path to rdf file """
        return Path(self.control.io_file_rdfFile)

    @rdfFile.setter
    def rdfFile(self, rdf):
        self.control.io_file_rdfFile = str(rdf)

    def run(self, executable=None, modules=(),
            numProcs=1, mpi='mpirun -n', outputFile=None,
            RUN_CHECK=15):
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

        control_file = self.workdir / self.controlFile.name
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
                with open("env.sh", 'w') as out_file:
                    out_file.write(f"module purge && module load {' '.join(modules)}\n")
                    out_file.write(run_command)
                cmd = ['sh', './env.sh']
            else:
                cmd = run_command.split()

            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            proc.wait(RUN_CHECK)
            if not Path(outputFile).is_file():  # Job not started yet
                proc.kill()
                raise RuntimeError("DLPoly failing to start, output ({outputFile}) not found after {RUN_CHECK}s")

            error_code = proc.wait()

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
