#!/usr/bin/env python3
import unittest
from pathlib import Path

from dlpoly.correlations import Correlations

DATA_PATH = Path(__file__).parent


class CorrelationsTest(unittest.TestCase):

    correlations = Correlations(source=DATA_PATH / "COR")

    def test_correlations_values(self):
        assert self.correlations.is_yaml
        assert self.correlations.n_correlations == 4

        for cor in [
            "stress_xy-stress_xy",
            "stress_yz-stress_yz",
            "heat_flux_x-heat_flux_x",
            "Ar-velocity_x-velocity_y",
        ]:
            assert cor in self.correlations.data.keys()

        assert self.correlations.blocks == [1, 1, 1, 1]
        assert self.correlations.window == [1, 1, 1, 1]
        assert self.correlations.points_per_block == [5000, 100, 100, 100]

        for lags in self.correlations.lags:
            assert lags == [float(i) for i in range(10)]

        assert (
            self.correlations.data["stress_xy-stress_xy"]["value"][0] == 0.12336263E-02
        )
        assert (
            self.correlations.data["stress_yz-stress_yz"]["value"][0] == 0.19269362E-01
        )
        assert (
            self.correlations.data["heat_flux_x-heat_flux_x"]["value"][0]
            == 0.57119580E-09
        )
        assert (
            self.correlations.data["Ar-velocity_x-velocity_y"]["value"][0]
            == 0.31963469E-01
        )

    def test_correlations_observables(self):

        for observables in ["viscosity", "kinematic-viscosity", "thermal-conductivity"]:
            assert observables in self.correlations.observables.keys()

        assert len(self.correlations.observables["viscosity"]["components"]) == 2
        assert len(self.correlations.observables["kinematic-viscosity"]["components"]) == 2
        assert (
            self.correlations.observables["thermal-conductivity"]["value"] == 0.23450770E-06
        )


if __name__ == "__main__":
    unittest.main()
