#!/usr/bin/env python3

from dlpoly import DLPoly
from ase.build import bulk
from ase.io import write
from dlpoly.new_control import NewControl as Control
from dlpoly.field import Field, Bond, Potential, Molecule
from dlpoly.species import Species


dlp = "/your/home/bin/DLPOLY.Z"
#dlp = "/home/drFaustroll/lavello/build-dlp-jan/bin/DLPOLY.Z"

a = bulk('Ar', 'fcc', a=4.0)*(8,8,8)
write("Ar-fcc.config",a,format='dlp4')

ctl = Control()
ctl.title = 'Ar'
ctl.temperature = (300, 'K')
ctl.timestep = ( 1, 'fs')
ctl.ensemble = 'nve'
ctl.padding = (0.5, 'Ang')
ctl.vdw_method = 'direct'
ctl.cutoff = (7.0,'Ang')
ctl.stats_frequency = (100,'steps')
ctl.print_frequency = (100,'steps')
ctl.stack_size = (10,'steps')
ctl.time_run = (10000,'fs')
ctl.time_equilibration = (1000,'steps')
ctl.time_job = (10000,'s')
ctl.time_close = (10,'s')
ctl.data_dump_frequency = (5000,'steps')
ctl.io_file_config = 'Ar-fcc.config'

# you can also do it dictionary style
#ctl['io_file_config'] = 'Ar-fcc.config'

ctl.write("new.control")

fld = Field()

fld.header = "Ar"
fld.units = "kJ"
m = Molecule()
m.name="Ar"
m.n_atoms = 1
m.species = {1: Species(name="Ar",index=1,mass=39.948000,charge=0.0,frozen=0,repeats=1)}
fld.add_molecule(m)
m.n_mols = len(a)
fld.add_potential("Ar",Potential("vdw",['lj','Ar','Ar','0.9661', '3.405']))
fld.write("ar.field")

dlpoly = DLPoly()
dlpoly.control = ctl
dlpoly.load_config("Ar-fcc.config")
dlpoly.load_field("ar.field")
dlpoly.workdir = "argon"
dlpoly.run(executable=dlp,numProcs = 1)


