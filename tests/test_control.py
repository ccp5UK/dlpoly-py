#!/usr/bin/env python3
import dlpoly as dlp
import unittest


class ControlTest(unittest.TestCase):

    def setUp(self):
        self.control = ControlTest.control

    @classmethod
    def setUpClass(cls):
        super(ControlTest, cls).setUpClass()
        cls.control = dlp.DLPoly(control="tests/CONTROL").control

    def test_control_steps(self):
        self.assertEqual(self.control.timing.steps, 20,
                         'incorrect number of steps')
        self.assertEqual(self.control.timing.equil, 10,
                         'incorrect number of equilibration steps')
        self.assertEqual(self.control.timing.timestep, 0.001,
                         'incorrect timestep step')
        self.assertEqual(self.control.timing.variable, True,
                         'incorrect variable step')

    def test_control_tp(self):
        self.assertEqual(self.control.temp, 300.0,
                         'incorrect temperature')
        self.assertEqual(self.control.pres[0], 0.001,
                         'incorrect pressure')

    def test_control_ens(self):
        self.assertEqual(self.control.ensemble.ensemble, 'npt',
                         'incorrect ensemble')
        self.assertEqual(self.control.ensemble.means, 'hoover',
                         'incorrect ensemble type')
        self.assertListEqual(self.control.ensemble.args,
                             ['0.5', '1.0'],
                             'incorrect ensemble')

    def test_control_prints(self):
        self.assertEqual(self.control.print.statsevery, 5,
                         'incorrect stats frequency')
        self.assertEqual(self.control.print.printevery, 5,
                         'incorrect print frequency')
        self.assertEqual(self.control.print.rdf, True,
                         'incorrect rdf')
        self.assertEqual(self.control.timing.collect, True,
                         'incorrect collect setting')

    def test_control_equil(self):
        self.assertEqual(self.control.cap, 1000.0,
                         'incorrect cap')
        self.assertEqual(self.control.scale, 3,
                         'incorrect scale')
        self.assertEqual(self.control.shake, 0.000001,
                         'incorrect shake')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(ControlTest('test_control_steps'))
    suite.addTest(ControlTest('test_control_tp'))
    suite.addTest(ControlTest('test_control_ens'))
    suite.addTest(ControlTest('test_control_prints'))
    suite.addTest(ControlTest('test_control_equil'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
