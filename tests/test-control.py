#!/usr/bin/env python3
import dlpoly as dlp


d = dlp.DLPoly()
d.load_control("CONTROL")

d.control.write("test.control")
