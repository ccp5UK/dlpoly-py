#!/usr/bin/env python3

from dlpoly import DLPoly

dlp = "/your/home/bin/DLPOLY.Z"

Ts = range(1,601,50)
for i,T in enumerate(Ts):
    print(f"Heat at {T=} K")
    if i == 0:
        c = "Ar.config"
    else:
        c = f"argon-T{Ts[i-1]}/REVCON"

    dlPoly = DLPoly(control="Ar.control", config=c,
                field="Ar.field", workdir=f"argon-T{T}")
    dlPoly.control['temperature'] = (T, 'K')
    dlPoly.run(executable=dlp,numProcs = 1, debug=True)
