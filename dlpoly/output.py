import numpy as np


class output():
    __version__ = "0"

    def __init__(self, source=None):

        self.vdw_energy = None
        self.vdw_pressure = None
        self.steps = None
        self.average_steps = None
        self.time = None  # in ps
        self.average_time = None
        self.run_time = None
        self.run_tps = None
        self.average = None
        self.pressure = None
        self.pressure_tensor = None
        self.pressure_tensor_rms = None
        self.average_cell = None
        self.average_cell_rms = None
        self.diffusion = None

        if source is not None:
            self.source = source
            self.read(source)

    def type_3x3(self, label, a):
        out = "{}: \n".format(label)
        for i in range(3):
            out += "{:16.8e} {:16.8e} {:16.8e}\n".format(a[i, 0], a[i, 1], a[i, 2])
        return out

    def __str__(self):
        outStr = ''
        if self.vdw_energy is not None:
            outStr += "long range vdw energy correction: {} donkeys\n".format(self.vdw_energy)
            outStr += "long range vdw pressure correction: {} donkeys\n".format(self.vdw_pressure)
        outStr += "runtime for md loop: {} s\n".format(self.run_time)
        outStr += "time per md step: {} s\n".format(self.run_tps)
        outStr += "md steps: {}\n".format(self.steps)
        outStr += "md steps for average: {}\n".format(self.average_steps)
        outStr += "md simulation time: {} ps\n".format(self.time)
        outStr += "md simulation time for average: {} ps\n".format(self.average_time)
        if self.average is not None:
            outStr += "Averages: \n"
            outStr += "#{:16s} {:>16s} {:>16s} \n".format("name", "value", "rms")
            for k, v in self.average.items():
                outStr += " {:16s} {:16.8e} {:16.8e}\n".format(k, *v)
            outStr += "\n"
        if self.diffusion is not None:
            outStr += "Approximate 3D Diffusion Coefficients and square root of MSDs:\n"
            outStr += "#{:16s} {:>20s} {:>16s} \n".format("Specie", "DC [10^-9 m^2 s^-1]", "Sqrt(MSD) [Å]")
            for k, v in self.diffusion.items():
                outStr += " {:16s}     {:16.8e} {:16.8e}\n".format(k, *v)
            outStr += "\n"
        if self.pressure_tensor is not None:
            outStr += self.type_3x3("Average pressure tensor [katm]: ", self.pressure_tensor)
            outStr += self.type_3x3("Average pressure tensor rms [katm]: ", self.pressure_tensor_rms)
            outStr += "pressure (trace/3) [katm]: {}\n".format(self.pressure)
        if self.average_cell is not None:
            outStr += self.type_3x3("Average cell vectors [Å]: ", self.average_cell)
            outStr += self.type_3x3("Average cell vectors rms [Å]: ", self.average_cell_rms)
        return outStr

    def read(self, source="OUTPUT"):
        """ Read an OUTPUT file into memory """

        with open(source, 'r') as f:
            line = f.readline()
            while line:
                line = f.readline()
                a = line.strip().split()
                if len(a) == 0:
                    continue
                if a[0] == 'vdw':
                    if a[1] == 'energy':
                        self.vdw_energy = float(a[2])
                    if a[1] == 'pressure':
                        self.vdw_pressure = float(a[2])
                    continue
                if a[0] == 'run':
                    self.steps = int(a[3])
                    self.time = float(a[6])
                    self.average_steps = int(a[12])
                    self.average_time = float(a[15])
                    dline = f.readline()
                    h = []
                    for i in range(3):
                        h += f.readline().strip().split()[1:]
                    h = h[0:18] + h[20:]
                    dline = f.readline()
                    v = []
                    for i in range(3):
                        v += [float(j) for j in f.readline().strip().split()[1:]]
                    dline = f.readline()
                    rms = []
                    for i in range(3):
                        rms += [float(j) for j in f.readline().strip().split()[1:]]
                    self.average = {l: (a, b) for (l, a, b) in zip(h, v, rms)}
                    continue
                if a[0] == 'Loop':
                    self.run_time = float(a[6])
                    self.run_tps = float(a[11])
                    continue
                if a[0] == 'Pressure':
                    dline = f.readline()
                    self.pressure_tensor = np.zeros((3, 3))
                    self.pressure_tensor_rms = np.zeros((3, 3))
                    for i in range(3):
                        a = [float(j) for j in f.readline().strip().split()]
                        self.pressure_tensor[i, :] = np.array(a[0:3])
                        self.pressure_tensor_rms[i, :] = np.array(a[3:6])
                    self.pressure = float(f.readline().strip().split()[1])
                    continue
                if a[0] == 'Approximate':
                    dline = f.readline()
                    h = []
                    while True:
                        dline = f.readline().strip().split()
                        if len(dline) == 0:
                            break
                        h += [dline]
                    self.diffusion = {e[0]: (float(e[1]), float(e[2])) for e in h}
                    continue
                if a[0] == 'Average':
                    self.average_cell = np.zeros((3, 3))
                    self.average_cell_rms = np.zeros((3, 3))
                    for i in range(3):
                        a = [float(j) for j in f.readline().strip().split()]
                        self.average_cell[i, :] = np.array(a[0:3])
                        self.average_cell_rms[i, :] = np.array(a[3:6])
                    continue


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        output = output(sys.argv[1])
    else:
        output = output("OUTPUT")
