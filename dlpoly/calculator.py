"""
DLPoly ASE Calculator
"""

from os import PathLike
from typing import Literal, Optional, Sequence

from ase import Atoms
from ase.calculators.calculator import FileIOCalculator, all_changes
from ase.io import read, write
from ase.stress import full_3x3_to_voigt_6_stress
from pint import UnitRegistry

from dlpoly import DLPoly


class DLPolyCalculator(FileIOCalculator, DLPoly):
    """
    Calculator using DLPoly for ASE
    """
    implemented_properties = ['energy', 'forces', 'stress']
    units = UnitRegistry()
    # these can be pre-calculated
    to_ase_pressure = units('kiloatmosphere').to('electron_volt / angstrom**3').magnitude

    def __init__(self, field: Optional[PathLike] = None, control:
                 Optional[PathLike] = None, restart: Optional[bool] = None,
                 ignore_bad_restart_file: bool = FileIOCalculator._deprecated,
                 label: str = 'dlpoly', atoms: Optional[Atoms] = None,
                 command: Optional[str] = None,
                 numProcs: int = 1, **kwargs):

        FileIOCalculator.__init__(self, restart, ignore_bad_restart_file,
                                  label, atoms)

        DLPoly.__init__(self, control=control, field=field, **kwargs)

        self.numProcs = numProcs
        if command is not None:
            self.command = command
            self.exe = command

    def calculate(self, atoms: Optional[Atoms] = None,
                  properties: Sequence[Literal['energy', 'forces', 'stress']] = ('energy',),
                  system_changes: Sequence[str] = tuple(all_changes)):

        if atoms is not None:
            if self.config is None:
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
