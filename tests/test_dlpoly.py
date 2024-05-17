import tempfile
import unittest
from io import StringIO
from pathlib import Path

from dlpoly.dlpoly import DLPoly
from dlpoly.new_control import NewControl


DATA_PATH = Path(__file__).parent


class DLPolyTest(unittest.TestCase):

    def test_load_outputs(self):
        dlp = DLPoly()
        dlp.control = NewControl()
        dlp.control.read(StringIO("""title 8xGRAMICIDIN A WITH WATER SOLVATING (99120 ATOMS)
timestep  0.001 ps
ensemble nve
temperature  300.0 K
print_frequency  5 steps
stats_frequency  5 steps
time_run 0 steps
vdw_cutoff  8.0 ang
cutoff  8.0 ang
coul_method spme
spme_precision 1e-06
"""))
        dlp.load_config(DATA_PATH / "CONFIG", required=True)
        dlp.load_field(DATA_PATH / "FIELD", required=True)

        for temperature in (300., 120., 300.):
            with tempfile.TemporaryDirectory() as tempdir:
                dlp.workdir = Path(tempdir) / "dlprun"
                dlp.config_file = DATA_PATH / "CONFIG"
                dlp.field_file = DATA_PATH / "FIELD"
                dlp.control.temperature = (temperature, 'K')
                dlp.run(load_outputs=True, outputFile=dlp.workdir / "OUTPUT")
                stat = dlp.statis

                self.assertAlmostEqual(stat["System Temperature"][0], temperature)


if __name__ == "__main__":
    unittest.main()
