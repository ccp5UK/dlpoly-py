#!/usr/bin/env python3
"""
Module to handle DLPOLY config files
"""

import numpy as np
from species import Species

class Atom():
    """ Class defining a DLPOLY atom type """
    params = {'element': str, 'pos':list, 'vel':list,
              'forces':list, 'id':int}

    def __init__(self):

        self.element = ''
        self.pos = np.zeros(3)
        self.vel = np.zeros(3)
        self.forces = np.zeros(3)
        self.id = 1

    def write(self, level):
        if level == 0:
            return "{:8s}{:10d}\n{:20.10f}{:20.10f}{:20.10f}".format(self.element,
                self.id, *self.pos)
        if level == 1:
            return "{:8s}{:10d}\n{:20.10f}{:20.10f}{:20.10f}\n{:20.10f}{:20.10f}{:20.10f}".format(self.element,
                self.id, *self.pos, *self.vel)
        if level == 2:
            return "{:8s}{:10d}\n{:20.10f}{:20.10f}{:20.10f}\n{:20.10f}{:20.10f}{:20.10f}\n{:20.10f}{:20.10f}{:20.10f}".format(self.element,
                self.id, *self.pos, *self.vel, *self.forces)


    def __str__(self):
        return "{:8s}{:10d}\n{:20.10f}{:20.10f}{:20.10f}\n{:20.10f}{:20.10f}{:20.10f}\n{:20.10f}{:20.10f}{:20.10f}\n".format(self.element,
                self.id, *self.pos, *self.vel, *self.forces)

    def __getitem__(self, key):
       return getattr(self, key)

    def __setitem__(self, key, val):
        if key not in Species.params:
            raise KeyError('Param {} not valid param name atom type.'.format(key))
        try:
            val = Species.params[key](val)
        except TypeError:
            raise ValueError(
                'Type of {} not valid, must be {}'.format(type(val).__name__,
                                                          Species.params[key].__name__))
        setattr(self, key, val)

    params = property(lambda self: [key for key in Atom.params])

    def read(self, fh, level):
        """ reads info for one atom """
        line = fh.readline()
        if not line:
            return False
        el, ids = line.split()
        self.element = el
        self.id = int(ids)
        self.pos = [float(i) for i in fh.readline().split()]
        if level > 0:
            self.vel = [float(i) for i in fh.readline().split()]
            if level > 1:
                self.forces = [float(i) for i in fh.readline().split()]
        return self

class Config():
    """ Class defining a DLPOLY config file """
    params = {'atoms': list, 'cell':np.ndarray, 'pbc':int,
              'natoms':int, 'level':int, 'title':str}

    natoms = property(lambda self: len(self.atoms))

    def __init__(self, source=None):

        self.title = ""
        self.level = 0
        self.atoms = None
        self.pbc = 0
        self.cell = np.zeros((3, 3))

        if source is not None:
            self.read(source)

    def __getitem__(self, key):
        return getattr(self, key)


    def write(self, filename='new.config', title='', level=0):
        self.level = level
        with open(filename, "w") as outFile:
            outFile.write('{0:72s}\n'.format(title))
            outFile.write('{0:10d}{1:10d}{2:10d}\n'.format(level, self.pbc, self.natoms))
            if self.pbc > 0:
                for j in range(3):
                    outFile.write('{0:20.10f}{1:20.10f}{2:20.10f}\n'.format(
                        self.cell[j, 0], self.cell[j, 1], self.cell[j, 2]))
                for a in self.atoms:
                    print(a.write(self.level), file=outFile)

    def read(self, filename='CONFIG'):
        try:
            f = open(filename, 'r')
        except IOError:
            print("File {0:s} does not exist!".format(filename))
            return []

        self.title = f.readline()
        line = f.readline().split()
        self.level = int(line[0])
        self.pbc = int(line[1])
        if self.pbc > 0:
            for j in range(3):
                line = f.readline().split()
                for i in range(3):
                    try:
                        self.cell[j, i] = float(line[i])
                    except ValueError:
                        raise RuntimeError("error reading cell")

        self.atoms = []
        while True:
            a = Atom().read(f, self.level)
            if not a:
                break
            self.atoms.append(a)
        return self

if __name__ == '__main__':
    cnf = Config().read()
    cnf.write()
