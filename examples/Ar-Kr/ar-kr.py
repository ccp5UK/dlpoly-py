#!/usr/bin/env python3

from dlpoly import DLPoly

dlp="/path_to_dlpoly/bin/DLPOLY.Z"

dlPoly = DLPoly(control="Ar-Kr.control", config="Ar-Kr.config",
                field="Ar-Kr.field", workdir="arkr")
dlPoly.control.time_run = (1000, 'steps')

dlPoly.run(executable=dlp,numProcs = 1, debug=True)
