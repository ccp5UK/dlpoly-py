'''
Code to build CONFIG/FIELD from layound files
'''

import copy
import random
import numpy as np
from dlpoly.field import Field
from dlpoly.config import Config
from dlpoly.utility import parse_line, read_line
from .cfgLoader import CFG

class System:
    keywords = ('cell', 'include', 'vdw')
    def __init__(self):
        self.config = Config()
        self.config.level = 0
        self.field = Field()
        self.CFGs = {}

        self.defined = {key: False for key in System.keywords}

    def handle_structure(self, source):
        lastConfig = None
        while True:
            line = read_line(source)
            line = parse_line(line)
            while line.endswith('&'):
                line += read_line(source).strip('&')
            if line.lower() == 'end structure':
                break

            keyword, *args = line.split()
            keyword = keyword.lower()
            print(keyword)
            if keyword == 'include':
                filename, *args = args
                if filename not in self.CFGs:
                    self.CFGs[filename] = CFG(filename)

                newConfig = copy.copy(self.CFGs[filename])
                self._add_config(newConfig, args)
                lastConfig = newConfig

            elif keyword == 'repeat':
                nRepeat, *args = args
                for i in range(int(nRepeat)):
                    newConfig = copy.copy(lastConfig)
                    self._add_config(newConfig, args[:])
                    lastConfig = newConfig

    def _add_config(self, newConfig, args):
        self.field.add_molecule(newConfig)

        while args:
            keyword = args.pop(0).lower()
            if keyword == 'angle':
                alpha, beta, gamma, *args = args
                angle = tuple(ang if ang != 'rand' else random.uniform(0, 180.)
                              for ang in (alpha, beta, gamma))
                newConfig.rotate(np.asarray(angle, dtype=float))
            elif keyword == 'pos':
                x, y, z, *args = args
                newConfig.translate(np.asarray((x, y, z), dtype=float))
            elif keyword == 'stretch':
                x, y, z, *args = args
                newConfig.stretch(np.asarray((x, y, z), dtype=float))
            else:
                raise IOError('Unrecognised keyword {} in {}'.format(keyword, 'include'))

        self.config.add_atoms(newConfig.atoms)


    def handle_cell(self, line):
        key, *args = line.split()
        if self.defined['cell']:
            raise ValueError('{} multiply defined in {}'.format(key.capitalize(), source))
        self.config.cell = np.zeros((3, 3))
        if len(args) == 1: # Fill diagonal
            for i in range(3):
                self.config.cell[i, i] = args[0]
            self.config.pbc = 1
        elif len(args) == 3: # Assume diagonal
            for i in range(3):
                self.config.cell[i, i] = args[i]
            self.config.pbc = 2
        elif len(args) == 9: # Full matrix
            self.config.cell = np.asarray(args).reshape((3, 3))
            self.config.pbc = 3
        else:
            raise IOError('Cannot handle block {} {}')
        
    def handle_vdw_block(self, source):
        for line in source:
            if line.lower() == 'end vdw':
                break
            for i in range(int(args[0])):
                line = read_line(source)

                potClass, nPots = line.split()
                self.field._read_block(source, potClass, nPots)
        else:
            raise IOError('Unended vdw block')


def build(source):
    system = System()
    for line in source:
        line = parse_line(line).lower()
        if not line:
            continue
        key, *args = line.split()

        if key == 'structure':
            system.handle_structure(source)
        elif key == 'cell':
            system.handle_cell(line)
        elif key == 'vdw':
            system.handle_vdw_block(source)
    
    return system
