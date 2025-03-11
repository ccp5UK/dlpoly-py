"""
Module to handle new-style DLPoly control files.
"""
from collections.abc import Iterable, Sequence
from functools import singledispatchmethod
from pathlib import Path
from typing import Any, Dict, Iterator, TextIO, Tuple, Union

from .types import OptPath, PathLike
from .utility import DLPData


class NewControl(DLPData):
    """
    Class to handle new-style DLPoly control file.

    Attributes
    ----------
    source
        File data originally read from.

    Notes
    -----
    For meanings of parameters, see DLPoly manual.
    """
    def __init__(self, source: OptPath = None, **override):
        """
        Instantiate class to handle new-style DLPoly control file.

        Parameters
        ----------
        source : OptPath
            File to read.
        **override : Dict[str, Any]
            Extra arguments to set on instantiation.
        """
        DLPData.__init__(self, {
            "title": str,
            "simulation_method": str,
            "random_seed": (int, int, int),
            "density_variance": (float, str),
            "data_dump_frequency": (float, str),
            "subcell_threshold": float,
            "evb_num_ff": int,
            "time_run": (float, str),
            "time_equilibration": (float, str),
            "time_job": (float, str),
            "time_close": (float, str),
            "stats_frequency": (float, str),
            "stack_size": (float, str),
            "record_equilibration": bool,
            "print_probability_distribution": bool,
            "analyse_all": bool,
            "analyse_angles": bool,
            "analyse_bonds": bool,
            "analyse_dihedrals": bool,
            "analyse_inversions": bool,
            "analyse_frequency": (float, str),
            "analyse_frequency_bonds": (float, str),
            "analyse_frequency_angles": (float, str),
            "analyse_frequency_dihedrals": (float, str),
            "analyse_frequency_inversions": (float, str),
            "analyse_max_dist": (float, str),
            "analyse_num_bins": int,
            "analyse_num_bins_bonds": int,
            "analyse_num_bins_angles": int,
            "analyse_num_bins_dihedrals": int,
            "analyse_num_bins_inversions": int,
            "msd_calculate": bool,
            "msd_print": bool,
            "msd_start": (float, str),
            "msd_frequency": (float, str),
            "correlation_observable": (str, ...),
            "correlation_blocks": (int, ...),
            "correlation_block_points": (int, ...),
            "correlation_window": (int, ...),
            "correlation_update_frequency": (int, ...),
            "correlation_dump_frequency": (float, str),
            "traj_calculate": bool,
            "traj_key": str,
            "traj_start": (float, str),
            "traj_interval": (float, str),
            "defects_calculate": bool,
            "defects_start": (float, str),
            "defects_interval": (float, str),
            "defects_distance": (float, str),
            "defects_backup": bool,
            "displacements_calculate": bool,
            "displacements_start": (float, str),
            "displacements_interval": (float, str),
            "displacements_distance": (float, str),
            "coord_calculate": bool,
            "coord_ops": str,
            "coord_start": (float, str),
            "coord_interval": (float, str),
            "adf_calculate": bool,
            "adf_frequency": (float, str),
            "adf_precision": float,
            "rdf_calculate": bool,
            "rdf_print": bool,
            "rdf_frequency": (float, str),
            "rdf_binsize": (float, str),
            "rdf_error_analysis": str,
            "rdf_error_analysis_blocks": int,
            "zden_calculate": bool,
            "zden_print": bool,
            "zden_frequency": (float, str),
            "zden_binsize": (float, str),
            "vaf_calculate": bool,
            "vaf_print": bool,
            "vaf_frequency": (float, str),
            "vaf_binsize": int,
            "vaf_averaging": bool,
            "currents_calculate": bool,
            "energy_stress_currents": bool,
            "heat_flux": bool,
            "momentum_density": (str, ...),
            "write_per_particle": bool,
            "elastic_constants": bool,
            "print_frequency": (float, str),
            "io_units_scheme": str,
            "io_units_length": str,
            "io_units_time": str,
            "io_units_mass": str,
            "io_units_charge": str,
            "io_units_energy": str,
            "io_units_pressure": str,
            "io_units_force": str,
            "io_units_velocity": str,
            "io_units_power": str,
            "io_units_surface_tension": str,
            "io_units_emf": str,
            "io_read_method": str,
            "io_read_readers": (int, str),
            "io_read_batch_size": (int, str),
            "io_read_buffer_size": (int, str),
            "io_read_error_check": bool,
            "io_read_ascii_revold": bool,
            "io_write_method": str,
            "io_write_writers": (int, str),
            "io_write_batch_size": (int, str),
            "io_write_buffer_size": (int, str),
            "io_write_sorted": bool,
            "io_write_error_check": bool,
            "io_write_ascii_revive": bool,
            "io_file_output": str,
            "io_file_control": str,
            "io_file_config": str,
            "io_file_field": str,
            "io_file_field_2": str,
            "io_file_field_3": str,
            "io_file_statis": str,
            "io_file_heatflux": str,
            "io_file_history": str,
            "io_file_historf": str,
            "io_file_revive": str,
            "io_file_revold": str,
            "io_file_revcon": str,
            "io_file_rdf": str,
            "io_file_msd": str,
            "io_file_currents": str,
            "io_file_tabbnd": str,
            "io_file_tabang": str,
            "io_file_tabdih": str,
            "io_file_tabinv": str,
            "io_file_tabvdw": str,
            "io_file_tabeam": str,
            "io_file_cor": str,
            "io_file_setevb": str,
            "io_file_popevb": str,
            "io_statis_yaml": bool,
            "io_rdf_yaml": bool,
            "io_file_revcon_2": str,
            "io_file_revcon_3": str,
            "io_file_config_2": str,
            "io_file_config_3": str,
            "output_energy": bool,
            "output_std_dev": bool,
            "ignore_config_indices": bool,
            "print_topology_info": bool,
            "print_level": int,
            "timer_depth": int,
            "timer_yaml_file": bool,
            "timer_per_mpi": bool,
            "timestep": (float, str),
            "timestep_variable": bool,
            "timestep_variable_min_dist": (float, str),
            "timestep_variable_max_dist": (float, str),
            "timestep_variable_max_delta": (float, str),
            "ensemble": str,
            "ensemble_method": str,
            "ensemble_thermostat_coupling": (float, str),
            "ensemble_dpd_order": str,
            "ensemble_dpd_drag": (float, str),
            "ensemble_thermostat_friction": (float, str),
            "ensemble_thermostat_softness": float,
            "ensemble_barostat_coupling": (float, str),
            "ensemble_barostat_friction": (float, str),
            "ensemble_semi_isotropic": str,
            "ensemble_semi_orthorhombic": bool,
            "ensemble_tension": (float, str),
            "pressure_tensor": (float, float, float, float, float, float, str),
            "pressure_hydrostatic": (float, str),
            "pressure_perpendicular": (float, float, float, str),
            "temperature": (float, str),
            "pseudo_thermostat_method": str,
            "pseudo_thermostat_width": (float, str),
            "pseudo_thermostat_temperature": (float, str),
            "impact_part_index": int,
            "impact_time": (float, str),
            "impact_energy": (float, str),
            "impact_direction": (float, float, float),
            "ttm_calculate": bool,
            "ttm_num_ion_cells": int,
            "ttm_num_elec_cells": (float, float, float),
            "ttm_metal": bool,
            "ttm_heat_cap_model": str,
            "ttm_heat_cap": (float, str),
            "ttm_temp_term": (float, str),
            "ttm_fermi_temp": (float, str),
            "ttm_elec_cond_model": str,
            "ttm_elec_cond": (float, str),
            "ttm_diff_model": str,
            "ttm_diff": (float, str),
            "ttm_dens_model": str,
            "ttm_dens": (float, str),
            "ttm_min_atoms": int,
            "ttm_stopping_power": (float, str),
            "ttm_spatial_dist": str,
            "ttm_spatial_sigma": (float, str),
            "ttm_spatial_cutoff": float,
            "ttm_fluence": (float, str),
            "ttm_penetration_depth": (float, str),
            "ttm_laser_type": str,
            "ttm_temporal_dist": str,
            "ttm_temporal_duration": (float, str),
            "ttm_temporal_cutoff": float,
            "ttm_variable_ep": str,
            "ttm_boundary_condition": str,
            "ttm_boundary_xy": bool,
            "ttm_boundary_heat_flux": (float, str),
            "ttm_time_offset": (float, str),
            "ttm_oneway": bool,
            "ttm_stats_frequency": (float, str),
            "ttm_traj_frequency": (float, str),
            "ttm_com_correction": str,
            "ttm_redistribute": bool,
            "ttm_e-phonon_friction": (float, str),
            "ttm_e-stopping_friction": (float, str),
            "ttm_e-stopping_velocity": (float, str),
            "ttm_e-phonon_cutoff_velocity": (float, str),
            "rlx_cgm_step": (float, str),
            "rlx_tol": (float, str),
            "shake_max_iter": int,
            "shake_tolerance": (float, str),
            "dftb": bool,
            "fixed_com": bool,
            "reset_temperature_interval": (float, str),
            "regauss_frequency": (float, str),
            "rescale_frequency": (float, str),
            "equilibration_force_cap": (float, str),
            "minimisation_criterion": str,
            "minimisation_tolerance": (float, str),
            "minimisation_step_length": (float, str),
            "minimisation_frequency": (float, str),
            "initial_minimum_separation": (float, str),
            "restart": str,
            "nfold": (int, int, int),
            "cutoff": (float, str),
            "padding": (float, str),
            "coul_bjerrum_length": (float, str),
            "coul_damping": (float, str),
            "coul_dielectric_constant": float,
            "coul_extended_exclusion": bool,
            "coul_method": str,
            "coul_precision": float,
            "spme_precision": float,
            "spme_alpha": (float, str),
            "spme_kvec": (int, int, int),
            "spme_kvec_spacing": (float, str),
            "spme_nsplines": int,
            "polarisation_model": str,
            "polarisation_thole": float,
            "metal_direct": bool,
            "metal_sqrtrho": bool,
            "vdw_method": str,
            "vdw_cutoff": (float, str),
            "vdw_mix_method": str,
            "vdw_force_shift": bool,
            "plumed": bool,
            "plumed_input": str,
            "plumed_log": str,
            "plumed_precision": int,
            "plumed_restart": bool,
            "strict_checks": bool,
            "unsafe_comms": bool,
            "dftb_test": bool,
            "replay": bool,
            "replay_calculate_forces": bool,
            "charge_smearing_method": str,
            "charge_smearing_length": (float, str),
            "charge_smearing_beta": str,
        }, strict=True)

        self.io_file_output = "OUTPUT"
        self.io_file_control = "CONTROL"
        self.io_file_config = "CONFIG"
        self.io_file_field = "FIELD"
        self.io_file_statis = "STATIS"
        self.io_file_history = "HISTORY"
        self.io_file_historf = "HISTORF"
        self.io_file_revive = "REVIVE"
        self.io_file_revold = "REVOLD"
        self.io_file_revcon = "REVCON"
        self.io_file_rdf = "RDFDAT"
        self.io_file_cor = "COR"
        self.io_file_msd = "MSDTMP"
        self.io_file_currents = "CURRENTS"

        self.title = 'Untitled'
        self.source = Path(source) if source is not None else source
        if source is not None:
            self.read(source)

        for key, val in override.items():
            self[key] = val

    @staticmethod
    def from_dict(in_dict: Dict[str, Any], strict: bool = True) -> "NewControl":
        """
        Create a control file from a dictionary.

        If not `strict`, raising on invalid options in dictionary.

        Parameters
        ----------
        in_dict : Dict[str, Any]
            Dictionary to read params from.
        strict : bool
            Whether to `raise` in case of invalid key.

        Returns
        -------
        NewControl
            Control built from dictionary `in_dict`.
        """
        new_control = NewControl()
        if strict:
            for key, val in in_dict.items():
                new_control[key] = val
        else:
            for key, val in in_dict.items():
                if key in new_control.keys:
                    new_control[key] = val

        return new_control

    @singledispatchmethod
    def read(self, x):
        """
        Read a DLPoly new-style control file.

        Note: If used on `Control` instance, will update `Control`
              with read values with new values taking priority.

        Parameters
        ----------
        x : Union[dict, Iterable[str], TextIO, str, Path]
            Dict or file-like data to read.

        Raises
        ------
        TypeError
            Attempt to read from invalid type.
        """
        raise TypeError(f"Cannot create {type(self).__name__} from {type(x).__name__}")

    @read.register(dict)
    def _(self, in_dict: dict):
        """
        Read a control file from a dictionary.

        Parameters
        ----------
        in_dict : dict
            Dictionary to read from.
        """
        for key, val in in_dict.items():
            self[key] = val

    @read.register(Iterable)
    @read.register(TextIO)
    def _(self, data):
        """
        Read a control file from a file-like string iterator.

        Parameters
        ----------
        data : Union[Iterable[str], TextIO]
            File-like data to read from.
        """
        for line in data:
            line = line.split("#")[0]
            line = line.split("!")[0]
            line = line.strip()
            if not line:
                continue
            key, *args = line.split()
            # Special case to handle string
            if key == "title":
                self[key] = " ".join(args)
                continue

            if key.startswith("ewald"):
                corrected_key = key.replace("ewald", "spme")
                print(f"Warning {key} used in control, should be {corrected_key}"
                      " (applying correction)", flush=True)
                key = corrected_key

            self[key] = [stripped_arg for arg in args
                         if (stripped_arg := arg.strip("[]"))]

    @read.register(Path)
    @read.register(str)
    def _(self, filename: PathLike):
        """
        Read a control file from a path on disc.

        Parameters
        ----------
        filename : PathLike
            Path to DLPoly new-style control file.
        """
        with open(filename, "r", encoding="utf-8") as in_file:
            self.read(in_file)

    @singledispatchmethod
    @staticmethod
    def _format_val(vals: Any, key: str) -> str:
        """
        Format `Control` variables for output to file.

        Parameters
        ----------
        vals : Any
            Value to format.
        key : str
            Key of variables.

        Returns
        -------
        str
            Formatted `Control` variable.
        """
        return str(vals)

    @_format_val.register
    @staticmethod
    def _(vals: Sequence, key: str) -> str:
        """
        Format tuple/vector of parameters.

        Parameters
        ----------
        vals : Sequence
            Vector-like value.
        key : str
            Key of variable.

        Returns
        -------
        str
            Formatted `Control` variable.
        """
        lvals = None
        can_be_len_1 = key in ("correlation_observable",
                               "correlation_blocks",
                               "correlation_block_points",
                               "correlation_window",
                               "correlation_update_frequency",
                               "momentum_density")

        if not can_be_len_1 and isinstance(vals[-1], str):
            lvals, unit = vals[:-1], vals[-1]
        else:
            lvals, unit = vals, ""

        if unit == "steps":
            lvals = list(map(int, lvals))

        out = " ".join(map(str, lvals))

        if len(lvals) > 1 or can_be_len_1:
            out = f"[{out}]"

        return f"{out} {unit}"

    @_format_val.register
    @staticmethod
    def _(vals: bool, key: str) -> str:
        """
        Format boolean arguments.

        Parameters
        ----------
        vals : bool
            Boolean value.
        key : str
            Key of variable.

        Returns
        -------
        str
            Formatted `Control` variable.
        """
        return "ON" if vals else "OFF"

    @_format_val.register(str)
    @_format_val.register(Path)
    @staticmethod
    def _(vals: Union[str, Path], key: str) -> str:
        """
        Format string/Path arguments.

        Parameters
        ----------
        vals : Union[str, Path]
            Path or string-like value.
        key : str
            Key of variable.

        Returns
        -------
        str
            Formatted `Control` variable.
        """
        if not vals:
            return ""

        return str(vals)

    def write(self, filename: PathLike = "new_control"):
        """
        Write `Control` object to disc.

        Parameters
        ----------
        filename : PathLike
            File to write data to.
        """

        def output(key: str, val: Any):
            """
            Write key to file if present.

            Parameters
            ----------
            key : str
                Key to write.
            val : Any
                Value to write.
            """
            if formatted := self._format_val(val, key):
                print(key, formatted, file=out_file)

        with open(filename, "w", encoding="utf-8") as out_file:
            output("title", self["title"])
            for key, vals in self.items():
                if (
                        key in ("title", "filename", "io_file_control") or
                        (key in ("io_file_output") and vals.upper() != "SCREEN")
                ):
                    continue
                output(key, vals)

    def __iter__(self) -> Iterator[str]:
        """
        Return all `Control` keys which have been set.

        Returns
        -------
        Iterator[str]
            Generator of DLPoly keys which have been set.
        """
        return (key for key, vals in self.__dict__.items()
                if (not key.startswith("_") and
                    key not in ("source") and
                    vals is not None))

    def items(self) -> Iterator[Tuple[str, Any]]:
        """
        Return key-value tuples like `dict.items()` method.

        Yields
        ------
        Tuple[str, Any]
            Key-value pairs.
        """
        for key in self:
            yield (key, self[key])

    def __str__(self) -> str:
        out = f"""
Control: {self.source}
title: {self.title}
keys_set: {", ".join(key for key in self)}
"""

        return out

    def __repr__(self) -> str:
        out = f"""
Control: {self.source}
title: {self.title}
"""
        out += "\n".join(f"{key}: {self._format_val(vals, key)}"
                         for key, vals in self.items()
                         if key != "title")
        return out


def is_new_control(filename: PathLike) -> bool:
    """
    Determine if file is in old or new format.

    Parameters
    ----------
    filename : PathLike
        File to check.

    Returns
    -------
    bool
        Whether file is old-style or new-style.
    """
    with open(filename, "r", encoding="utf-8") as in_file:
        for line in in_file:
            line = line[0:line.find("#")]
            line = line[0:line.find("!")]
            line = line.strip()

            if not line:
                continue

            key = line.split()[0].lower()
            return key == "title"

    return False
