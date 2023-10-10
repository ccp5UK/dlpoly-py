import unittest
from dlpoly.currents import Currents


class CurrentsTest(unittest.TestCase):

    def setUp(self):
        self.currents = CurrentsTest.currents

    @classmethod
    def setUpClass(cls):
        super(CurrentsTest, cls).setUpClass()
        cls.currents = Currents()

    def test_currents_read_yaml(self):
        self.currents.read('tests/CURRENTS.yml')
        self.assertEqual(self.currents.data.shape, (21, 2, 8, 3))
        self.assertEqual(self.currents.atoms, ['Li', 'F'])
        self.assertAlmostEqual(self.currents.timesteps[0], 0.0)
        self.assertAlmostEqual(self.currents.timesteps[-1], 0.20000000E-01)

    def test_currents_read(self):
        self.currents.read('tests/CURRENTS')
        self.assertEqual(self.currents.data.shape, (21, 2, 8, 3))
        self.assertEqual(self.currents.atoms, ['Li', 'F'])
        self.assertAlmostEqual(self.currents.timesteps[0], 0.0)
        self.assertAlmostEqual(self.currents.timesteps[-1], 0.20000000E-01)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(CurrentsTest('test_currents_read_yaml'))
    suite.addTest(CurrentsTest('test_currents_read'))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
