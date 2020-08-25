""" Module containing main DLPOLY class.
"""

import subprocess
import os.path
import os
import shutil
from .control import Control
from .config import Config
from .field import Field
from .statis import Statis
from .rdf import rdf
from .cli import get_command_args
from .utility import copy_file


class DLPoly:
    """ Main class of a DLPOLY runnable set of instructions """
    __version__ = "4.10"  # which version of dlpoly supports

    def __init__(self, control=None, config=None, field=None, statis=None, output=None,
                 destconfig=None, rdf=None, workdir=None):
        # Default to having a control
        self.control = Control()
        self.config = None
        self.destconfig = destconfig
        self.field = None
        self.statis = None
        self.rdf = None
        self.workdir = workdir

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
            self.control.io.output = output

    def redir_output(self, direc=None):
        """ Redirect output to direc and update self for later parsing """
        if direc is None:
            direc = self.workdir

        # Set the path to be: direc/filename, stripping off all unnecessary pathing
        self.control.io.statis = os.path.abspath(os.path.join(direc, os.path.basename(self.control.io.statis)))
        self.control.io.output = os.path.abspath(os.path.join(direc, os.path.basename(self.control.io.output)))
        self.control.io.revive = os.path.abspath(os.path.join(direc, os.path.basename(self.control.io.revive)))
        self.control.io.revcon = os.path.abspath(os.path.join(direc, os.path.basename(self.control.io.revcon)))

        if hasattr(self.control, 'traj') and not self.control.io.history:
            self.control.io.history = 'HISTORY'
        if self.control.io.history:
            self.control.io.history = os.path.abspath(
                os.path.join(direc, os.path.basename(self.control.io.history)))

        if self.control.io.historf:
            self.control.io.historf = os.path.abspath(
                os.path.join(direc, os.path.basename(self.control.io.historf)))

        if hasattr(self.control, 'restart') and not self.control.io.revold:
            self.control.io.revold = 'REVOLD'
        if self.control.io.revold:
            self.control.io.revold = os.path.abspath(
                os.path.join(direc, os.path.basename(self.control.io.revold)))

        if self.control.print.rdf and not self.control.io.rdf:
            self.control.io.rdf = 'RDFDAT'
        if self.control.io.rdf:
            self.control.io.rdf = os.path.abspath(
                os.path.join(direc, os.path.basename(self.control.io.rdf)))

        if hasattr(self.control, 'msdtmp') and not self.control.io.msd:
            self.control.io.msd = 'MSDTMP'
        if self.control.io.msd:
            self.control.io.msd = os.path.abspath(
                os.path.join(direc, os.path.basename(self.control.io.msd)))

    @staticmethod
    def _update_file(direc, file):
        copy_file(file, direc)
        return os.path.join(direc, os.path.basename(file))

    def copy_input(self, direc=None):
        """ Copy input field and config to the working location """
        if direc is None:
            direc = self.workdir
        try:
            shutil.copy(self.fieldFile, direc)
        except shutil.SameFileError:
            pass

        if self.destconfig is None:
            self.configFile = self._update_file(direc, self.configFile)

        else:
            self.configFile = self._update_file(direc, self.destconfig)

        self.fieldFile = self._update_file(direc, self.fieldFile)

        if self.vdwFile:
            self.vdwFile = self._update_file(direc, self.vdwFile)
        if self.eamFile:
            self.eamFile = self._update_file(direc, self.eamFile)
        if self.control.io.tabbnd:
            self.control.io.tabbnd = self._update_file(direc, self.control.io.tabbnd)
        if self.control.io.tabang:
            self.control.io.tabang = self._update_file(direc, self.control.io.tabang)
        if self.control.io.tabdih:
            self.control.io.tabdih = self._update_file(direc, self.control.io.tabdih)
        if self.control.io.tabinv:
            self.control.io.tabinv = self._update_file(direc, self.control.io.tabinv)

    def write(self, control=True, config=True, field=True, prefix='', suffix=''):
        """ Write each of the components to file """
        if control:
            self.control.write_old(prefix+self.controlFile+suffix)
        if config and self.config:
            self.config.write(prefix+self.configFile+suffix)
        if field and self.field:
            self.field.write(prefix+self.fieldFile+suffix)

    def load_control(self, source=None):
        """ Load control file into class """
        if source is None:
            source = self.controlFile
        if os.path.isfile(source):
            self.control = Control(source)
            self.controlFile = source
        else:
            print("Unable to find file: {}".format(source))

    def load_field(self, source=None):
        """ Load field file into class """
        if source is None:
            source = self.fieldFile
        if os.path.isfile(source):
            self.field = Field(source)
            self.fieldFile = source
        else:
            print("Unable to find file: {}".format(source))

    def load_config(self, source=None):
        """ Load config file into class """
        if source is None:
            source = self.configFile
        if os.path.isfile(source):
            self.config = Config(source)
            self.configFile = source
        else:
            print("Unable to find file: {}".format(source))

    def load_statis(self, source=None):
        """ Load statis file into class """
        if source is None:
            source = self.statisFile
        if os.path.isfile(source):
            self.statis = Statis(source)
            self.statisFile = source
        else:
            print("Unable to find file: {}".format(source))

    def load_rdf(self, source=None):
        """ Load statis file into class """
        if source is None:
            source = self.rdfFile
        if os.path.isfile(source):
            self.rdf = rdf(source)
            self.rdfFile = source
        else:
            print("Unable to find file: {}".format(source))

    @property
    def controlFile(self):
        """ Path to control file """
        return self.control.io.control

    @controlFile.setter
    def controlFile(self, control):
        self.control.io.control = control

    @property
    def fieldFile(self):
        """ Path to field file """
        return self.control.io.field

    @property
    def vdwFile(self):
        """ Path to TABLE for vdw file """
        return self.control.io.tabvdw

    @property
    def eamFile(self):
        """ Path to TABEAM for eam file """
        return self.control.io.tabeam

    @controlFile.setter
    def controlFile(self, control):
        self.control.io.control = control

    @fieldFile.setter
    def fieldFile(self, field):
        self.control.io.field = field

    @vdwFile.setter
    def vdwFile(self, vdw):
        self.control.io.tabvdw = vdw

    @eamFile.setter
    def eamFile(self, eam):
        self.control.io.tabeam = eam

    @property
    def configFile(self):
        """ Path to config file """
        return self.control.io.config

    @configFile.setter
    def configFile(self, config):
        self.control.io.config = config

    @property
    def statisFile(self):
        """ Path to statis file """
        return self.control.io.statis

    @property
    def rdfFile(self):
        """ Path to rdf file """
        return self.control.io.rdfFile

    @rdfFile.setter
    def rdfFile(self, rdf):
        self.control.io.rdfFile = rdf

    @statisFile.setter
    def statisFile(self, statis):
        self.control.io.statis = statis

    def run(self, executable=None, modules=(),
            numProcs=1, mpi='mpirun -n', outputFile=None):
        """ this is very primitive one allowing the checking
        for the existence of files and alteration of control parameters """

        try:
            os.mkdir(self.workdir)
        except FileExistsError:
            print("Folder {} exists, over-writing.".format(self.workdir))

        dlpexe = executable
        if executable is None:
            try:
                dlpexe = os.environ["DLP_EXE"]
            except KeyError:
                dlpexe = "DLPOLY.Z"

        prefix = self.workdir+"/"
        controlFile = prefix+os.path.basename(self.controlFile)
        self.copy_input()
        self.redir_output()
        self.control.write(controlFile)

        if outputFile is None:
            outputFile = self.control.io.output
        if numProcs > 1:
            runCommand = "{0:s} {1:d} {2:s} -c {3:s} -o {4:s}".format(mpi,
                                                                      numProcs,
                                                                      dlpexe,
                                                                      controlFile,
                                                                      outputFile)
        else:
            runCommand = "{0:s} -c {1:s} -o {2:s}".format(dlpexe, controlFile, outputFile)

        if modules:
            loadMods = "module purge && module load " + modules
            with open("env.sh", 'w') as outFile:
                outFile.write(loadMods+"\n")
                outFile.write(runCommand)
                cmd = ['sh ./env.sh']
        else:
            cmd = [runCommand]

        errorCode = subprocess.call(cmd, shell=True)
        return errorCode


def main():
    """ Run the main program """
    argList = get_command_args()
    dlPoly = DLPoly(control=argList.control, config=argList.config,
                    field=argList.field, statis=argList.statis,
                    workdir=argList.workdir)
    dlPoly.run(executable=argList.dlp)


if __name__ == "__main__":
    main()
