#!/usr/bin/env python3

from dlpoly import DLPoly

dlp="/home/drFaustroll/playground/dlpoly/dl-poly-alin/build-yaml/bin/DLPOLY.Z"

dlPoly = DLPoly(control="Ar-Kr.control", config="Ar-Kr.config",
                field="Ar-Kr.field", workdir="arkr")
dlPoly.control.steps = 1000

dlPoly.run(executable=dlp,numProcs = 4)