"""
Module containing main DLPOLY class
"""

import subprocess
import os.path
from control import Control
from config import Config
from field import Field
from cli import get_command_args

class DLPoly:
    """ Main class of a DLPOLY runnable set of instructions """
    def __init__(self, control=None, config=None, field=None, statis=None):
        if control is not None:
            self.controlFile = control
            self.load_control()
        else:
            # Default to having a control
            self.control = Control()
        if config is not None:
            self.configFile = config
            self.load_config()
        if field is not None:
            self.fieldFile = field
            self.load_field()
        if statis is not None:
            self.statisFile = statis
            self.load_statis()

    def load_control(self, source=None):
        """ Load control file into class """
        if source is None:
            source = self.controlFile
        if os.path.isfile(source):
            self.control = Control(source)
        else:
            print("Unable to find file: {}".format(source))


    def load_field(self, source=None):
        """ Load field file into class """
        if source is None:
            source = self.fieldFile
        if os.path.isfile(source):
            self.field = Field(source)
        else:
            print("Unable to find file: {}".format(source))

    def load_config(self, source=None):
        """ Load config file into class """
        if source is None:
            source = self.configFile
        if os.path.isfile(source):
            self.config = Config(source)
        else:
            print("Unable to find file: {}".format(source))

    def load_statis(self, source=None):
        """ Load statis file into class """
        if source is None:
            source = self.statisFile
        if os.path.isfile(source):
            self.config = Statis(source)
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


    def run(self, executable="DLPOLY.Z", modules=(), numProcs=1, mpi='mpirun -n'):
        """ this is very primitive one allowing the checking
        for the existence of files and alteration of control parameters """

        if numProcs > 1:
            runCommand = "{0:s} {1:d} {2:s} {3:s}".format(mpi, numProcs, executable, self.controlFile)
        else:
            runCommand = "{0:s} {1:s}".format(executable, self.controlFile)

        if modules:
            loadMods = "module purge && module load " + modules
            with open("env.sh", 'w') as outFile:
                outFile.write(loadMods+"\n")
                outFile.write(runCommand)
                cmd = ['sh ./env.sh']
        else:
            cmd = [runCommand]
        subprocess.call(cmd, shell=True)

if __name__ == "__main__":
    argList = get_command_args()
    DLPoly(control=argList.control, config=argList.config, field=argList.field, statis=argList.statis)
