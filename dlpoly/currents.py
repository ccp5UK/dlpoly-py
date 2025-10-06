"""
Module to handle CURRENTS files.
"""

from typing import Optional, List

from ruamel.yaml import YAML
import numpy as np

from .types import PathLike, OptPath


class Currents:
    """
    Class for reading Currents.

    Attributes
    ----------
    source : PathLike
        Original file read data from.
    is_yaml : bool
        Whether data are in YAML format.
    density : Optional[np.typing.NDArray]
        k-space density read from file.
    longitudinal : Optional[np.typing.NDArray]
        k-space longitudinal current read from file.
    transverse : Optional[np.typing.NDArray]
        k-space transverse current read from file.
    energy_density : Optional[np.typing.NDArray]
        k-space energy-density current
    energy : Optional[np.typing.NDArray]
        k-space energy current read from file.
    stress : Optional[np.typing.NDArray]
        k-dependent stress tensor
    atoms : Optional[List[str]]
        List of atoms from file.
    timesteps : Optional[np.typing.NDArray]
        Timestep samples in file.
    """

    def __init__(self, source: OptPath = None):
        """
        Instantiate class for reading Currents.

        Parameters
        ----------
        source : OptPath
            File to read data from.
        """
        self.is_yaml = False
        self.source = source
        self.density: Optional[np.typing.NDArray] = None
        self.longitudinal: Optional[np.typing.NDArray] = None
        self.transverse: Optional[np.typing.NDArray] = None
        self.energy: Optional[np.typing.NDArray] = None
        self.energy_density: Optional[np.typing.NDArray] = None
        self.stress: Optional[np.typing.NDArray] = None
        self.atoms: Optional[List[str]] = None
        self.timesteps: Optional[np.typing.NDArray] = None

        if source is not None:
            self.source = source
            self.read(source)

    def read(self, source: PathLike = "CURRENTS"):
        """
        Read Currents file in YAML or plaintext format.

        Parameters
        ----------
        source : PathLike
            File to read data from.
        """
        with open(source, "r", encoding="utf-8") as in_file:
            test_word = in_file.readline().split()[0]
            self.is_yaml = test_word == "%YAML"

        if self.is_yaml:
            self._read_yaml(source)
        else:
            self._read_plaintext(source)

    def _read_yaml(self, source: PathLike):
        """
        Read Currents data from YAML format file.

        Parameters
        ----------
        source : PathLike
            File to read data from.
        """
        self.source = source
        yaml_parser = YAML()

        with open(source, "rb") as in_file:
            data = yaml_parser.load(in_file)

        times = len(data["timesteps"])

        if times > 0:
            atoms = list(data["timesteps"][0]["density"])
            natoms = len(atoms)
            has_energy = "stress" in data["timesteps"][0]

            if natoms > 0:
                kpoints = len(data["timesteps"][0]["density"][atoms[0]])
                kpoints //= 2

                self.density = np.zeros((times, natoms, kpoints), dtype=complex)
                self.longitudinal = np.zeros((times, natoms, kpoints, 3), dtype=complex)
                self.transverse = np.zeros((times, natoms, kpoints, 3), dtype=complex)
                self.energy_density = np.zeros((times, natoms, kpoints, 3), dtype=complex)
                if has_energy:
                    self.energy = np.zeros((times, natoms, kpoints, 3), dtype=complex)
                    self.stress = np.zeros((times, natoms, kpoints, 6), dtype=complex)

                self.timesteps = np.zeros(times)
                self.atoms = atoms

                for timestep in range(times):
                    curr_data = data["timesteps"][timestep]
                    self.timesteps[timestep] = curr_data["time"]
                    density = curr_data["density"]
                    longitudinal = curr_data["longitudinal"]
                    transverse = curr_data["transverse"]
                    energy_density = curr_data["energy_density"]
                    if has_energy:
                        stress = curr_data["stress"]
                        energy = curr_data["energy"]

                    for ind, atom in enumerate(atoms):
                        self.density[timestep, ind, :] = _unpack_complex(density[atom], 1)
                        self.longitudinal[timestep, ind, :, :] = _unpack_complex(
                            longitudinal[atom], 3
                        )
                        self.transverse[timestep, ind, :, :] = _unpack_complex(transverse[atom], 3)
                        self.energy_density[timestep, ind, :, :] = _unpack_complex(
                            energy_density[atom], 3
                        )
                        if has_energy:
                            self.energy[timestep, ind, :, :] = _unpack_complex(energy[atom], 3)
                            self.stress[timestep, ind, :, :] = _unpack_complex(stress[atom], 6)

    def _read_plaintext(self, source: PathLike):
        """
        Read Currents data from plain-text format file.

        Parameters
        ----------
        source : PathLike
            File to read data from.

        Raises
        ------
        Exception
            If k-point samples are inconsistent.
        """
        self.source = source
        with open(source, "r", encoding="utf-8") as file:
            lines = [line.rstrip().replace(",", " ") for line in file]

        if len(lines) < 4:
            return

        kpoints = len(lines[0].split()) // 2 - 1

        header = lines[0 : min(5, len(lines))]
        has_energy = header[-1].split()[1] == header[-2].split()[1]

        unique_atoms = set()
        for line in lines:
            unique_atoms.add(line.split()[1])

        natoms = len(unique_atoms)
        entries = 6 if has_energy else 4
        nsteps = (len(lines) // natoms) // entries

        header = lines[0 : entries * natoms]
        self.atoms = []
        for i in range(0, len(header), entries):
            self.atoms.append(header[i].split()[1])

        line_no = 0

        self.density = np.zeros((nsteps, natoms, kpoints), dtype=complex)
        self.longitudinal = np.zeros((nsteps, natoms, kpoints, 3), dtype=complex)
        self.transverse = np.zeros((nsteps, natoms, kpoints, 3), dtype=complex)
        self.energy_density = np.zeros((nsteps, natoms, kpoints, 3), dtype=complex)
        self.timesteps = np.zeros(nsteps)
        if has_energy:
            self.energy = np.zeros((nsteps, natoms, kpoints, 3), dtype=complex)
            self.stress = np.zeros((nsteps, natoms, kpoints, 6), dtype=complex)
        for timestep in range(nsteps):
            for ind in range(len(self.atoms)):
                self.timesteps[timestep] = lines[line_no].split()[0]
                data = [
                    np.array(line.split()[2:]).astype(float)
                    for line in lines[line_no : line_no + entries]
                ]
                self.density[timestep, ind, :] = _unpack_complex(data[0], 1)
                self.longitudinal[timestep, ind, :, :] = _unpack_complex(data[1], 3)
                self.transverse[timestep, ind, :, :] = _unpack_complex(data[2], 3)
                self.energy_density[timestep, ind, :, :] = _unpack_complex(data[3], 3)
                if has_energy:
                    self.stress[timestep, ind, :, :] = _unpack_complex(data[4], 6)
                    self.energy[timestep, ind, :, :] = _unpack_complex(data[5], 3)
                line_no += entries


def _unpack_complex(data: list[float], components: int = 1) -> np.typing.NDArray:
    """
    Unpack column major packed complex data.

    Parameters
    ----------
    data : list[float]
        Complex data in column major order

    Returns
    -------
    np.typing.NDArray
        Unpacked complex data
    """
    data = np.array(data)
    if components == 1:
        return data[0::2] + 1j * data[1::2]
    cdata = data[0::2] + 1j * data[1::2]
    unpacked = np.zeros((len(cdata) // components, components), dtype=complex)
    for cmp in range(components):
        unpacked[:, cmp] = cdata[cmp::components]
    return unpacked
