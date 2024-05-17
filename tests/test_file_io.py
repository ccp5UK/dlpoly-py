import filecmp
import tempfile
import unittest
from pathlib import Path

from dlpoly import DLPoly

DATA_PATH = Path(__file__).parent


class InputFileTest(unittest.TestCase):

    def test_copy_input(self):

        input_files = ("TABVDW", "TABANG", "TABDIH", "TABINV",
                       "TABBND", "TABEAM", "FIELD", "CONFIG")

        with tempfile.TemporaryDirectory() as work_name:
            work_dir = Path(work_name)

            dlpoly = DLPoly(control=DATA_PATH / "CONTROL",
                            config=DATA_PATH / "CONFIG",
                            field=DATA_PATH / "FIELD",
                            workdir=work_dir,
                            vdw_file=DATA_PATH / "TABVDW",
                            ang_file=DATA_PATH / "TABANG",
                            dih_file=DATA_PATH / "TABDIH",
                            inv_file=DATA_PATH / "TABINV",
                            bnd_file=DATA_PATH / "TABBND",
                            eam_file=DATA_PATH / "TABEAM")

            dlpoly.copy_input()

            for input_file in input_files:
                work_file = work_dir / input_file
                self.assertEqual(dlpoly.control[f"io_file_{input_file.lower()}"], str(work_file))
                self.assertTrue(work_file.is_file(), f"{input_file} i/o failure")
                self.assertTrue(filecmp.cmp(DATA_PATH / input_file, work_file, shallow=False))


if __name__ == '__main__':
    unittest.main()
