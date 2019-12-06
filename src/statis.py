"""
File containing methods for loading statistics data from DLPoly
"""

import numpy as np

def read_rdf(filename="RDFDAT"):
    """ Read an RDF file into data """
    with open(filename, 'r') as fileIn:
        # Discard title
        _ = fileIn.readline()
        nRDF, nPoints = map(int, fileIn.readline().split())

        data = np.zeros(nRDF+1, nPoints, 2)
        labels = []

        for sample in range(nRDF):
            species = fileIn.readline().split()
            labels.append(species)
            for point in range(nPoints):
                r, g_r = fileIn.readline().split()
                data[sample, point, :] = float(r), float(g_r)
                data[nRDF, point, :] += data[sample, point, :]
    return labels, data
    # try:
    #     title, header, rdfall = open(filename).read().split('\n', 2)
    # except IOError:
    #     return 0, 0, 0, []
    # nrdf, npoints = map(int, header.split())
    # b = 2*(npoints+1)
    # d = np.zeros((nrdf+1, npoints, 2), dtype=float)
    # labels = []
    # s = rdfall.split()
    # for i in range(nrdf):
    #     x = s[b*i:b*(i+1)]
    #     y = np.array(x[2:], dtype=float)
    #     y.shape = npoints, 2
    #     d[i, :, :] = y
    #     labels.append(x[0]+" ... "+x[1])
    # labels.append("all")
    # for j in range(npoints):
    #     d[nrdf, j, 0] = np.sum(d[0:nrdf-1, j, 0])
    #     d[nrdf, j, 1] = np.sum(d[0:nrdf-1, j, 1])
    # return nrdf+1, npoints, d, labels

def readStatis(filename="STATIS"):
    h1, h2, s = open(filename).read().split('\n', 2)
    d = np.array(s.split(), dtype=float)
    nd = int(d[2])
    n = d.size//(nd+3)
    d.shape = n, nd+3
    datumNames = ["1-1 total extended system energy",
                  "1-2 system temperature",
                  "1-3 configurational energy",
                  "1-4 short range potential energy",
                  "1-5 electrostatic energy",
                  "2-1 chemical bond energy",
                  "2-2 valence angle and 3-body potential energy",
                  "2-3 dihedral, inversion, and 4-body potential energy",
                  "2-4 tethering energy",
                  "2-5 enthalpy (total energy + PV)",
                  "3-1 rotational temperature",
                  "3-2 total virial",
                  "3-3 short-range virial",
                  "3-4 electrostatic virial",
                  "3-5 bond virial",
                  "4-1 valence angle and 3-body virial",
                  "4-2 constraint bond virial",
                  "4-3 tethering virial",
                  "4-4 volume",
                  "4-5 core-shell temperature",
                  "5-1 core-shell potential energy",
                  "5-2 core-shell virial",
                  "5-3 MD cell angle α",
                  "5-4 MD cell angle β",
                  "5-5 MD cell angle γ",
                  "6-1 PMF constraint virial",
                  "6-2 pressure",
                  "6-3 exdof"]

    for i in range(28, nd):
        datumNames.append("{0:d}-{1:d} col_{2:d}".format(i//5+1, i%5+1, i+1))
    return n, nd, d, datumNames
