'''
Module to handle CURRENTS files
'''

from typing import Optional, List

from ruamel.yaml import YAML
import numpy as np

from .types import PathLike, OptPath


class Currents():

    def __init__(self, source: OptPath = None):

        self.is_yaml = False
        self.source = source
        self.data: Optional[np.typing.NDArray] = None
        self.atoms: Optional[List[str]] = None
        self.timesteps: Optional[np.typing.NDArray] = None

        if source is not None:
            self.source = source
            self.read(source)

    def read(self, source: PathLike = "CURRENTS"):
        with open(source, 'r', encoding='utf-8') as in_file:
            test_word = in_file.readline().split()[0]
            self.is_yaml = test_word == "%YAML"

        if self.is_yaml:
            self._read_yaml(source)
        else:
            self._read_plaintext(source)

    def _read_yaml(self, source: PathLike):
        self.source = source
        yaml_parser = YAML()

        with open(source, 'rb') as in_file:
            data = yaml_parser.load(in_file)

        times = len(data['timesteps'])

        if times > 0:
            atoms = list(data['timesteps'][0]['atoms'].keys())
            natoms = len(atoms)

            if natoms > 0:
                kpoints = len(data['timesteps'][0]['atoms'][atoms[0]])
                kpoints = kpoints // (2*3)

                self.data = np.zeros((times, natoms, kpoints, 3), dtype=complex)
                self.timesteps = np.zeros(times)
                self.atoms = atoms

                for timestep in range(times):
                    curr_data = data['timesteps'][timestep]
                    self.timesteps[timestep] = curr_data['time']
                    for ind, atom in enumerate(atoms):
                        points = np.array(curr_data['atoms'][atom], dtype=float)
                        rx = points[0:points.shape[0]:6]
                        ix = points[1:points.shape[0]:6]
                        ry = points[2:points.shape[0]:6]
                        iy = points[3:points.shape[0]:6]
                        rz = points[4:points.shape[0]:6]
                        iz = points[5:points.shape[0]:6]
                        for k in range(kpoints):
                            self.data[timestep, ind, k, 0] = complex(rx[k], ix[k])
                            self.data[timestep, ind, k, 1] = complex(ry[k], iy[k])
                            self.data[timestep, ind, k, 2] = complex(rz[k], iz[k])

    def _read_plaintext(self, source: PathLike):
        self.source = source
        with open(source, "r", encoding="utf-8") as file:
            lines = [line.rstrip().replace(",", " ") for line in file]

        timesteps = np.zeros(len(lines))
        atoms = []
        kpoints = 0

        for i, line in enumerate(lines):
            data = line.split()
            timesteps[i] = float(data[0])
            atoms.append(data[1])
            k = (len(data)-2)//(2*3)
            if kpoints not in (0, k):
                raise Exception(f"""Inconsistent number of kpoint values in currents file: {source}
  at line {i}
  {data}""")
            kpoints = k

        self.timesteps = np.sort(np.unique(timesteps))

        # unique performs a sort, but we must preserve
        #  the ordering of the file
        self.atoms = []
        for atom in atoms:
            if atom in self.atoms:
                break
            self.atoms.append(atom)

        self.data = np.zeros((len(self.timesteps),
                              len(self.atoms),
                              kpoints,
                              3), dtype=complex)

        line_no = 0
        if len(self.timesteps) > 0 and len(self.atoms) > 0:
            for timestep in range(len(self.timesteps)):
                for ind in range(len(self.atoms)):
                    data = lines[line_no].split()
                    points = np.array(data[2:len(data)]).astype(float)
                    rx = points[0:points.shape[0]:6]
                    ix = points[1:points.shape[0]:6]
                    ry = points[2:points.shape[0]:6]
                    iy = points[3:points.shape[0]:6]
                    rz = points[4:points.shape[0]:6]
                    iz = points[5:points.shape[0]:6]
                    for k in range(kpoints):
                        self.data[timestep, ind, k, 0] = complex(rx[k], ix[k])
                        self.data[timestep, ind, k, 1] = complex(ry[k], iy[k])
                        self.data[timestep, ind, k, 2] = complex(rz[k], iz[k])
                    line_no += 1
