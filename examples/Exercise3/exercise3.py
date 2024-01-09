#!/usr/bin/env python3

from dlpoly import DLPoly
from dlpoly.rdf import rdf
from dlpoly.output import Output
import matplotlib
import matplotlib.pyplot as plt


def showrdf(loc):
    m = rdf(loc)
    for i in range(len(m.labels)):
        plt.plot(m.x, m.data[i,:,0],label = "-".join(m.labels[i]))
    plt.xlabel("r [Å])")
    plt.ylabel("gofr [a.u.])")
    plt.legend()


dlPoly = DLPoly(control="CONTROL", config="CONFIG",
                field="FIELD", workdir="w40")

dlPoly.control.time_run = 10000
dlPoly.run(numProcs = 1)

showrdf("w40/RDFDAT")
plt.show()
