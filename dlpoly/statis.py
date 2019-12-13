"""
File containing methods for loading statistics data from DL_POLY_4
"""

import numpy as np


class Statis():
    __version__ = "0"

    def __init__(self, source=None, control=None, config=None):
        self.rows = 0
        self.columns = 0
        self.data = None
        if source is not None:
            self.source = source
            self.read(source)

        self.gen_labels(control, config)

    _labelPos = property(lambda self: (len(self.labels)//5+1, len(self.labels) % 5+1))

    def add_label(self, arg):
        self.labels.append("{0:d}-{1:d} {2:s}".format(*self._labelPos, arg))

    def read(self, filename="STATIS"):
        h1, h2, s = open(filename).read().split('\n', 2)
        self.data = np.array(s.split(), dtype=float)
        self.columns = int(self.data[2])
        self.rows = self.data.size//(self.columns + 3)
        self.data.shape = self.rows, self.columns + 3
        return self

    def gen_labels(self, control=None, config=None):
        self.labels = ["1-1 Total Extended System Energy",
                       "1-2 System Temperature",
                       "1-3 Configurational Energy",
                       "1-4 Short Range Potential Energy",
                       "1-5 Electrostatic Energy",
                       "2-1 Chemical Bond Energy",
                       "2-2 Valence Angle And 3-Body Potential Energy",
                       "2-3 Dihedral, Inversion, And 4-Body Potential Energy",
                       "2-4 Tethering Energy",
                       "2-5 Enthalpy (Total Energy + Pv)",
                       "3-1 Rotational Temperature",
                       "3-2 Total Virial",
                       "3-3 Short-Range Virial",
                       "3-4 Electrostatic Virial",
                       "3-5 Bond Virial",
                       "4-1 Valence Angle And 3-Body Virial",
                       "4-2 Constraint Bond Virial",
                       "4-3 Tethering Virial",
                       "4-4 Volume",
                       "4-5 Core-Shell Temperature",
                       "5-1 Core-Shell Potential Energy",
                       "5-2 Core-Shell Virial",
                       "5-3 Md Cell Angle Α",
                       "5-4 Md Cell Angle Β",
                       "5-5 Md Cell Angle Γ",
                       "6-1 Pmf Constraint Virial",
                       "6-2 Pressure",
                       "6-3 External Degree Of Freedom"]

        if control:
            if getattr(control, 'l_msd', False) and config: # Never true as yet
                for i in range(config.natoms):
                    self.add_label("Mean Squared Displacement")
                    self.add_label("Velocity . Velocity")
            for i in range(9):
                self.add_label("Stress Tensor")
            if control and control.ensemble.ensemble in ("npt", "nst"):
                for i in range(9):
                    self.add_label("Cell Dimensions")
                self.add_label("Instantaneous PV")
                if any(key in control.ensemble.args for key in ("area", "tens", "semi", "orth")):
                    self.add_label("H_Z")
                    self.add_label("vol/h_z")
                    if any(key in control.ensemble.args for key in ("tens", "semi")):
                        # "-h_z*(stats%strtot(1)-(thermo%press+thermo%stress(1)))*tenunt"
                        self.add_label("Surface Tension")
                        # "-h_z*(stats%strtot(5)-(thermo%press+thermo%stress(5)))*tenunt"
                        self.add_label("Surface Tension") 

        # Catch Remainder
        for i in range(len(self.labels)+1, self.columns):
            self.add_label("col_{2:d}".format(i+1))


    def flatten(self):
        for i in range(self.columns-3):
            with open(self.labels[i], 'w') as f:
                for j in range(self.rows):
                    f.write("{} {}\n".format(self.data[j, 1], self.data[j, i+3]))


def read_rdf(filename="RDFDAT"):
    """ Read an RDF file into data """
    with open(filename, 'r') as fileIn:
        # Discard title
        _ = fileIn.readline()
        nRDF, nPoints = map(int, fileIn.readline().split())

        data = np.zeros(nRDF+1, nPoints, 2)
        labels = []

        for sample in range(nRDF):
            species = fileIn.readline().split()
            labels.append(species)
            for point in range(nPoints):
                r, g_r = fileIn.readline().split()
                data[sample, point, :] = float(r), float(g_r)
                data[nRDF, point, :] += data[sample, point, :]
    return labels, data
