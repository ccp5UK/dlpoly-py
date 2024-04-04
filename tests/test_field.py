#!/usr/bin/env python3
import unittest
import dlpoly as dlp


class FieldTest(unittest.TestCase):

    def setUp(self):
        self.field = FieldTest.field
        self.field_ters = FieldTest.field_ters

    @classmethod
    def setUpClass(cls):
        super(FieldTest, cls).setUpClass()
        cls.field = dlp.DLPoly(field="tests/FIELD").field
        cls.field_ters = dlp.DLPoly(field="tests/FIELD.ters").field

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


def suite():
    suite = unittest.TestSuite()
    suite.addTest(FieldTest('test_field_units'))
    suite.addTest(FieldTest('test_field_mol'))
    suite.addTest(FieldTest('test_field_ters'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
