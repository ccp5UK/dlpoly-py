#!/usr/bin/env python3

from dlpoly import DLPoly
import os

dlp="/home/drFaustroll/bin/DLPOLY.Z"

dlPoly = DLPoly(control="Ar.control", config="Ar.config",
                field="Ar.field", workdir="argon")
dlPoly.run(executable=dlp,numProcs = 4)

dlPoly = DLPoly(control="Ar.control", config="argon/REVCON", destconfig="Ar.config",
                field="Ar.field", workdir="argon-T310")
dlPoly.control['temp'] = 310.0
dlPoly.run(executable=dlp,numProcs = 4)

wkd='argon-neweps'
field = DLPoly(field="Ar.field").field
field.vdws[0].params=['125.0','3.0']
field.write('Ar-n.field')

dlPoly = DLPoly(control="Ar.control", config="argon/REVCON", destconfig="Ar.config",
                field='Ar-n.field', workdir=wkd)

dlPoly.run(executable=dlp,numProcs = 4)

