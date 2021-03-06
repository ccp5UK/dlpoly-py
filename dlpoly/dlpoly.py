"""
Module containing main DLPOLY class
"""

import subprocess
import os.path
import os
import shutil
from dlpoly.control import Control
from dlpoly.config import Config
from dlpoly.field import Field
from dlpoly.statis import Statis
from dlpoly.cli import get_command_args


class DLPoly:
    """ Main class of a DLPOLY runnable set of instructions """
    __version__ = "4.10"  # which version of dlpoly supports

    def __init__(self, control=None, config=None, field=None, statis=None, output=None, workdir=None):
        # Default to having a control
        self.control = Control()
        self.config = None
        self.field = None
        self.statis = None
        self.workdir = workdir

        if control is not None:
            self.load_control(control)
        if config is not None:
            self.load_config(config)
        if field is not None:
            self.load_field(field)
        if statis is not None:
            self.load_statis(statis)

        # Override output
        self.control.io.output = output

    def redir_output(self, direc=None):
        """ Redirect output to direc and update self for later parsing """
        if direc is None:
            direc = self.workdir

        # Set the path to be: direc/filename, stripping off all unnecessary pathing
        self.control.io.outstat = os.path.abspath(os.path.join(direc, os.path.basename(self.control.io.outstat)))
        self.control.io.history = os.path.abspath(os.path.join(direc, os.path.basename(self.control.io.history)))
        self.control.io.historf = os.path.abspath(os.path.join(direc, os.path.basename(self.control.io.historf)))
        self.control.io.output = os.path.abspath(os.path.join(direc, os.path.basename(self.control.io.output)))
        self.control.io.revive = os.path.abspath(os.path.join(direc, os.path.basename(self.control.io.revive)))
        self.control.io.revcon = os.path.abspath(os.path.join(direc, os.path.basename(self.control.io.revcon)))
        self.control.io.revold = os.path.abspath(os.path.join(direc, os.path.basename(self.control.io.revold)))

    def copy_input(self, direc=None):
        """ Copy input field and config to the working location """
        if direc is None:
            direc = self.workdir
        shutil.copy(self.fieldFile, direc)
        shutil.copy(self.configFile, direc)
        self.fieldFile = os.path.join(direc, os.path.basename(self.fieldFile))
        self.configFile = os.path.join(direc, os.path.basename(self.configFile))

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
            self.config = Statis(source)
            self.statisFile = source
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

    @controlFile.setter
    def controlFile(self, control):
        self.control.io.control = control

    @fieldFile.setter
    def fieldFile(self, field):
        self.control.io.field = field

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
        return self.control.io.outstats

    @statisFile.setter
    def statisFile(self, statis):
        self.control.io.outstats = statis

    def run(self, executable="DLPOLY.Z", modules=(),
            numProcs=1, mpi='mpirun -n', outputFile=None):
        """ this is very primitive one allowing the checking
        for the existence of files and alteration of control parameters """

        try:
            os.mkdir(self.workdir)
        except FileExistsError:
            print("Folder {} exists, over-writing.".format(self.workdir))

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
                                                                      executable,
                                                                      controlFile,
                                                                      outputFile)
        else:
            runCommand = "{0:s} -c {1:s} -o {2:s}".format(executable, controlFile, outputFile)

        if modules:
            loadMods = "module purge && module load " + modules
            with open("env.sh", 'w') as outFile:
                outFile.write(loadMods+"\n")
                outFile.write(runCommand)
                cmd = ['sh ./env.sh']
        else:
            cmd = [runCommand]
        print(cmd)
        subprocess.call(cmd, shell=True)


def main():
    """ Run the main program """
    argList = get_command_args()
    dlPoly = DLPoly(control=argList.control, config=argList.config,
                    field=argList.field, statis=argList.statis,
                    workdir=argList.workdir)
    dlPoly.run(executable=argList.dlp)


if __name__ == "__main__":
    main()
