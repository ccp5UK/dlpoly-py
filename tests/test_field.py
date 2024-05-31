#!/usr/bin/env python3
import unittest
from pathlib import Path

import dlpoly.field as dlp

DATA_PATH = Path(__file__).parent


class FieldTest(unittest.TestCase):
    field = dlp.Field(DATA_PATH / "FIELD")
    field_ters = dlp.Field(DATA_PATH / "FIELD.ters")

    def test_field_units(self):
        self.assertEqual(self.field.units, "kcal",
                         'incorrect units in FIELD')
        self.assertEqual(self.field_ters.units, "ev",
                         'incorrect units in FIELD.ters')

    def test_field_mol(self):
        self.assertEqual(self.field.molecules['Gramicidin A'].n_mols, 8,
                         'incorrect number of gramidicin')
        self.assertEqual(self.field.molecules['Gramicidin A'].n_atoms, 354,
                         'incorrect number of atoms in gramidicin')

    def test_field_ters(self):
        self.assertEqual(len(self.field_ters.pots), 5,
                         'incorrect number of tersoff potentials')
        self.assertEqual(self.field_ters.pots[('C',)][0].pot_class, 'ters',
                         'missing tersoff single params')
        self.assertEqual(self.field_ters.pots[('C', 'C')][0].pot_class, 'ters-cross',
                         'missing tersoff cross params')
        self.assertEqual(self.field_ters.nTersoffs, 2,
                         'incorrect number of Tersoffs potentials')
        self.assertEqual(self.field_ters.nTersoffCrosses, 3,
                         'incorrect number of Tersoff cross potentials')
        self.assertEqual(self.field_ters.nKihss, 0,
                         'incorrect number of Tersoff KIHS potentials')


if __name__ == '__main__':
    unittest.main()
