"""
Load a part config for inclusion into whole config
"""
import numpy as np

from dlpoly.config import Atom
from dlpoly.field import Molecule
from dlpoly.utility import read_line, build_3d_rotation_matrix

class CFG(Molecule):
    ''' Load a partial configuration '''
    def __init__(self, source=None):
        Molecule.__init__(self)
        self.atoms = []
        self.nMols = 1
        if source is not None:
            self.read(source)
            self._centre_mol()

    atomSpecies = property(lambda self: [self.species[atom.element] for atom in self.atoms])
    atomPos = property(lambda self: [atom.pos for atom in self.atoms])

    def translate(self, translation):
        ''' Move all atoms by translation '''
        for atom in self.atoms:
            atom.pos += translation

    def stretch(self, stretch):
        ''' Stretch all atoms by translation '''
        for atom in self.atoms:
            atom.pos *= stretch

    def rotate(self, rotation):
        ''' Perform rotation on the atoms in cell '''
        alpha, beta, gamma = rotation
        rot = build_3d_rotation_matrix(alpha, beta, gamma, 'deg')
        self.apply_matrix_transform(rot)

    def apply_matrix_transform(self, transform: np.ndarray):
        ''' Apply a matrix transform to own atoms '''
        for atom in self.atoms:
            atom.pos = np.matmul(transform, atom.pos)

    def _centre_com(self):
        ''' Centre CoM about 0, 0, 0 '''
        centreOfMass = 0.
        for atom in self.atoms:
            centreOfMass += self.species[atom.element].mass * atom.pos
        centreOfMass /= np.sum(spec.mass for spec in self.atomSpecies)
        self.translate(-centreOfMass)

    def _centre_mol(self):
        ''' Centre molecule's centroid about 0, 0, 0 '''
        tmpArr = np.asarray(self.atomPos)
        maxPos, minPos = np.max(tmpArr, axis=0), np.min(tmpArr, axis=0)
        shift = (minPos + maxPos) / 2
        self.translate(-shift)

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
