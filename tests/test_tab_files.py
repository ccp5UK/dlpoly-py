#!/usr/bin/env python3
import unittest

from dlpoly import DLPoly
from pathlib import Path


class TabFileTest(unittest.TestCase):

    def setUp(self):
        self.dlpoly = TabFileTest.dlpoly

    @classmethod
    def setUpClass(cls):
        super(TabFileTest, cls).setUpClass()
        cls.dlpoly = DLPoly(control="tests/CONTROL",
                            config="tests/CONFIG",
                            field="tests/FIELD",
                            workdir="tabio",
                            vdw_file="tests/VDW")

    def test_io(self):
        self.assertEqual(self.dlpoly.control.io_file_tabvdw, "tests/VDW")
        self.dlpoly.run()
        self.assertEqual(Path("tabio/VDW").is_file(), True, "TABVDW i/o failure")


def suite():
    suite = unittest.TestSuite()
    suite.addTest(TabFileTest('test_io'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
