#!/usr/bin/env python3

from dlpoly import DLPoly

dlp="/your/home/bin/DLPOLY.Z"

dlPoly = DLPoly(control="Ar.control", config="Ar.config",
                field="Ar.field", workdir="argon")
dlPoly.run(executable=dlp,numProcs = 4)

for T in range(200,601,50):
    print("Process T = {}".format(T))
    dlPoly = DLPoly(control="Ar.control", config="Ar.config",
                field="Ar.field", workdir="argon-T{}".format(T))
    dlPoly.control['temperature'] = (T, 'K')
    dlPoly.run(executable=dlp,numProcs = 1, debug=True)
