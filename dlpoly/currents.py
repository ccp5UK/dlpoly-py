'''
Module to handle CURRENTS files
'''

from ruamel.yaml import YAML
import numpy as np


class Currents():

    def __init__(self, source=None):

        self.is_yaml = False
        self.source = source
        self.data = None
        self.atoms = None
        self.timesteps = None

        if source is not None:
            self.source = source
            self.read(source)

    def read(self, source="CURRENTS"):
        with open(source, 'r', encoding='utf-8') as in_file:
            test_word = in_file.readline().split()[0]
            self.is_yaml = test_word == "%YAML"

        if self.is_yaml:
            self._read_yaml(source)
        else:
            self._read_plaintext(source)

    def _read_yaml(self, source):
        self.source = source
        yaml_parser = YAML()

        with open(source, 'rb') as in_file:
            data = yaml_parser.load(in_file)

        times = len(data['timesteps'])

        if times > 0:
            atoms = [k for k in data['timesteps'][0]['atoms'].keys()]
            natoms = len(atoms)

            if natoms > 0:
                kpoints = len(data['timesteps'][0]['atoms'][atoms[0]])
                kpoints = int(kpoints / (2*3))

                self.data = np.zeros((times, natoms, kpoints, 3)).astype(complex)
                self.timesteps = np.zeros(times)
                self.atoms = atoms

                for t in range(times):
                    self.timesteps[t] = data['timesteps'][t]['time']
                    for (i, atom) in enumerate(atoms):
                        points = np.array(data['timesteps'][t]['atoms'][atom]).astype(float)
                        rx = points[0:points.shape[0]:6]
                        ix = points[1:points.shape[0]:6]
                        ry = points[2:points.shape[0]:6]
                        iy = points[3:points.shape[0]:6]
                        rz = points[4:points.shape[0]:6]
                        iz = points[5:points.shape[0]:6]
                        for k in range(kpoints):
                            self.data[t, i, k, 0] = complex(rx[k], ix[k])
                            self.data[t, i, k, 1] = complex(ry[k], iy[k])
                            self.data[t, i, k, 2] = complex(rz[k], iz[k])

    def _read_plaintext(self, source):
        self.source = source
        with open(source) as file:
            lines = [line.rstrip() for line in file]

        timesteps = np.zeros(len(lines))
        atoms = []
        kpoints = 0

        for line in range(len(lines)):
            data = lines[line].split()
            data = [v for v in data if v != ',']
            timesteps[line] = float(data[0].strip(','))
            atoms.append(data[1])
            k = int((len(data)-2)/(2*3))
            if kpoints != 0 and k != kpoints:
                message = f"Inconsistent number of kpoint values in currents file: {source}"
                message = message * f"\n  at line {line}"
                message = message * "\n  "*data
                raise Exception(message)
            kpoints = k

        self.timesteps = np.sort(np.unique(timesteps))
        atoms = [a.strip(',') for a in atoms]
        # unique performs a sort, but we must preserve
        #  the ordering of the file
        self.atoms = []
        for i in range(len(atoms)):
            if (atoms[i] not in self.atoms):
                self.atoms.append(atoms[i])
            else:
                break

        self.data = np.zeros((len(self.timesteps), len(self.atoms), kpoints, 3)).astype(complex)

        line = 0
        if len(self.timesteps) > 0 and len(self.atoms) > 0:
            for t in range(len(self.timesteps)):
                for i in range(len(self.atoms)):
                    data = lines[line].split()
                    data = [v for v in data if v != ',']
                    points = np.array(data[2:len(data)]).astype(float)
                    rx = points[0:points.shape[0]:6]
                    ix = points[1:points.shape[0]:6]
                    ry = points[2:points.shape[0]:6]
                    iy = points[3:points.shape[0]:6]
                    rz = points[4:points.shape[0]:6]
                    iz = points[5:points.shape[0]:6]
                    for k in range(kpoints):
                        self.data[t, i, k, 0] = complex(rx[k], ix[k])
                        self.data[t, i, k, 1] = complex(ry[k], iy[k])
                        self.data[t, i, k, 2] = complex(rz[k], iz[k])
                    line += 1
