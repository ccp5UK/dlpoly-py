#!/usr/bin/env python3

from dlpoly import DLPoly
from ase.build import bulk
from ase.io import write
from dlpoly.new_control import NewControl as Control
from dlpoly.field import Field, Bond, Potential, Molecule
from dlpoly.species import Species


dlp = "/your/home/bin/DLPOLY.Z"

a = bulk('NaCl', 'rocksalt', a=5.64,cubic=True)*(4,4,4)
write("NaCl.config",a,format='dlp4')

nNa = len([ x.symbol for x in a if x.symbol == 'Na' ])
nCl = len([ x.symbol for x in a if x.symbol == 'Cl' ])

ctl = Control()
ctl.title = 'NaCl'
ctl.temperature = (300, 'K')
ctl.timestep = ( 1, 'fs')
ctl.ensemble = 'nve'
ctl.padding = (0.5, 'Ang')
ctl.vdw_method = 'direct'
ctl.cutoff = (10.0,'Ang')
ctl.stats_frequency = (100,'steps')
ctl.print_frequency = (100,'steps')
ctl.stack_size = (10,'steps')
ctl.ewald_precision = 1.0e-6
ctl.coul_method = 'spme'
ctl.time_run = (10000,'fs')
ctl.time_equilibration = (1000,'steps')
ctl.time_job = (10000,'s')
ctl.time_close = (10,'s')
ctl.data_dump_frequency = (5000,'steps')
ctl.io_file_config = 'NaCl.config'

# you can also do it dictionary style
#ctl['io_file_config'] = 'NaCl.config'

ctl.write("NaCl.control")

# old bhm
#Na          22.989769         1.0  1
#Cl           35.453        -1.0  1
#Na      Na  bhm       6.08114245       3.15450000       2.34000000      24.18021033      11.51457935
#Na      Cl  bhm       4.86491396       3.15450000       2.75500000     161.20458891     200.06692161
#Cl      Cl  bhm       3.64868547       3.15450000       3.17000000    1669.62237094    3353.72848948


fld = Field()

fld.header = "NaCl"
fld.units = "kcal/mole"
m = Molecule()
m.name="NaCl"
m.n_atoms = 2
m.species = {1: Species(name="Na",index=1,mass=22.99,charge=0.885,frozen=0,repeats=1),
             2: Species(name="Cl",index=2,mass=35.45,charge=-0.885, frozen=0.,repeats=1)}
fld.add_molecule(m)
m.n_mols = nNa
#fld.add_potential("NaNa",Potential("vdw",['bhm','Na','Na','6.08114245','3.15450000','2.34000000','24.18021033','11.51457935']))
fld.add_potential("NaNa",Potential("vdw",['lj','Na','Na','0.0347','2.52']))
fld.add_potential("NaCl",Potential("vdw",['lj','Na','Cl','0.1152', '3.19']))
fld.add_potential("ClCl",Potential("vdw",['lj','Cl','Cl','0.3826', '3.85']))
fld.write("NaCl.field")

dlpoly = DLPoly()
dlpoly.control = ctl
dlpoly.load_config("NaCl.config")
dlpoly.load_field("NaCl.field")
dlpoly.workdir = "nacl"
dlpoly.run(executable=dlp,numProcs = 1)


