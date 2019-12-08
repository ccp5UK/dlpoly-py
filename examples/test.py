#!/usr/bin/env python3
import dlpoly as dlp


# d = dlp.DLPoly(control="CONTROL")
d = dlp.DLPoly(config="CONFIG")
print(d.Config.write("test"))
