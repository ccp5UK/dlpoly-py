#!/usr/bin/env python3

from dlpoly import DLPoly

dlp="/home/drFaustroll/playground/dlpoly/dl-poly-alin/build-mpi/bin/DLPOLY.Z"

dlPoly = DLPoly(control="Ar.control", config="Ar.config",
                field="Ar.field", workdir="argon")
dlPoly.run(executable=dlp,numProcs = 4)
