"""
Module to handle new DLPOLY control files
"""

from .utility import DLPData

class DummyIOParam():
    """ Dummy class defining io parameters """
    def __init__(self, parent):
        self.control = None
        self.parent = parent

    @property
    def field(self):
        return self.parent.io_file_field

    @property
    def config(self):
        return self.parent.io_file_config

    @property
    def statis(self):
        return self.parent.io_file_statis

    @property
    def output(self):
        return self.parent.io_file_output

    @property
    def history(self):
        return self.parent.io_file_history

    @property
    def historf(self):
        return self.parent.io_file_historf

    @property
    def revive(self):
        return self.parent.io_file_revive

    @property
    def revcon(self):
        return self.parent.io_file_revcon

    @property
    def revold(self):
        return self.parent.io_file_revold

    @property
    def rdf(self):
        return self.parent.io_file_rdf

    @property
    def msd(self):
        return self.parent.io_file_msd

    @property
    def tabvdw(self):
        return self.parent.io_file_tabvdw

    @property
    def tabbnd(self):
        return self.parent.io_file_tabbnd

    @property
    def tabang(self):
        return self.parent.io_file_tabang

    @property
    def tabdih(self):
        return self.parent.io_file_tabdih

    @property
    def tabinv(self):
        return self.parent.io_file_tabinv

    @property
    def tabeam(self):
        return self.parent.io_file_tabeam

    @config.setter
    def config(self,value):
        self.parent.io_file_config = value

    @field.setter
    def field(self,value):
        self.parent.io_file_field = value

    @statis.setter
    def statis(self,value):
        self.parent.io_file_statis = value

    @history.setter
    def history(self,value):
        self.parent.io_file_history = value

    @historf.setter
    def historf(self,value):
        self.parent.io_file_historf = value

    @revive.setter
    def revive(self,value):
        self.parent.io_file_revive = value

    @revold.setter
    def revold(self,value):
        self.parent.io_file_revold = value

    @revcon.setter
    def revcon(self,value):
        self.parent.io_file_revcon = value

    @rdf.setter
    def rdf(self,value):
        self.parent.io_file_rdf = value

    @msd.setter
    def msd(self,value):
        self.parent.io_file_msd = value

    @tabbnd.setter
    def tabbnd(self,value):
        self.parent.io_file_tabbnd = value

    @tabang.setter
    def tabang(self,value):
        self.parent.io_file_tabang = value

    @tabdih.setter
    def tabdih(self,value):
        self.parent.io_file_tabdih = value

    @tabinv.setter
    def tabinv(self,value):
        self.parent.io_file_tabinv = value

    @tabvdw.setter
    def tabvdw(self,value):
        self.parent.io_file_tabvdw = value

    @tabeam.setter
    def tabeam(self,value):
        self.parent.io_file_tabeam = value


class NewControl(DLPData):
    """ Class defining a DLPOLY new control file

    :param source: File to read
    :param override: Set keys manually on init

    """
    def __init__(self, source=None, **override):
        DLPData.__init__(self, {
            "io": DummyIOParam,
            "title": str,
            "random_seed": (int, int, int),
            "density_variance": (float, str),
            "data_dump_frequency": (int, str),
            "subcell_threshold": float,
            "time_run": (float, str),
            "time_equilibration": (float, str),
            "time_job": (float, str),
            "time_close": (float, str),
            "stats_frequency": (float, str),
            "stack_size": (int, str),
            "record_equilibration": bool,
            "print_per_particle_contrib": bool,
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
            "msd_start": (int, str),
            "msd_frequency": (float, str),
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
            "coord_ops": int,
            "coord_start": (float, str),
            "coord_interval": (float, str),
            "adf_calculate": bool,
            "adf_frequency": (float, str),
            "adf_precision": float,
            "rdf_calculate": bool,
            "rdf_print": bool,
            "rdf_frequency": (float, str),
            "rdf_binsize": float,
            "rdf_error_analysis": str,
            "rdf_error_analysis_blocks": int,
            "zden_calculate": bool,
            "zden_print": bool,
            "zden_frequency": (float, str),
            "zden_binsize": float,
            "vaf_calculate": bool,
            "vaf_print": bool,
            "vaf_frequency": (float, str),
            "vaf_binsize": int,
            "vaf_averaging": bool,
            "currents_calculate": bool,
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
            "io_write_netcdf_format": str,
            "io_write_ascii_revive": bool,
            "io_file_output": str,
            "io_file_config": str,
            "io_file_field": str,
            "io_file_statis": str,
            "io_file_history": str,
            "io_file_historf": str,
            "io_file_revive": str,
            "io_file_revold": str,
            "io_file_revcon": str,
            "io_file_rdf": str,
            "io_file_msd": str,
            "io_file_tabbnd": str,
            "io_file_tabang": str,
            "io_file_tabdih": str,
            "io_file_tabinv": str,
            "io_file_tabvdw": str,
            "io_file_tabeam": str,
            "output_energy": bool,
            "ignore_config_indices": bool,
            "print_topology_info": bool,
            "print_level": int,
            "time_depth": int,
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
            "ttm_num_elec_cells": (int, int, int),
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
            "ttm_spatial_cutoff": (float, str),
            "ttm_fluence": (float, str),
            "ttm_penetration_depth": (float, str),
            "ttm_laser_type": str,
            "ttm_temporal_dist": str,
            "ttm_temporal_duration": (float, str),
            "ttm_temporal_cutoff": (float, str),
            "ttm_variable_ep": str,
            "ttm_boundary_condition": str,
            "ttm_boundary_xy": bool,
            "ttm_boundary_heat_flux": (bool, str),
            "ttm_time_offset": (float, str),
            "ttm_oneway": bool,
            "ttm_statis_frequency": (float, str),
            "ttm_traj_frequency": (float, str),
            "ttm_com_correction": str,
            "ttm_redistribute": bool,
            "ttm_e-phonon_friction": (float, str),
            "ttm_e-stopping_friction": (float, str),
            "ttm_e-stopping_velocity": (float, str),
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
            "coul_damping": (float, str),
            "coul_dielectric_constant": float,
            "coul_extended_exclusion": bool,
            "coul_method": str,
            "coul_precision": float,
            "ewald_precision": float,
            "ewald_alpha": (float, str),
            "ewald_kvec": (int, int, int),
            "ewald_kvec_spacing": (float, str),
            "ewald_nsplines": int,
            "polarisation_model": str,
            "polarisation": float,
            "metal_direct": bool,
            "metal_sqrtrho": bool,
            "vdw_method": str,
            "vdw_cutoff": (float, str),
            "vdw_mix_method": str,
            "vdw_force_shift": bool,
            "plumed": bool,
            "plumed_input": str,
            "plumed_log": str,
            "plumed_precision": float,
            "plumed_restart": bool,
            "strict_checks": bool,
            "unsafe_comms": bool,
            "unit_test": bool,
        }, strict=True)

        self.io = DummyIOParam(self)

        if source is not None:
            self.read(source)

        for key, val in override.items():
            self[key] = val

    def read(self, filename):
        """ Read a control file

        :param filename: File to read

        """
        with open(filename, "r") as inFile:
            for line in inFile:
                line = line.strip()
                if line == '':
                    continue
                key, *args = line.split()
                self[key] = args

    def write(self, filename="new_control"):
        """ Write a new control file

        :param filename: Name to write to

        """
        def output(key, vals):
            if isinstance(vals, (list, tuple)):
                if isinstance(vals[-1], str):
                    unit = vals.pop()
                else:
                    unit = ""
                if len(vals) > 1:
                    print(key, "[", *(f" {val}" for val in vals), "]", unit, file=outFile)
                else:
                    print(key, *(f" {val}" for val in vals), unit, file=outFile)

            elif isinstance(vals, bool):
                if vals:
                    print(key, "ON", file=outFile)
                else:
                    print(key, "OFF", file=outFile)
            elif isinstance(vals, str) and not vals:
                return
            else:
                print(key, vals, file=outFile)

        with open(filename, "w") as outFile:
            output("title", self["title"])
            for key, vals in self.__dict__.items():
                if key in ("title", "filename") or key.startswith("_"):
                    continue
                output(key, vals)

def is_new_control(filename):
    """ Determine if file is in old or new format """
    with open(filename, 'r') as inFile:
        for line in inFile:
            line = line[0:line.find('#')]
            line = line[0:line.find('!')]
            line = line.strip()

            if not line:
                continue

            key = line.split()[0].lower()
            return key == 'title'
