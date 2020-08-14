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

Examples can be found in https://gitlab.com/drFaustroll/dlpoly-py/-/tree/devel/examples

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
   dlPoly.control['temp'] = 310.0
   dlPoly.run(executable=dlp,numProcs = 4)

alternatively you can set the environment variable DLP_EXE to point to DL_POLY_4 executable and remove the executable parameter from
run.

.. code:: bash

   export DLP_EXE="/home/drFaustroll/playground/dlpoly/dl-poly-alin/build-yaml/bin/DLPOLY.Z"

.. code:: python

   from dlpoly import DLPoly

   dlPoly = DLPoly(control="Ar.control", config="Ar.config",
                   field="Ar.field", workdir="argon")
   dlPoly.run(numProcs = 4)

   # change temperature and rerun, from previous termination
   dlPoly = DLPoly(control="Ar.control", config="argon/REVCON", destconfig="Ar.config",
                field="Ar.field", workdir="argon-T310")
   dlPoly.control['temp'] = 310.0
   dlPoly.run(numProcs = 4)



authors
-------

 - Alin M Elena, Daresbury Laboratory, UK
 - Jacob Wilkins, University of Oxford, UK

contact
-------

  - please report issues in the `gitlab tracker <https://gitlab.com/drFaustroll/dlpoly-py/-/issues>`_
  - available in the `matrix room <https://matrix.to/#/!MsDOMMiBCBkTvqGxOz:matrix.org/$-Tgf2pIJ9CD732cbG5FEawZiRy8CJlexMbgwD25vvBQ?via=matrix.org>`_

