#!/usr/bin/env python3

from dlpoly import DLPoly

dlp="/path_to_dlpoly/bin/DLPOLY.Z"
dlp = "/home/drFaustroll/lavello/build-dlp-jan/bin/DLPOLY.Z"

dlPoly = DLPoly(control="water.control", config="water.config",
                field="spce.field", workdir="water")

dlPoly.run(executable=dlp,numProcs = 1)
