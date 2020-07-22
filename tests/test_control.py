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
        self.assertEqual(self.control.steps, 20,
                         'incorrect number of steps')
        self.assertEqual(self.control.equilibration, 10,
                         'incorrect number of equilibratio steps')

    def test_control_tp(self):
        self.assertEqual(self.control.temperature, 300.0,
                         'incorrect temperature')
        self.assertEqual(self.control.press, 0.001,
                         'incorrect pressure')

    def test_control_ens(self):
        self.assertEqual(self.control.ensemble.ensemble, 'npt',
                         'incorrect ensemble')
        self.assertEqual(self.control.ensemble.means, 'hoover',
                         'incorrect ensemble type')
        self.assertListEqual(self.control.ensemble.args,
                             ['0.5', '1.0'],
                             'incorrect ensemble')


def suite():
    suite = unittest.TestSuite()
    suite.addTest(ControlTest('test_control_steps'))
    suite.addTest(ControlTest('test_control_tp'))
    suite.addTest(ControlTest('test_control_ens'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
