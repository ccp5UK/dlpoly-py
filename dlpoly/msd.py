'''
Module to handle MSDTMP config files
'''
import numpy as np


class MSD():
    """Class relating to MSD data

    :param source: File to read
    """

    def __init__(self, source=None):
        self.n_frames = 0
        self.n_atoms = 0
        self.data = None
        self.latom = []
        self.timestep = 0
        self.step = None
        self.time = None
        self.title = ""
        self.species = None

        if source is not None:
            self.source = source
            self.read(source)

    @property
    def n_species(self):
        return len(self.species)

    def per_species(self):
        """List by species

        :returns: List of species averages
        :rtype: np.ndarray

        """
        data = np.zeros((self.n_frames, self.n_species, 2))
        for i in range(self.n_frames):
            for j, species in enumerate(self.species):
                m = [x == species for x in self.latom[i]]
                data[i, j, 0] = np.average(self.data[i, m, 0])
                data[i, j, 1] = np.average(self.data[i, m, 1])

        return data

    def read(self, filename="MSDTMP"):
        """Read an MSDTMP file

        :param filename: File to read

        """

        with open(filename, "r", encoding="utf-8") as in_file:
            data_in = map(lambda x: x.strip().split(), iter(in_file))

            self.title = next(data_in)[0]
            self.n_atoms, self.n_frames, _ = map(int, next(data_in))

            self.data = np.zeros((self.n_frames, self.n_atoms, 2))
            self.step = np.zeros(self.n_frames)
            self.time = np.zeros(self.n_frames)

            for i in range(self.n_frames):
                header = next(data_in)
                self.step[i] = int(header[1])
                self.timestep = float(header[3])
                self.time[i] = float(header[4])
                frame_species = []
                for j in range(self.n_atoms):
                    species, _, mean_sq, t = next(data_in)
                    self.data[i, j, :] = float(mean_sq)**2, float(t)
                    frame_species.append(species)
                self.latom.append(np.sort(frame_species))
        # nb now np.sort(np.unique()), as set() can have non-deterministic behaviour on
        #   non deterministic input (an issue for unit tests)
        #   https://stackoverflow.com/questions/51927850/is-set-deterministic
        self.species = np.sort(np.unique(self.latom[0]))

        return self
