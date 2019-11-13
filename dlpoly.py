"""
Module containing main DLPOLY class
"""

import subprocess
from control import Control
from config import Config

class DlPoly:
    """ Main class of a DLPOLY runnable set of instructions """
    def __init__(self, control="CONTROL"):
        self.control = Control(control)
        self.config = Config().read(self.config_file)
        self.field = None

    control_file = property(lambda self: self.control.io.control)
    field_file = property(lambda self: self.control.io.field)
    config_file = property(lambda self: self.control.io.config)
    statis_file = property(lambda self: self.control.io.outstats)

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
