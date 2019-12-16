"""
Load a part config for inclusion into whole config
"""
import numpy as np

from dlpoly.config import Atom
from dlpoly.field import Molecule
from dlpoly.utility import read_line

class CFG(Molecule):
    ''' Load a partial configuration '''
    def __init__(self, source=None):
        Molecule.__init__(self)
        self.atoms = []
        self.nMols = 1
        if source is not None:
            self.read(source)
            self._centre_mol()

    def _centre_mol(self):
        ''' Centre molecule about 0, 0, 0 '''
        tmpArr = np.asarray([atom.pos for atom in self.atoms])
        maxPos, minPos = np.max(tmpArr, axis=0), np.min(tmpArr, axis=0)
        shift = (minPos + maxPos) / 2
        for atom in self.atoms:
            atom.pos -= shift

    def _read_pos(self, source, nElem):
        ''' Read in an atoms block '''
        self.atoms = [None]*nElem
        for i in range(nElem):
            datum = read_line(source).split()
            self.atoms[i] = Atom(element=datum[0], pos=np.asarray(datum[1:4]), index=i)

    def _read_bonds(self, source, nElem):
        ''' Read in a bonds block '''
        for _ in range(nElem):
            potClass, num = read_line(source).split()
            num = int(num)
            self._read_block(source, potClass, num)

    def read(self, source):
        ''' Read a partial config file '''
        with open(source, 'r') as sourceFile:
            self.name = read_line(sourceFile)
            for line in sourceFile:
                block, num = line.strip().split()
                num = int(num)
                block = block.lower()
                if block == 'positions':
                    self._read_pos(sourceFile, num)
                elif block == 'species':
                    self._read_atoms(sourceFile, num)
                elif block == 'bonding':
                    self._read_bonds(sourceFile, num)
                else:
                    raise ValueError('Cannot read structure {}'.format(block))
