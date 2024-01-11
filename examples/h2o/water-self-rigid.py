#!/usr/bin/env python3

from dlpoly import DLPoly
from ase.io import read, write
from dlpoly.new_control import NewControl as Control
from dlpoly.field import Field, Bond, Potential, Molecule
from dlpoly.species import Species


dlp = "/your/home/bin/DLPOLY.Z"
dlp = "/home/drFaustroll/lavello/build-dlp-jan/bin/DLPOLY.Z"

water = read("water-constraints.config")
write("water-self.config",water,format='dlp4')
nH2O = len([x.symbol for x in water if x.symbol == 'O'])

ctl = Control()
ctl.title = 'water'
ctl.temperature = (300, 'K')
ctl.timestep = ( 1, 'fs')
ctl.ensemble = 'nve'
ctl.padding = (0.5, 'Ang')
ctl.vdw_method = 'direct'
ctl.cutoff = (10.0,'Ang')
ctl.coul_method = 'spme'
ctl.ewald_precision = 1.0e-6
ctl.stats_frequency = (100,'steps')
ctl.print_frequency = (100,'steps')
ctl.stack_size = (10,'steps')
ctl.time_run = (1000,'fs')
ctl.time_equilibration = (100,'fs')
ctl.time_job = (10000,'s')
ctl.time_close = (10,'s')
ctl.data_dump_frequency = (5000,'steps')
ctl.io_file_config = 'water-self.config'

# you can also do it dictionary style
#ctl['io_file_config'] = 'Ar-fcc.config'

ctl.write("water-self.control")

fld = Field()

fld.header = "water spce"
fld.units = "kcal/mole"
m = Molecule()
m.name="H2O"
m.n_atoms = 6
m.species = {1: Species(name="O",index=1,mass=15.9994,charge=-0.730,frozen=0,repeats=2),
             2: Species(name="H",index=2,mass=1.008,charge=0.365,frozen=0,repeats=4)}
m.add_potential('1',Bond('rigid',['3','1','3','4']))
m.add_potential('2',Bond('rigid',['3','2','5','6']))

fld.add_molecule(m)
m.n_mols = nH2O//2

fld.add_potential("O",Potential("vdw",['lj','O','O','0.16', '3.196']))
fld.write("spce-self.field")

dlpoly = DLPoly()
dlpoly.control = ctl
dlpoly.load_config("water-self.config")
dlpoly.load_field("spce-self.field")
dlpoly.workdir = "water-self"
dlpoly.run(executable=dlp,numProcs = 1)


