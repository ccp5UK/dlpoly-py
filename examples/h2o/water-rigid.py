#!/usr/bin/env python3

from dlpoly import DLPoly

dlp="/path_to_dlpoly/bin/DLPOLY.Z"
dlp = "/home/drFaustroll/lavello/build-dlp-jan/bin/DLPOLY.Z"

dlPoly = DLPoly(control="water-rigid.control", config="water-constraints.config",
                field="spce-rigid.field", workdir="water")

dlPoly.run(executable=dlp,numProcs = 1)
