#!/usr/bin/env python3
import unittest

from dlpoly import DLPoly
from pathlib import Path
import filecmp
import tempfile


class InputFileTest(unittest.TestCase):

    def test_copy_input(self):

        input_files = ("TABVDW", "TABANG", "TABDIH", "TABINV",
                       "TABBND", "TABEAM", "FIELD", "CONFIG")

        with tempfile.TemporaryDirectory() as work_name:
            work_dir = Path(work_name)

            dlpoly = DLPoly(control="tests/CONTROL",
                            config="tests/CONFIG",
                            field="tests/FIELD",
                            workdir=work_dir,
                            vdw_file="tests/TABVDW",
                            ang_file="tests/TABANG",
                            dih_file="tests/TABDIH",
                            inv_file="tests/TABINV",
                            bnd_file="tests/TABBND",
                            eam_file="tests/TABEAM")

            dlpoly.copy_input()

            for input_file in input_files:
                work_file = work_dir / input_file
                self.assertEqual(dlpoly.control[f"io_file_{input_file.lower()}"], str(work_file))
                self.assertTrue(work_file.is_file(), f"{input_file} i/o failure")
                self.assertTrue(filecmp.cmp(f"tests/{input_file}", work_file, shallow=False))
