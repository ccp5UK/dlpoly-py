"""
Code to build CONFIG/FIELD from layound files
"""
from dlpoly.field import Field
from dlpoly.config import Config
from dlpoly.utility import read_line
from .cfgLoader import CFG

class System:
    def __init__(self):
        self.config = Config()
        self.field = Field()
        self.CFGs = {}

def build(source):
    system = System()
    while True:
        line = read_line(source)
        if not line:
            break
        key, *args = line.split()
        if key == "include":
            filename, *args = args
            if filename not in system.CFGs:
                system.CFGs[filename] = CFG(filename)
            system.config.add_atoms(system.CFGs[filename].atoms)
            system.field.add_molecule(system.CFGs[filename].molecule)

    return system
