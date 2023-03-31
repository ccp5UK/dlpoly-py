""" Module containing data related to parsing output """
import numpy as np


class Output():
    """Class containing parsed OUTPUT data

     :param source: OUTPUT file to read

     """
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

    @staticmethod
    def type_3x3(label, data):
        """Print as 3x3 block

        :param label: Label to print
        :param a: Value stored

        """
        out = f"{label}: \n"
        for i in range(3):
            out += f"{data[i, 0]:16.8e} {data[i, 1]:16.8e} {data[i, 2]:16.8e}\n"
        return out

    def __str__(self):
        out_str = ''
        if self.vdw_energy is not None:
            out_str += f"long range vdw energy correction: {self.vdw_energy} donkeys\n"
            out_str += f"long range vdw pressure correction: {self.vdw_pressure} donkeys\n"

        out_str += f"runtime for md loop: {self.run_time} s\n"
        out_str += f"time per md step: {self.run_tps} s\n"
        out_str += f"md steps: {self.steps}\n"
        out_str += f"md steps for average: {self.average_steps}\n"
        out_str += f"md simulation time: {self.time} ps\n"
        out_str += f"md simulation time for average: {self.average_time} ps\n"

        if self.average is not None:
            out_str += "Averages: \n"
            out_str += f"#{'name':16s} {'value':>16s} {'rms':>16s}\n"
            for key, value in self.average.items():
                out_str += f" {key:16s} {value[0]:16.8e} {value[1]:16.8e}\n"
            out_str += "\n"

        if self.diffusion is not None:
            out_str += "Approximate 3D Diffusion Coefficients and square root of MSDs:\n"
            out_str += f"#{'Species':16s} {'DC [10^-9 m^2 s^-1]':>20s} {'Sqrt(MSD) [Å]':>16s} \n"
            for key, value in self.diffusion.items():
                out_str += " {key:16s}     {value[0]:16.8e} {value[1]:16.8e}\n"
            out_str += "\n"

        if self.pressure_tensor is not None:
            out_str += self.type_3x3("Average pressure tensor [katm]: ",
                                     self.pressure_tensor)
            out_str += self.type_3x3("Average pressure tensor rms [katm]: ",
                                     self.pressure_tensor_rms)
            out_str += f"pressure (trace/3) [katm]: {self.pressure}\n"

        if self.average_cell is not None:
            out_str += self.type_3x3("Average cell vectors [Å]: ", self.average_cell)
            out_str += self.type_3x3("Average cell vectors rms [Å]: ", self.average_cell_rms)
        return out_str

    def read(self, source="OUTPUT"):
        """ Read an OUTPUT file into memory

        :param source: File to read

        """
        with open(source, 'r', encoding="utf-8") as in_file:
            to_read = iter(in_file)
            to_read = map(lambda line: line.strip().split(), to_read)

            for line in to_read:
                if not line:
                    continue

                key, *values = line

                if key == 'vdw':
                    typ, val, *_ = values
                    if typ == 'energy':
                        self.vdw_energy = float(val)
                    elif typ == 'pressure':
                        self.vdw_pressure = float(val)

                elif key == 'run':
                    self.steps = int(values[2])
                    self.time = float(values[5])
                    self.average_steps = int(values[11])
                    self.average_time = float(values[14])
                    next(to_read)

                    headers = [val for _, arr in zip(range(3), to_read) for val in arr]
                    del headers[19]
                    next(to_read)

                    vals = [float(val) for _, arr in zip(range(3), to_read) for val in arr[1:]]
                    next(to_read)

                    rmss = [float(val) for _, arr in zip(range(3), to_read) for val in arr[1:]]

                    self.average = {header: (val, rms)
                                    for (header, val, rms) in zip(headers, vals, rmss)}

                elif key == 'Loop':
                    self.run_time = float(values[5])
                    self.run_tps = float(values[10])

                elif key == 'Pressure':
                    next(to_read)

                    self.pressure_tensor = np.zeros((3, 3))
                    self.pressure_tensor_rms = np.zeros((3, 3))
                    for i in range(3):
                        values = np.array(next(to_read), dtype=float)
                        self.pressure_tensor[i, :] = values[0:3]
                        self.pressure_tensor_rms[i, :] = values[3:6]

                    self.pressure = float(next(to_read)[1])

                elif key == 'Approximate':
                    next(to_read)
                    data = []
                    while line := next(to_read):
                        data.append(line)

                    self.diffusion = {atom: (float(x), float(y)) for atom, x, y in data}

                elif key == 'Average':
                    self.average_cell = np.zeros((3, 3))
                    self.average_cell_rms = np.zeros((3, 3))
                    for i in range(3):
                        values = np.array(next(to_read), dtype=float)
                        self.average_cell[i, :] = values[0:3]
                        self.average_cell_rms[i, :] = values[3:6]


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        OUTPUT = Output(sys.argv[1])
    else:
        OUTPUT = Output("OUTPUT")
