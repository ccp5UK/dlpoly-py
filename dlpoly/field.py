"""
Module containing data relating to DLPoly field files.
"""

from abc import ABC
from collections import defaultdict
from typing import Dict, Iterator, List, Literal, Optional, Sequence, TextIO, Tuple, Set

from .species import Species
from .types import OptPath, PathLike
from .utility import batched, peek, read_line

BondTypes = Literal["atoms", "bonds", "constraints",
                    "angles", "dihedrals", "inversions", "rigid"]
PotentialTypes = Literal["dpd", "extern", "vdw", "vdwtab", "metal", "rdf",
                         "tbp", "fbp", "ters", "kihs", "ters-cross",
                         "teth", "shell", "pmf"]


class Interaction(ABC):
    """
    Abstract base class for managing atomic interactions.
    """

    #: Number of atoms for handled kinds of interactions.
    n_atoms: Dict[str, int] = {}

    def __init__(self):
        """
        Instantiate Interaction.
        """
        self._pot_class = None

    @property
    def pot_classes(self) -> List[str]:
        """
        Types of potentials handled by classes.
        """
        return list(self.n_atoms.keys())

    @property
    def pot_class(self) -> str:
        """
        The type of potential.
        """
        return self._pot_class

    @pot_class.setter
    def pot_class(self, pot_class: str):
        """
        Set type of pot class and check validity.

        Parameters
        ----------
        pot_class : str
            Type of potential.

        Raises
        ------
        IOError
            If potential not in valid set of potentials for type.
        """
        if pot_class not in self.pot_classes:
            raise IOError(f"Unrecognised {type(self).__name__} class {pot_class}. "
                          f"Must be one of {', '.join(self.pot_classes)}")
        self._pot_class = pot_class


class Bond(Interaction):
    """
    Class containing information regarding bonds in molecules.

    Attributes
    ----------
    atoms : MaybeList[str]
        Atoms species involved in interaction.
    params : Sequence[float]
        Parameters determining properties of interaction.
    pot_type : str
        Name of interaction type.
    """
    n_atoms = {"atoms": 1,
               "bonds": 2,
               "constraints": 2,
               "angles": 3,
               "dihedrals": 4,
               "inversions": 4,
               "rigid": -1,
               "teth": 1,
               "shell": 2,
               "pmf": 1
               }

    def __init__(self, pot_class: BondTypes, params: Sequence[float] = ()):
        """
        Instantiate class containing information regarding bonds in molecules.

        Parameters
        ----------
        pot_class : BondTypes
            Type of governing interaction.
        params : Sequence[float]
            Parameters of interaction.
        """
        Interaction.__init__(self)
        self.pot_class = pot_class
        # In bonds key comes first...
        if pot_class in ["shell", "constraints"]:
            # except for shell, which has none and two atoms...
            self.atoms, self.params = params[0:2], params[2:]
            self.pot_type = "shell"
        elif pot_class == "pmf":
            # or pmf which has one atom
            self.atoms, self.params = params[0], params[1]
            self.pot_type = "pmf"
        else:
            self.pot_type, params = params[0], params[1:]
            self.atoms, self.params = (params[0:self.n_atoms[pot_class]],
                                       params[self.n_atoms[pot_class]:])

    def __str__(self) -> str:
        return " ".join((self.pot_type,
                         " ".join(self.atoms),
                         " ".join(self.params)))


class Potential(Interaction):
    """
    Class containing information regarding potentials.

    Attributes
    ----------
    atoms : MaybeList[str]
        Atoms species involved in interaction.
    params : Sequence[float]
        Parameters determining properties of interaction.
    pot_type : str
        Name of interaction type.
    """
    n_atoms = {"extern": 0, "vdw": 2, "vdwtab": 2, "metal": 2, "rdf": 2, "tbp": 3, "fbp": 4,
               "ters": 1, "ters-cross": 2, "kihs": 2, "dpd": 2}

    def __init__(self, pot_class: PotentialTypes, params: Sequence[float] = ()):
        """
        Instantiate class containing information regarding potentials.

        Parameters
        ----------
        pot_class : PotentialTypes
            Type of governing interaction.
        params : Sequence[float]
            Parameters of interaction.
        """
        Interaction.__init__(self)
        self.pot_class = pot_class
        # In potentials atoms come first...
        self.atoms, params = params[0:self.n_atoms[pot_class]], params[self.n_atoms[pot_class]:]
        if pot_class != "rdf":
            # rdf is just a pair of atoms
            self.pot_type, self.params = params[0], params[1:]
        if params is not None:
            # Atoms always in alphabetical/numerical order
            self.atoms = sorted(self.atoms)

    def __str__(self) -> str:
        if self.pot_class in ("ters", "kihs"):
            batched_pars = (" ".join(pars) for pars in batched(self.params, 5))
            return " ".join((" ".join(self.atoms),
                             self.pot_class,
                             "\n".join(batched_pars)))

        if self.pot_class == "ters-cross":
            return " ".join((self.atoms,
                            " ".join(self.params)))

        return " ".join((" ".join(self.atoms),
                         self.pot_type,
                         " ".join(self.params)))


class PotHaver(ABC):
    """
    Abstract base class defining an object which contains potentials or bonds.

    Attributes
    ----------
    pots : Dict[Tuple[str, ...], List[Interaction]]
        Potentials managed by object.
    """
    def __init__(self):
        """
        Instantiate class which can contain Interactions.
        """
        self.pots = defaultdict(list)

    def add_potential(self, atoms: Sequence[str], potential: Interaction):
        """
        Add a potential to the list of available potentials.

        Parameters
        ----------
        atoms : Sequence[str]
            Atoms in interaction.
        potential : Interaction
            Interaction governing potential.

        Raises
        ------
        TypeError
            Invalid type passed to potential.
        """
        if not isinstance(potential, (Potential, Bond)):
            raise TypeError("Tried to add non-potential to a potential containing object")

        self.pots[tuple(atoms)].append(potential)

    def set_potential(self, old_pot: Interaction, new_pot: Interaction):
        """
        Override a potential with a new one.

        Parameters
        ----------
        old_pot : Interaction
            Potential to replace.
        new_pot : Interaction
            Replacement potential.
        """
        for i, curr_pot in enumerate(self.pots[old_pot.atoms]):
            if curr_pot == old_pot:
                self.pots[old_pot.atoms][i] = new_pot
                return

    def get_pot(self,
                species: Optional[Tuple[str, ...]] = None,
                pot_class: Optional[str] = None,
                pot_type: Optional[str] = None,
                quiet: bool = False) -> Iterator[Interaction]:
        """
        Return all pots matching criteria.

        Parameters
        ----------
        species : Optional[Tuple[str, ...]]
            Search by species.
        pot_class : Optional[str]
            Search by pot_class.
        pot_type : Optional[str]
            Search by pot_type.
        quiet : bool
            Print warning if potential not found.

        Returns
        -------
        Interaction
            Potentials matching criteria.
        """
        tests = (("atoms", species), ("pot_class", pot_class), ("pot_type", pot_type))
        out = peek(pot for potSet in self.pots.values() for pot in potSet if
                   all(getattr(pot, prop) == val for prop, val in tests if val is not None)
                   )

        if out is None:
            if not quiet:
                for name, val in tests:
                    if val is not None:
                        print(f"No potentials for {name} {val} found")
            out = ()
        return out

    def get_pot_by_species(self,
                           species: Tuple[str, ...],
                           quiet: bool = False) -> Iterator[Interaction]:
        """
        Return all pots for a given pot species.

        Parameters
        ----------
        species : Tuple[str, ...]
            Search by species.
        quiet : bool
            Print warning if potential not found.

        Returns
        -------
        Iterator[Interaction]
            Potentials matching criteria.
        """
        return self.get_pot(species=species, quiet=quiet)

    def get_pot_by_class(self, pot_class: str, quiet: bool = False) -> Iterator[Interaction]:
        """
        Return all pots for a given pot class.

        Parameters
        ----------
        pot_class : str
            Search by pot_class.
        quiet : bool
            Print warning if potential not found.

        Returns
        -------
        Iterator[Interaction]
            Potentials matching criteria.
        """
        return self.get_pot(pot_class=pot_class, quiet=quiet)

    def get_pot_by_type(self, pot_type: str, quiet: bool = False) -> Iterator[Interaction]:
        """
        Return all pots for a given pot type.

        Parameters
        ----------
        pot_type : Optional[str]
            Search by pot_type.
        quiet : bool
            Print warning if potential not found.

        Returns
        -------
        Iterator[Interaction]
            Potentials matching criteria.
        """
        return self.get_pot(pot_type=pot_type, quiet=quiet)

    def get_num_pot_by_species(self, species: Tuple[str, ...], quiet: bool = False) -> int:
        """
        Return number of pots for a given pot species.

        Parameters
        ----------
        species : Tuple[str, ...]
            Search by species.
        quiet : bool
            Print warning if potential not found.

        Returns
        -------
        int
            Number of potentials matching criteria.
        """
        return len(list(self.get_pot_by_species(species, quiet)))

    def get_num_pot_by_class(self, pot_class: str, quiet: bool = False) -> int:
        """
        Return number of pots for a given pot class.

        Parameters
        ----------
        pot_class : str
            Search by pot_class.
        quiet : bool
            Print warning if potential not found.

        Returns
        -------
        int
            Number of potentials matching criteria.
        """
        return len(list(self.get_pot_by_class(pot_class, quiet)))

    def get_num_pot_by_type(self, pot_type: str, quiet: bool = False) -> int:
        """
        Return number of pots for a given pot type.

        Parameters
        ----------
        pot_type : Optional[str]
            Search by pot_type.
        quiet : bool
            Print warning if potential not found.

        Returns
        -------
        int
            Number of potentials matching criteria.
        """
        return len(list(self.get_pot_by_type(pot_type, quiet)))


class Molecule(PotHaver):
    """
    Class containing molecule field data.

    Attributes
    ----------
    name : str
        Name of molecule.
    n_mols : int
        Number of molecules of `Molecule` in system.
    n_atoms : int
        Number of atoms in molecule.
    species : Dict[str, int]
        Species in molecule.
    pmf_mean_bondlength : Optional[float]
        Mean bondlength determined by pmf.
    """

    def __init__(self):
        """
        Instantiate class containing molecule field data.
        """
        PotHaver.__init__(self)
        self.name = ""
        self.n_mols = 0
        self.n_atoms = 0
        self.species = {}
        self.pmf_mean_bondlength = None

    @property
    def activeBonds(self) -> Iterator[str]:
        """
        List of names of Bond types present in `Molecule`.
        """
        return (name for name in Bond.n_atoms if self.get_num_pot_by_class(name, quiet=True))

    def read(self, field_file: TextIO) -> "Molecule":
        """
        Read a single molecule into class and return itself.

        Parameters
        ----------
        field_file : TextIO
            File to read data from.

        Returns
        -------
        Molecule
            Read molecule.
        """
        self.name = read_line(field_file).strip()
        self.n_mols = int(read_line(field_file).split()[1])
        line = read_line(field_file)
        while line.lower() != "finish":
            if line.lower().split()[0] == "pmf":
                self.pmf_mean_bondlength = float(line.split()[1])
                self._read_pmf(field_file)
            else:
                pot_class, n_pots = line.split()
                pot_class = pot_class.lower()
                n_pots = int(n_pots)
                self._read_block(field_file, pot_class, n_pots)
            line = read_line(field_file)
        return self

    def get_masses(self) -> List[List[float]]:
        """
        Get all masses from molecule.

        Returns
        -------
        List[List[float]]
            Masses of elements.
        """
        masses = [[spec.mass] * spec.repeats for spec in self.species.values()]
        return masses

    def get_charges(self):
        """
        Get all charges from molecule.

        Returns
        -------
        List[List[float]]
            Charges of elements.
        """
        charges = [[spec.charge] * spec.repeats for spec in self.species.values()]
        return charges

    def write(self, out_file: TextIO):
        """
        Write to `out_file` (called by `Field`).

        Parameters
        ----------
        out_file : TextIO
            File to write data to.
        """
        print(self.name, file=out_file)
        print(f"nummols {self.n_mols}", file=out_file)
        print(f"atoms {self.n_atoms}", file=out_file)
        for element in self.species.values():
            print(element, file=out_file)

        for pot_class in self.activeBonds:
            pots = list(self.get_pot_by_class(pot_class, quiet=True))
            print(f"{pot_class} {len(pots)}", file=out_file)
            for pot in pots:
                print(pot, file=out_file)
        print("finish", file=out_file)

    def _read_block(self,
                    field_file: TextIO,
                    pot_class: BondTypes,
                    n_pots: int):
        """
        Read a potentials block.

        Parameters
        ----------
        field_file : TextIO
            File to read.
        pot_class : BondTypes
            Potential class being read.
        n_pots : int
            Number of potentials in block.
        """
        if pot_class.lower() == "atoms":
            self.n_atoms = n_pots
            self._read_atoms(field_file, n_pots)
            return

        for _ in range(n_pots):
            args = read_line(field_file).split()
            pot = Bond(pot_class, args)
            self.add_potential(pot.atoms, pot)

    def _read_pmf(self, field_file: TextIO):
        """
        Read the two pmf unit blocks.

        Parameters
        ----------
        field_file : TextIO
            File to read PMF from.
        """
        unit_1 = read_line(field_file).lower().split()
        n_atoms = int(unit_1[2])
        self._read_pmf_unit(field_file, n_atoms)

        unit_2 = read_line(field_file).lower().split()
        n_atoms = int(unit_2[2])
        self._read_pmf_unit(field_file, n_atoms)

    def _read_pmf_unit(self, field_file: TextIO, n_atoms: int):
        """
        Read an individual pmf unit block.

        Parameters
        ----------
        field_file : TextIO
            File to read PMF from.
        n_atoms : int
            Number of atoms in PMF block.
        """
        for _ in range(n_atoms):
            # weight may be omitted
            site, *weight = read_line(field_file).split()
            args = [site] + (weight if weight else [0.0])
            pot = Bond("pmf", args)
            self.add_potential(pot.atoms, pot)

    def _read_atoms(self, field_file: TextIO, n_atoms: int):
        """
        Read atoms in block.

        Parameters
        ----------
        field_file : TextIO
            File to read from.
        n_atoms : int
            Number of atoms in block.
        """
        atom = 0
        index = 0
        while atom < n_atoms:
            name, mass, charge, *repeats_frozen = read_line(field_file).split()

            repeats_frozen = tuple(map(int, repeats_frozen))
            if not repeats_frozen:
                repeats, frozen = 1, 0
            elif len(repeats_frozen) == 1:
                repeats, frozen = repeats_frozen[0], 0
            elif len(repeats_frozen) == 2:
                repeats, frozen = repeats_frozen
            else:
                repeats, frozen, *_ = repeats_frozen

            repeats = int(repeats)
            self.species[index] = Species(name, len(self.species),
                                          float(charge), float(mass), frozen, repeats)
            atom += repeats
            index += 1


class _PotList:  # pylint: disable=too-few-public-methods,attribute-defined-outside-init
    """
    List of potentials with given type.
    """
    def __set_name__(self, owner, name):
        if name == "tersoffs":
            name = "ters"
        elif name == "tersoffcrosses":
            name = "ters-cross"
        elif name == "vdwstab":
            name = "tabvdw"
        else:
            name = name[:-1]  # Strip "s"
        self.pot_name = name

    def __get__(self, obj, objtype=None):
        return list(obj.get_pot_by_class(self.pot_name))


class _PotCount:  # pylint: disable=too-few-public-methods,attribute-defined-outside-init
    """
    Number of potentials with given type.
    """
    def __set_name__(self, owner, name):
        self.pot_name = name[1:].lower()  # Strip "n"

    def __get__(self, obj, objtype=None):
        return len(getattr(obj, self.pot_name))


class Field(PotHaver):
    """
    Class containing DLPoly FIELD data.

    Attributes
    ----------
    header : str
        Initial comment for Field.
    units : Literal["internal", "kcal/mol", "kJ/mol"]
        Energy units in Field.
    molecules : Dict[str, Molecule]
        Dictionary of `Molecule` by name.
    """

    def __init__(self, source: OptPath = None):
        """
        Instantiate class containing DLPoly FIELD data.

        Parameters
        ----------
        source : OptPath
            File to read from.
        """
        PotHaver.__init__(self)
        self.header = ""
        self.units = "internal"
        self.molecules: Dict[str, Molecule] = {}
        if source is not None:
            self.source = source
            self.read(self.source)

    vdws = _PotList()
    vdwstab = _PotList()
    metals = _PotList()
    rdfs = _PotList()
    kihss = _PotList()
    tbps = _PotList()
    fbps = _PotList()
    externs = _PotList()
    tersoffs = _PotList()
    tersoffcrosses = _PotList()
    kim_model = None
    kim_interactions = None

    nMolecules = _PotCount()
    nVdws = _PotCount()
    nVdwsTab = _PotCount()
    nMetals = _PotCount()
    nRdfs = _PotCount()
    nTersoffs = _PotCount()
    nTersoffCrosses = _PotCount()
    nKihss = _PotCount()
    nTbps = _PotCount()
    nFbps = _PotCount()
    nExterns = _PotCount()

    @property
    def activePots(self) -> Iterator[str]:
        """
        Generator of all `Interaction` names in `Field`.
        """
        return (name for name in Potential.n_atoms
                if self.get_num_pot_by_class(name, quiet=True))

    @property
    def species(self) -> Dict[str, str]:
        """
        Dictionary of `Species` by name.
        """
        return {spec.element: spec
                for mol in self.molecules.values()
                for spec in mol.species.values()}

    @property
    def potSpecies(self) -> Set[str]:
        """
        Set of `Species` involved in potentials.
        """
        return {spec for specPairs in self.pots
                for spec in specPairs}

    def _read_block(self, field_file: TextIO, pot_class: PotentialTypes, n_pots: int):
        """
        Read a potentials block.

        Parameters
        ----------
        field_file : TextIO
            File to read from.
        pot_class : PotentialTypes
            Class of potential being read.
        n_pots : int
            Number of potentials to read.
        """
        if pot_class == "tersoff":
            self._read_tersoff(field_file, n_pots)
            return
        if 'vdwtab' in pot_class:
            pot_class = 'vdwtab'
        for pot in range(n_pots):
            args = field_file.readline().split()
            pot = Potential(pot_class, args)
            self.add_potential(pot.atoms, pot)

    def _parse_kim(self, line: str):
        """
        Parse an OpenKIM key

        Parameters
        ----------
        line : str
            The OpenKIM line to parse.

        Raises
        ------
        Exception
            If line is not kim_init or kim_interactions.
        """
        key, value = line.split()
        if key.lower() == "kim_init":
            self.kim_model = value
        elif key.lower() == "kim_interactions":
            self.kim_interactions = value.split(" ")
        else:
            raise Exception(f"Malformed OpenKIM entry {line}. Only 'kim_init' or 'kim_interactions' are allowed.")

    def _read_tersoff(self, field_file: TextIO, n_pots: int):
        """
        Read a tersoff set (different to standard block).

        Parameters
        ----------
        field_file : TextIO
            File to read from.
        n_pots : int
            Number of tersoffs to read.

        Raises
        ------
        Exception
            Both kihs and ters blocks present.
        """
        tersoff_type = None
        # must have n entries for kihs or ters
        for _ in range(n_pots):
            record_1 = field_file.readline().split()
            record_2 = field_file.readline().split()
            if tersoff_type is None:
                tersoff_type = record_1[1]
            elif tersoff_type != record_1[1]:
                raise Exception("Mixed or incorrect tersoff types, expect one of ters or kihs")

            args = [arg for arg in record_1 if arg != tersoff_type]
            for arg in record_2:
                args.append(arg)

            if tersoff_type == "kihs":
                record_3 = field_file.readline().split()
                for arg in record_3:
                    args.append(arg)

            pot = Potential(tersoff_type, args)
            self.add_potential(pot.atoms, pot)

        # now handle ters's cross terms
        if tersoff_type == "ters":
            count = int(n_pots * (n_pots + 1) / 2)
            for _ in range(count):
                args = field_file.readline().split()
                pot = Potential("ters-cross", args)
                self.add_potential(pot.atoms, pot)

    def add_molecule(self, molecule: Molecule, count: int = 1) -> Tuple[str, int]:
        """
        Add molecule to Field.

        Parameters
        ----------
        molecule : Molecule
            Molecule to add.
        count : int
            Number of molecules to add.

        Returns
        -------
        Tuple[str, int]
            Name and count of molecules after addition.
        """
        if molecule.name not in self.molecules:
            self.molecules[molecule.name] = molecule
        self.molecules[molecule.name].n_mols += count

        return molecule.name, self.molecules[molecule.name].n_mols

    def read(self, field_file: PathLike = "FIELD"):
        """
        Read DLPoly Field file into data.

        Parameters
        ----------
        field_file : PathLike
            File to read from.
        """
        with open(field_file, "r", encoding="utf-8") as in_file:
            # Header *must* be first line?
            self.header = in_file.readline().strip()
            units = read_line(in_file).split()
            if len(units) != 2:
                key, self.units = 'UNITS', 'internal'
            else:
                key, self.units = units
            line = read_line(in_file)
            while line.lower() != "close":
                if line.lower().startswith('kim'):
                    self._parse_kim(line)
                else:
                    key, *n_vals = line.lower().split()
                    n_vals = int(n_vals[-1]) if len(n_vals) else 1
                    if key.startswith("molecul"):
                        for _ in range(n_vals):
                            # Molecule sets its own count
                            self.add_molecule(Molecule().read(in_file), 0)
                    else:
                        self._read_block(in_file, key, n_vals)
                line = read_line(in_file)

            if ((self.kim_model is not None) != (self.kim_interactions is not None)):
                raise Exception('Either both kim_init and kim_interactions, or neither is valid.')

    def write(self, field_file: PathLike = "FIELD"):
        """
        Write data to DLPoly field file.

        Parameters
        ----------
        field_file : PathLike
            File to write to.
        """
        with open(field_file, "w", encoding="utf-8") as out_file:
            print(self.header, file=out_file)
            print(f"units {self.units}", file=out_file)
            print(f"molecules {self.nMolecules}", file=out_file)

            for molecule in self.molecules.values():
                molecule.write(out_file)

            if (self.kim_model is not None and self.kim_interactions is not None):
                print(f"kim_init {self.kim_model}", file=out_file)
                print(f"kim_interactions {' '.join(self.kim_interactions)}")

            for pot_class in self.activePots:
                pots = list(self.get_pot_by_class(pot_class, quiet=True))
                print(f"{pot_class} {len(pots)}", file=out_file)
                for pot in pots:
                    print(pot, file=out_file)
            print("close", file=out_file)

    def __str__(self) -> str:
        return ("[" +
                ", \n".join(molecule.name for molecule in self.molecules.values())
                + "]")


if __name__ == "__main__":
    FLD = Field("FIELD")
    FLD.write("geoff")
