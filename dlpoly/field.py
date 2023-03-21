"""
Module containing data relating to DLPOLY field files
"""

from collections import defaultdict
from abc import ABC
from .species import Species
from .utility import read_line, peek


class Interaction(ABC):
    """ Abstract base class for managing atomic interactions """
    def __init__(self):
        self._pot_class = None

    n_atoms = {}

    @property
    def pot_class(self):
        """ The type of potential """
        return self._pot_class

    @pot_class.setter
    def pot_class(self, pot_class):
        if pot_class not in self.pot_classes:
            raise IOError(f"Unrecognised {type(self).__name__} class {pot_class}. "
                          f"Must be one of {', '.join(self.pot_classes)}")
        self._pot_class = pot_class

    pot_classes = property(lambda self: list(self.n_atoms.keys()))


class Bond(Interaction):
    """ Class containing information regarding bonds in molecules """
    n_atoms = {"atoms": 1,
               "bonds": 2,
               "constraints": 2,
               "angles": 3,
               "dihedrals": 4,
               "inversions": 4,
               "rigid": -1
               }

    def __init__(self, pot_class=None, params=None):
        Interaction.__init__(self)
        self.pot_class = pot_class
        # In bonds key comes first...
        self.pot_type, params = params[0], params[1:]
        self.atoms, self.params = (params[0:self.n_atoms[pot_class]],
                                   params[self.n_atoms[pot_class]:])

    def __str__(self):
        return " ".join((self.pot_type,
                         " ".join(self.atoms),
                         " ".join(self.params)))


class Potential(Interaction):
    """ Class containing information regarding potentials """
    n_atoms = {"extern": 0, "vdw": 2, "metal": 2, "rdf": 2, "tbp": 3, "fbp": 4}

    def __init__(self, pot_class=None, params=None):
        Interaction.__init__(self)
        self.pot_class = pot_class
        # In potentials atoms come first...
        self.atoms, params = params[0:self.n_atoms[pot_class]], params[self.n_atoms[pot_class]:]
        self.pot_type, self.params = params[0], params[1:]
        if params is not None:
            # Atoms always in alphabetical/numerical order
            self.atoms = sorted(self.atoms)

    def __str__(self):
        return " ".join((self.pot_type,
                         " ".join(self.atoms),
                         " ".join(self.params)))


class PotHaver(ABC):
    """ Abstract base class defining an object which contains potentials or bonds """
    def __init__(self):
        self.pots = defaultdict(list)

    def add_potential(self, atoms, potential):
        """ Add a potential to the list of available potentials """
        if not isinstance(potential, (Potential, Bond)):
            raise TypeError("Tried to add non-potential to a potential containing object")

        self.pots[tuple(atoms)].append(potential)

    def set_potential(self, old_pot, new_pot):
        """ Override a potential with a new one """
        for i, curr_pot in enumerate(self.pots[old_pot.atoms]):
            if curr_pot == old_pot:
                self.pots[old_pot.atoms][i] = new_pot
                return

    def get_pot(self, species=None, pot_class=None, pot_type=None, quiet=False):
        """ Return all pots for a given pot type """

        tests = (("atoms", species), ("pot_class", pot_class), ("pot_type", pot_type))
        out = peek(pot for potSet in self.pots.values() for pot in potSet if
                   all(getattr(pot, prop) == val for prop, val in tests if val is not None)
                   )

        if out is None and not quiet:
            for name, val in tests:
                if val is not None:
                    print(f"No potentials for {name} {val} found")
            out = ()
        return out

    def get_pot_by_species(self, species, quiet=False):
        """ Return all pots for a given pot species """
        return self.get_pot(species=species, quiet=quiet)

    def get_pot_by_class(self, pot_class, quiet=False):
        """ Return all pots for a given pot class """
        return self.get_pot(pot_class=pot_class, quiet=quiet)

    def get_pot_by_type(self, pot_type, quiet=False):
        """ Return all pots for a given pot type """
        return self.get_pot(pot_type=pot_type, quiet=quiet)

    def get_num_pot_by_species(self, species, quiet=False):
        """ Return all pots for a given pot species """
        return len(list(self.get_pot_by_species(species, quiet)))

    def get_num_pot_by_class(self, pot_class, quiet=False):
        """ Return all pots for a given pot class """
        return len(list(self.get_pot_by_class(pot_class, quiet)))

    def get_num_pot_by_type(self, pot_type, quiet=False):
        """ Return all pots for a given pot type """
        return len(list(self.get_pot_by_type(pot_type, quiet)))


class Molecule(PotHaver):
    """ Class containing field molecule data """
    def __init__(self):
        PotHaver.__init__(self)
        self.name = ""
        self.n_mols = 0
        self.n_atoms = 0
        self.species = {}

    activeBonds = property(lambda self: (name for name in Bond.n_atoms
                                         if self.get_num_pot_by_class(name)))

    def read(self, field_file):
        """ Read a single molecule into class and return itself """
        self.name = read_line(field_file).strip()
        self.n_mols = int(read_line(field_file).split()[1])
        line = read_line(field_file)
        while line.lower() != "finish":
            pot_class, n_pots = line.split()
            pot_class = pot_class.lower()
            n_pots = int(n_pots)
            self._read_block(field_file, pot_class, n_pots)
            line = read_line(field_file)
        return self

    def get_masses(self):
        """ Get all masses from molecule """
        masses = [[spec.mass] * spec.repeats for spec in self.species.values()]
        return masses

    def get_charges(self):
        """ Get all charges from molecule """
        charges = [[spec.charge] * spec.repeats for spec in self.species.values()]
        return charges

    def write(self, out_file):
        """ Write self to out_file (called by Field) """
        print(self.name, file=out_file)
        print(f"nummols {self.n_mols}", file=out_file)
        print(f"atoms {self.n_atoms}", file=out_file)
        for element in self.species.values():
            print(element, file=out_file)

        for pot_class in self.activeBonds:
            pots = list(self.get_pot_by_class(pot_class))
            print(f"{pot_class} {len(pots)}", file=out_file)
            for pot in pots:
                print(pot, file=out_file)
        print("finish", file=out_file)

    def _read_block(self, field_file, pot_class, n_pots):
        """ Read a potentials block """
        if pot_class.lower() == "atoms":
            self.n_atoms = n_pots
            self._read_atoms(field_file, n_pots)
            return

        for pot in range(n_pots):
            args = read_line(field_file).split()
            pot = Bond(pot_class, args)
            self.add_potential(pot.atoms, pot)

    def _read_atoms(self, field_file, n_atoms):
        atom = 0
        index = 0
        while atom < n_atoms:
            name, mass, charge, *repeats_frozen = read_line(field_file).split()
            if repeats_frozen:
                repeats, frozen, *_ = repeats_frozen
            else:
                repeats, frozen = 1, 0
            repeats = int(repeats)
            self.species[index] = Species(name, len(self.species),
                                          charge, mass, frozen, repeats)
            atom += repeats
            index += 1


class Field(PotHaver):
    """ Class containing field data """

    def __init__(self, source=None):
        PotHaver.__init__(self)
        self.header = ""
        self.units = "internal"
        self.molecules = {}
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

    activePots = property(lambda self: (name for name in Potential.n_atoms
                                        if self.get_num_pot_by_class(name)))

    species = property(lambda self: {spec.element: spec
                                     for mol in self.molecules.values()
                                     for spec in mol.species.values()})

    potSpecies = property(lambda self: {spec for specPairs in self.pots
                                        for spec in specPairs})

    def _read_block(self, field_file, pot_class, n_pots):
        """ Read a potentials block """
        if pot_class == "tersoff":
            self._read_tersoff(field_file, n_pots)
            return
        for pot in range(n_pots):
            args = field_file.readline().split()
            pot = Potential(pot_class, args)
            self.add_potential(pot.atoms, pot)

    def _read_tersoff(self, field_file, n_pots):
        """ Read a tersoff set (different to standard block) """

    def add_molecule(self, molecule):
        """ Add molecule to self """
        if molecule.name not in self.molecules:
            self.molecules[molecule.name] = molecule
        self.molecules[molecule.name].n_mols += 1

        return molecule.name, self.molecules[molecule.name].n_mols

    def read(self, field_file="FIELD"):
        """ Read field file into data """
        with open(field_file, "r", encoding="utf-8") as in_file:
            # Header *must* be first line?
            self.header = in_file.readline().strip()
            key, self.units = read_line(in_file).split()
            line = read_line(in_file)
            while line.lower() != "close":
                key, *n_vals = line.lower().split()
                n_vals = int(n_vals[-1])
                if key.startswith("molecul"):
                    for _ in range(n_vals):
                        mol = Molecule().read(in_file)
                        self.molecules[mol.name] = mol
                else:
                    self._read_block(in_file, key, n_vals)
                line = read_line(in_file)

    def write(self, field_file="FIELD"):
        """ Write data to field file """
        with open(field_file, "w", encoding="utf-8") as out_file:
            print(self.header, file=out_file)
            print(f"units {self.units}", file=out_file)
            print(f"molecules {self.nMolecules}", file=out_file)

            for molecule in self.molecules.values():
                molecule.write(out_file)

            for pot_class in self.activePots:
                pots = list(self.get_pot_by_class(pot_class, quiet=True))
                print(f"{pot_class} {len(pots)}", file=out_file)
                for pot in pots:
                    print(pot, file=out_file)
            print("close", file=out_file)

    def __str__(self):
        return ("[" +
                ", \n".join(molecule.name for molecule in self.molecules.values())
                + "]")


if __name__ == "__main__":
    FLD = Field("FIELD")
    FLD.write("geoff")
