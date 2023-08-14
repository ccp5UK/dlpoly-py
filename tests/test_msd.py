#!/usr/bin/env python3
import unittest
from dlpoly.msd import MSD

import numpy as np


class MSDTest(unittest.TestCase):

    def setUp(self):
        self.msd = MSDTest.msd

    @classmethod
    def setUpClass(cls):
        super(MSDTest, cls).setUpClass()
        cls.msd = MSD(source="tests/MSDTMP")

    def test_msd_init(self):
        self.assertEqual(self.msd.n_atoms, 99120,
                         'incorrect number of atoms')
        self.assertEqual(self.msd.n_frames, 3,
                         'incorrect number of frames')
        self.assertEqual(self.msd.n_species, 19)
        self.assertIsNone(np.testing.assert_array_equal(self.msd.species, np.array(['C', 'C2', 'C3', 'CB',
                                                                                    'CH', 'CK', 'CN', 'CQ',
                                                                                    'CS', 'CZ', 'H', 'HK',
                                                                                    'HO', 'HW', 'N', 'NA',
                                                                                    'O', 'OH', 'OW'], dtype='<U2')))
        self.assertEqual(self.msd.timestep, 0.00025)
        self.assertIsNone(np.testing.assert_array_equal(self.msd.step, np.array([10., 15., 20.])))
        self.assertIsNone(np.testing.assert_array_equal(self.msd.time, np.array([0.003, 0.00425, 0.0055])))

    def test_per_species(self):
        self.assertIsNone(np.testing.assert_array_equal(self.msd.per_species()[-1, :, :],
                                                        np.array([[3.2402125402866667e-02, 1.4425052666666666e+04],
                                                                 [4.3488269886067688e-02, 1.5816330575000000e+04],
                                                                 [4.1494341984733472e-02, 1.5695032131944447e+04],
                                                                 [3.0054512366671875e-02, 1.3486932656249999e+04],
                                                                 [3.8611976171655397e-02, 1.5201000540178573e+04],
                                                                 [3.9407910278891380e-02, 1.5306722526041667e+04],
                                                                 [5.3730257577646254e-02, 1.6590236109375001e+04],
                                                                 [1.3013582540375001e-02, 1.3224479374999999e+04],
                                                                 [1.5163676989500000e-02, 1.3378062500000000e+04],
                                                                 [4.5883100836070306e-02, 1.6195563984375000e+04],
                                                                 [3.7566206840000005e-02, 1.5093892343750002e+04],
                                                                 [3.7997452164981252e-02, 1.5319704718749999e+04],
                                                                 [4.9767547838624998e-02, 1.5742068749999999e+04],
                                                                 [1.0129880048010129e-03, 2.1788526175565491e+02],
                                                                 [5.4517915853917963e-04, 6.7927127578125010e+01],
                                                                 [8.5629846501593756e-04, 9.4098720312500006e+01],
                                                                 [5.9303175352144527e-04, 7.3357309375000000e+01],
                                                                 [1.2162657431193751e-03, 1.2694618750000001e+02],
                                                                 [6.4136960435998060e-04, 7.6009010534739517e+01]])))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(MSDTest('test_msd_init'))
    suite.addTest(MSDTest('test_per_species'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
