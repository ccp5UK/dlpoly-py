dlpoly-py
=========

this contains tools to read input and output for DL_POLY
it can also produce inputs and be mixed with other python packages
like ASE, MDAnalysis, MDAnse or pymatgen

install
-------

- via pip

.. code:: bash

   pip install dlpoly-py
   #or
   pip3 install dlpoly-py

- in a virtual environment

.. code:: bash

   # create virtual env
   virtualenv3 venv/dlpoly
   source venv/dlpoly/bin/activate
   pip3 install dlpoly-py

usage
-----

Examples can be found in https://gitlab.com/drFaustroll/dlpoly-py/examples

sime run using Ar data from above folder.


.. code:: python

   from dlpoly import DLPoly

   dlp="/home/drFaustroll/playground/dlpoly/dl-poly-alin/build-yaml/bin/DLPOLY.Z"

   dlPoly = DLPoly(control="Ar.control", config="Ar.config",
                   field="Ar.field", workdir="argon")
   dlPoly.run(executable=dlp,numProcs = 4)

   # change temperature and rerun, from previous termination
   dlPoly = DLPoly(control="Ar.control", config="argon/REVCON", destconfig="Ar.config",
                field="Ar.field", workdir="argon-T310")
   dlPoly.control.temperature = 310.0
   dlPoly.run(executable=dlp,numProcs = 4)


