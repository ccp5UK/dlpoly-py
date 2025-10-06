import unittest
from pathlib import Path

from dlpoly.currents import Currents, _unpack_complex

import numpy as np

DATA_PATH = Path(__file__).parent


class CurrentsTest(unittest.TestCase):
    currents = Currents()

    def test_currents_read_yaml(self):
        self.currents.read(DATA_PATH / "CURRENTS.yml")
        self.assertEqual(self.currents.density.shape, (3, 2, 2))
        self.assertAlmostEqual(self.currents.density[-1, 0, -1], complex(234.29275, -14.417973))

        self.assertEqual(self.currents.longitudinal.shape, (3, 2, 2, 3))
        self.assertAlmostEqual(
            self.currents.longitudinal[-1, 0, -1, -1], complex(-156.81642, -18.381872)
        )

        self.assertEqual(self.currents.transverse.shape, (3, 2, 2, 3))
        self.assertAlmostEqual(self.currents.transverse[-1, 0, -1, -1], complex(0.0, 0.0))

        self.assertEqual(self.currents.energy_density.shape, (3, 2, 2, 3))
        self.assertAlmostEqual(
            self.currents.energy_density[-1, 1, -1, -1], complex(-6977948.8, 423323.47)
        )

        self.assertEqual(self.currents.stress.shape, (3, 2, 2, 6))
        self.assertAlmostEqual(self.currents.stress[-1, 1, -1, -1], complex(2263714.5, -119116.98))

        self.assertEqual(self.currents.energy.shape, (3, 2, 2, 3))
        self.assertAlmostEqual(self.currents.energy[-1, 1, -1, -1], complex(-1385245.4, 2208897.4))

        self.assertEqual(self.currents.atoms, ["Li", "F"])

        self.assertAlmostEqual(self.currents.timesteps[0], 0.0)
        self.assertAlmostEqual(self.currents.timesteps[-1], 0.20000000e-02)

    def test_currents_read(self):
        self.currents.read(DATA_PATH / "CURRENTS")
        self.assertEqual(self.currents.density.shape, (3, 2, 2))
        self.assertAlmostEqual(self.currents.density[-1, 0, -1], complex(234.29275, -14.417973))

        self.assertEqual(self.currents.longitudinal.shape, (3, 2, 2, 3))
        self.assertAlmostEqual(
            self.currents.longitudinal[-1, 0, -1, -1], complex(-156.81642, -18.381872)
        )

        self.assertEqual(self.currents.transverse.shape, (3, 2, 2, 3))
        self.assertAlmostEqual(self.currents.transverse[-1, 0, -1, -1], complex(0.0, 0.0))

        self.assertEqual(self.currents.energy_density.shape, (3, 2, 2, 3))
        self.assertAlmostEqual(
            self.currents.energy_density[-1, 1, -1, -1], complex(-6977948.8, 423323.47)
        )

        self.assertEqual(self.currents.stress.shape, (3, 2, 2, 6))
        self.assertAlmostEqual(self.currents.stress[-1, 1, -1, -1], complex(2263714.5, -119116.98))

        self.assertEqual(self.currents.energy.shape, (3, 2, 2, 3))
        self.assertAlmostEqual(self.currents.energy[-1, 1, -1, -1], complex(-1385245.4, 2208897.4))

        self.assertEqual(self.currents.atoms, ["Li", "F"])

        self.assertAlmostEqual(self.currents.timesteps[0], 0.0)
        self.assertAlmostEqual(self.currents.timesteps[-1], 0.20000000e-02)

    def test_unpack_complex(self):
        np.random.seed(314159)

        for n, c in zip([1, 2, 3, 4], [1, 2, 3, 4]):
            cdata = np.random.rand(n, c) + 1j * np.random.rand(n, c)
            if c == 1:
                cdata = cdata.reshape(n)
            flat = cdata.flatten()
            rdata = np.zeros(n * c * 2)
            for i in range(len(flat)):
                rdata[i * 2] = flat[i].real
                rdata[i * 2 + 1] = flat[i].imag

            unpacked = _unpack_complex(rdata, c)
            print(cdata)
            print(unpacked)
            np.testing.assert_array_almost_equal(cdata, unpacked)


if __name__ == "__main__":
    unittest.main()
