from ase.calculators.calculator import (FileIOCalculator, all_changes)
from ase.io import write, read
from ase.stress import full_3x3_to_voigt_6_stress
from dlpoly import DLPoly
from pint import UnitRegistry


class DLPolyCalculator(FileIOCalculator, DLPoly):

    implemented_properties = ['energy', 'forces', 'stress']
    units = UnitRegistry()
    # these can be pre-calculated
    to_ase_pressure = units('kiloatmosphere').to('electron_volt / angstrom**3').magnitude

    def __init__(self, field=None, control=None, restart=None,
                 ignore_bad_restart_file=FileIOCalculator._deprecated,
                 label='dlpoly', atoms=None, command=None, numProcs=1,
                 **kwargs):

        FileIOCalculator.__init__(self, restart, ignore_bad_restart_file,
                                  label, atoms)

        DLPoly.__init__(self, control=control, field=field, **kwargs)

        self.numProcs = numProcs
        if command is not None:
            self.command = command
            self.exe = command

    def calculate(self, atoms=None, properties=['energy'],
                  system_changes=all_changes):

        if atoms is not None:
            if (self.config is None):
                # nb write does perform unit conversion
                write(self.config_file, atoms, format='dlp4')

            self.run(numProcs=self.numProcs)
            self.load_statis()

            # nb read converts dlp units to ase in velocity and forces
            atoms = read(self.control.io_file_revcon, format='dlp4')

            self.results['energy'] = self.statis.data[-1, 5] * self.units(self.field.units).to('electron_volt')
            self.results['forces'] = atoms.get_forces()
            self.results['stress'] = full_3x3_to_voigt_6_stress(
                self.statis.data[-1, 31:40].reshape((3, 3))
            ) * self.to_ase_pressure
