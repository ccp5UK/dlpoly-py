"""
Module containing main DLPOLY class
"""

import subprocess
import os.path
from control import Control
from config import Config
from cli import get_command_args

class DlPoly:
    """ Main class of a DLPOLY runnable set of instructions """
    def __init__(self, control=None, config=None, field=None, statis=None):
        if control is not None:
            self.control_file = control
            self.load_control()
        else:
            # Default to having a control
            self.control = Control()
        if config is not None:
            self.config_file = config
            self.load_config()
        if field is not None:
            self.field_file = field
            self.load_field()
        if statis is not None:
            self.statis = statis
            self.load_statis()

    def load_control(self, source=None):
        """ Load control file into class """
        if source is None:
            source = self.control_file
        if os.path.isfile(source):
            self.control = Control(source)
        else:
            print("Unable to find file: {}".format(source))


    def load_field(self, source=None):
        """ Load field file into class """
        if source is None:
            source = self.field_file
        if os.path.isfile(source):
            self.field = Field(source)
        else:
            print("Unable to find file: {}".format(source))

    def load_config(self, source=None):
        """ Load config file into class """
        if source is None:
            source = self.config_file
        if os.path.isfile(source):
            self.config = Config(source)
        else:
            print("Unable to find file: {}".format(source))

    def load_statis(self, source=None):
        """ Load statis file into class """
        if source is None:
            source = self.statis_file
        if os.path.isfile(source):
            self.config = Statis(source)
        else:
            print("Unable to find file: {}".format(source))

    @property
    def control_file(self):
        return self.control.io.control

    @control_file.setter
    def control_file(self, control):
        self.control.io.control = control

    @property
    def field_file(self):
        return self.control.io.field

    @field_file.setter
    def field_file(self, field):
        self.control.io.field = field

    @property
    def config_file(self):
        return self.control.io.config

    @config_file.setter
    def config_file(self, config):
        self.control.io.config = config

    @property
    def statis_file(self):
        return self.control.io.outstats

    @statis_file.setter
    def statis_file(self, statis):
        self.control.io.outstats = statis


    def run(self, dlp="DLPOLY.Z", modules=(), np=1, mpi='mpirun -n'):
        """ this is very primitive one allowing the checking
        for the existence of files and alteration of control parameters """

        if np > 1:
            cdlp = "{0:s} {1:d} {2:s} {3:s}".format(mpi, np, dlp, self.control_file)
        else:
            cdlp = "{0:s} {1:s}".format(dlp, self.control_file)

        if modules:
            ll="module purge && module load " + modules
            with open("env.sh", 'w') as outFile:
                outFile.write(ll+"\n")
                outFile.write(cdlp)
                cmd = ['sh ./env.sh']
        else:
            cmd = [cdlp]
        subprocess.call(cmd, shell=True)

if __name__ == "__main__":
    argList = get_command_args()
