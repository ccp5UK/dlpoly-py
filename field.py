"""
Module containing data relating to DLPOLY field files
"""

from collections import defaultdict
from abc import ABC
from species import Species
from utility import read_line, peek

class Interaction(ABC):
    """ Abstract base class for managing atomic interactions """
    nAtoms = {}
    @potClass.setter
    def potClass(self, potClass):
        if potClass not in self.potClasses:
            raise IOError("Unrecognised potential class {} must be one of {}".format(potClass,
                                                                                     ", ".join(self.potClasses)))
        self.potClass = potClass

    potClasses = property(lambda self: [potClass for potClass in self.nAtoms.keys()])

class Bond(Interaction):
    """ Class containing information regarding bonds in molecules """
    nAtoms = {"atoms": 1, "bonds": 2, "constraints": 2, "angles": 3, "dihedrals": 4, "inversions": 4, "rigid": -1}
    def __init__(self, potClass=None, params=None):
        self.potClass = potClass
        # In bonds key comes first...
        self.potType, params = params[0], params[1:]
        self.atoms, self.params = params[0:Potential.nAtoms[potClass]], params[Potential.nAtoms[potClass]:]
        # Atoms always in alphabetical/numerical order
        self.atoms = sorted(self.atoms)

class Potential(Interaction):
    """ Class containing information regarding potentials """
    nAtoms = {"extern": 0, "vdw": 2, "metal": 2, "rdf": 2, "tbp": 3, "fbp": 4}

    def __init__(self, potClass=None, params=None):
        self.potClass = potClass
        # In potentials atoms come first...
        self.atoms, params = params[0:Potential.nAtoms[potClass]], params[Potential.nAtoms[potClass]:]
        self.potType, self.params = params[0], params[1:]
        if params is not None:
            # Atoms always in alphabetical/numerical order
            self.atoms = sorted(self.atoms)

class PotHaver(ABC):
    """ Abstract base class defining an object which contains potentials or bonds """
    def __init__(self):
        self.pots = defaultdict(list)

    def add_potential(self, atoms, potential):
        """ Add a potential to the list of available potentials """
        if not isinstance(potential, (Potential, Bond)):
            raise TypeError("Tried to add non-potential to a potential containing object")

        self.pots[tuple(atoms)].append(potential)

    def get_pot_by_species(self, species):
        """ Return all pots for a given pot species """
        out = (pot for potSet in self.pots.values() for pot in potSet if species in pot.atoms)
        if peek(out) is None:
            print("No potentials for species {} found".format(species))
        return out

    def get_pot_by_class(self, potClass):
        """ Return all pots for a given pot class """
        out = (pot for potSet in self.pots.values() for pot in potSet if pot.potClass == potClass)
        if peek(out) is None:
            print("No potentials for potClass {} found".format(potClass))
        return out

    def get_pot_by_type(self, potType):
        """ Return all pots for a given pot type """
        out = (pot for potSet in self.pots.values() for pot in potSet if pot.potType == potType)
        if peek(out) is None:
            print("No potentials for potType {} found".format(potType))
        return out


class Molecule(PotHaver):
    """ Class containing field molecule data """
    def __init__(self):
        PotHaver.__init__(self)
        self.name = ""
        self.nMols = 0
        self.species = {}

    def read_molecule(self, fieldFile):
        """ Read a single molecule into class and return itself """
        self.name = read_line(fieldFile).strip()
        self.nMols = int(read_line(fieldFile).split()[1])
        line = read_line(fieldFile)
        while line.lower() != "finish":
            potClass, nPots = line.split()
            nPots = int(nPots)
            self._read_block(fieldFile, potClass, nPots)
            line = read_line(fieldFile)
        return self

    def _read_block(self, fieldFile, potClass, nPots):
        """ Read a potentials block """
        if potClass == "atoms":
            self._read_atoms(fieldFile, nPots)
            return

        for pot in range(nPots):
            args = read_line(fieldFile).split()
            pot = Bond(potClass, args)
            self.add_potential(pot.atoms, pot)

    def _read_atoms(self, fieldFile, nAtoms):
        atom = 0
        while atom < nAtoms:
            name, weight, charge, *repeatsFrozen = read_line(fieldFile).split()
            if repeatsFrozen:
                repeats, frozen = repeatsFrozen
            else:
                repeats, frozen = 1, False
            repeats = int(repeats)
            self.species[name] = Species(name, len(self.species), charge, weight, frozen, repeats)
            atom += repeats

class Field(PotHaver):
    """ Class containing field data """
    def __init__(self, source=None):
        PotHaver.__init__(self)
        self.header = ""
        self.units = "internal"
        self.molecules = []
        if source is not None:
            self.source = source
            self.read(self.source)


    vdws = property(lambda self: list(self.get_pot_by_class("vdw")))
    metals = property(lambda self: list(self.get_pot_by_class("metal")))
    rdfs = property(lambda self: list(self.get_pot_by_class("rdf")))
    tersoffs = property(lambda self: list(self.get_pot_by_class("tersoff")))
    tbps = property(lambda self: list(self.get_pot_by_class("tbp")))
    fbps = property(lambda self: list(self.get_pot_by_class("fbp")))
    externs = property(lambda self: list(self.get_pot_by_class("extern")))

    nMolecules = property(lambda self: len(self.molecules))
    nVdws = property(lambda self: len(self.vdws))
    nMetals = property(lambda self: len(self.metals))
    nRdfs = property(lambda self: len(self.rdfs))
    nTersoffs = property(lambda self: len(self.tersoffs))
    nTbps = property(lambda self: len(self.tbps))
    nFbps = property(lambda self: len(self.fbps))
    nExterns = property(lambda self: len(self.externs))

    species = property(lambda self: {spec.element: spec for mol in self.molecules for spec in mol.species.values()})
    potSpecies = property(lambda self: {spec for specPairs in self.pots for spec in specPairs})

    def _read_block(self, fieldFile, potClass, nPots):
        """ Read a potentials block """
        if potClass == "tersoff":
            self._read_tersoff(fieldFile, nPots)
            return
        for pot in range(nPots):
            args = fieldFile.readline().split()
            pot = Potential(potClass, args)
            self.add_potential(pot.atoms, pot)

    def _read_tersoff(self, fieldFile, nPots):
        """ Read a tersoff set (different to standard block) """


    def read(self, fieldFile="FIELD"):
        """ Read field file into data """
        with open(fieldFile, 'r') as inFile:
            # Header *must* be first line?
            self.header = inFile.readline()
            key, self.units = read_line(inFile).split()
            line = read_line(inFile)
            while line.lower() != "close":
                key, nVals = line.lower().split()
                nVals = int(nVals)
                if key == "molecules":
                    for _ in range(nVals):
                        self.molecules.append(Molecule().read_molecule(inFile))
                else:
                    self._read_block(inFile, key, nVals)
                line = read_line(inFile)

if __name__ == "__main__":
    FLD = Field("FIELD")
    print(FLD.species)
    print(*FLD.get_pot_by_species("Ar"))
