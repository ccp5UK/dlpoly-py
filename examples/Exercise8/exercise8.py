#!/usr/bin/env python3

from dlpoly import DLPoly
from dlpoly.rdf import rdf

dlPoly = DLPoly(control="CONTROL", config="CONFIG",
                field="FIELD", workdir="w40")

dlPoly.run(numProcs = 1)

