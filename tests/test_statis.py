#!/usr/bin/env python3
import unittest
from dlpoly.statis import Statis


class StatisTest(unittest.TestCase):

    def setUp(self):
        self.statis = StatisTest.statis

    @classmethod
    def setUpClass(cls):
        super(StatisTest, cls).setUpClass()
        cls.statis = Statis(source="tests/STATIS")

    def test_statis_ncolumns(self):
        self.assertEqual(self.statis.columns, 69,
                         'incorrect number of columns')

    def test_statis_nrows(self):
        self.assertEqual(self.statis.rows, 5,
                         'incorrect number of rows')

    def test_statis_steptime(self):
        self.assertListEqual(list(self.statis.data[1, 0:2]),
                             [5, 1.750000E-03],
                             'incorrect cell time/step')
    def test_statis_temperature(self):
        self.assertEqual(self.statis.data[2,4], 3.000000E+02 ,
                         'incorrect temperature')

def suite():
    suite = unittest.TestSuite()
    suite.addTest(StatisTest('test_statis_ncolumns'))
    suite.addTest(StatisTest('test_statis_nrows'))
    suite.addTest(StatisTest('test_statis_steptime'))
    suite.addTest(StatisTest('test_statis_temperature'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
