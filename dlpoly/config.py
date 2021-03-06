'''
Module to handle DLPOLY config files
'''

import copy
import numpy as np
# from dlpoly.species import Species
from dlpoly.utility import DLPData


class Atom(DLPData):
    ''' Class defining a DLPOLY atom type '''
    def __init__(self, element='', pos=None, vel=None, forces=None, index=1):
        DLPData.__init__(self, {'element': str, 'pos': (float, float, float),
                                'vel': (float, float, float),
                                'forces': (float, float, float), 'index': int,
                                'molecule': (str, int)})
        self.element = element
        self.pos = np.zeros(3) if pos is None else pos
        self.vel = np.zeros(3) if vel is None else vel
        self.forces = np.zeros(3) if forces is None else forces
        self.index = index

    def write(self, level):
        ''' Print own data to file w.r.t config print level '''
        if level == 0:
            return ('{:8s}{:10d}\n{:20.10f}'
                    '{:20.10f}{:20.10f}'.format(self.element,
                                                self.index, *self.pos))

        if level == 1:
            return ('{:8s}{:10d}\n'
                    '{:20.10f}{:20.10f}{:20.10f}\n'
                    '{:20.10f}{:20.10f}{:20.10f}').format(self.element,
                                                          self.index,
                                                          *self.pos, *self.vel)
        if level == 2:
            return ('{:8s}{:10d}\n'
                    '{:20.10f}{:20.10f}{:20.10f}\n'
                    '{:20.10f}{:20.10f}{:20.10f}\n'
                    '{:20.10f}{:20.10f}{:20.10f}').format(self.element,
                                                          self.index,
                                                          *self.pos,
                                                          *self.vel,
                                                          *self.forces)

    def __str__(self):
        return ('{:8s}{:10d}\n'
                '{:20.10f}{:20.10f}{:20.10f}\n'
                '{:20.10f}{:20.10f}{:20.10f}\n'
                '{:20.10f}{:20.10f}{:20.10f}\n').format(self.element,
                                                        self.index,
                                                        *self.pos, *self.vel,
                                                        *self.forces)

    def read(self, fileHandle, level):
        ''' reads info for one atom '''
        line = fileHandle.readline()
        if not line:
            return False
        element, index = line.split()
        self.element = element
        self.index = int(index)
        self.pos = [float(i) for i in fileHandle.readline().split()]
        if level > 0:
            self.vel = [float(i) for i in fileHandle.readline().split()]
            if level > 1:
                self.forces = [float(i) for i in fileHandle.readline().split()]
        return self


class Config():
    ''' Class defining a DLPOLY config file '''
    params = {'atoms': list, 'cell': np.ndarray, 'pbc': int,
              'natoms': int, 'level': int, 'title': str}

    natoms = property(lambda self: len(self.atoms))

    def __init__(self, source=None):
        self.title = ''
        self.level = 0
        self.atoms = []
        self.pbc = 0
        self.cell = np.zeros((3, 3))

        if source is not None:
            self.source = source
            self.read(source)

    def write(self, filename='new.config', title=None, level=0):
        self.level = level
        with open(filename, 'w') as outFile:
            outFile.write('{0:72s}\n'.format(self.title if title is None else title))
            outFile.write('{0:10d}{1:10d}{2:10d}\n'.format(level,
                                                           self.pbc,
                                                           self.natoms))
            if self.pbc > 0:
                for j in range(3):
                    outFile.write('{0:20.10f}{1:20.10f}{2:20.10f}\n'.format(
                        self.cell[j, 0], self.cell[j, 1], self.cell[j, 2]))
            for atom in self.atoms:
                print(atom.write(self.level), file=outFile)

    def add_atoms(self, other):
        ''' Add two Configs together to make one bigger config '''
        lastIndex = self.natoms
        if isinstance(other, Config):
            self.atoms += [copy.copy(atom) for atom in other.atoms]
        elif isinstance(other, (list, tuple)):
            self.atoms += [copy.copy(atom) for atom in other]
        # Shift new atoms' indices to reflect place in new config
        for i in range(lastIndex, self.natoms):
            self.atoms[i].index += lastIndex

    def read(self, filename='CONFIG'):
        ''' Read file into Config '''
        try:
            fileIn = open(filename, 'r')
        except IOError:
            print('File {0:s} does not exist!'.format(filename))
            return []

        self.title = fileIn.readline().strip()
        line = fileIn.readline().split()
        self.level = int(line[0])
        self.pbc = int(line[1])
        if self.pbc > 0:
            for j in range(3):
                line = fileIn.readline().split()
                for i in range(3):
                    try:
                        self.cell[j, i] = float(line[i])
                    except ValueError:
                        raise RuntimeError('Error reading cell')

        self.atoms = []
        while True:
            atom = Atom().read(fileIn, self.level)
            if not atom:
                break
            self.atoms.append(atom)

        fileIn.close()
        return self


if __name__ == '__main__':
    CONFIG = Config().read()
    CONFIG.write()
