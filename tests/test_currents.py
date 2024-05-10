import unittest
from pathlib import Path

from dlpoly.currents import Currents

DATA_PATH = Path(__file__).parent


class CurrentsTest(unittest.TestCase):

    currents = Currents()

    def test_currents_read_yaml(self):
        self.currents.read(DATA_PATH / "CURRENTS.yml")
        self.assertEqual(self.currents.data.shape, (21, 2, 8, 3))
        self.assertEqual(self.currents.atoms, ['Li', 'F'])
        self.assertAlmostEqual(self.currents.timesteps[0], 0.0)
        self.assertAlmostEqual(self.currents.timesteps[-1], 0.20000000E-01)

    def test_currents_read(self):
        self.currents.read(DATA_PATH / "CURRENTS")
        self.assertEqual(self.currents.data.shape, (21, 2, 8, 3))
        self.assertEqual(self.currents.atoms, ['Li', 'F'])
        self.assertAlmostEqual(self.currents.timesteps[0], 0.0)
        self.assertAlmostEqual(self.currents.timesteps[-1], 0.20000000E-01)


if __name__ == '__main__':
    unittest.main()
