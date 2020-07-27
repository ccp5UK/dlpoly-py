#!/usr/bin/env python3

from dlpoly import DLPoly
from dlpoly.rdf import rdf
import matplotlib
import matplotlib.pyplot as plt


def showrdf():
    m = rdf("RDFDAT")
    for i in range(len(m.labels)):
        plt.plot(m.x, m.data[i,:,0],label = "-".join(m.labels[i]))
    plt.xlabel("r [Å])")
    plt.ylabel("gofr [a.u.])")
    plt.legend()
    plt.show()

dlp="/home/drFaustroll/playground/dlpoly/dl-poly-alin/build-yaml/bin/DLPOLY.Z"

dlPoly = DLPoly(control="CONTROL", config="CONFIG",
                field="FIELD", workdir="w")
dlPoly.control.rdf = 10
dlPoly.run(executable=dlp,numProcs = 1)

showrdf()

dlPoly.control.rdf = 10
dlPoly.control.print = 100
dlPoly.control.pressure = 20
dlPoly.run(executable=dlp,numProcs = 1)
showrdf()
