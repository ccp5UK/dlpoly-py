=======
control
=======

``dlpoly-py`` supports both new-style (``NewControl``, preferred) and
old-style (``Control``, deprecated) control files.

By default, ``dlpoly-py`` will convert any old-style files into the
new-style on loading and will only write new-style files. It is
possible to manually use an old style file by setting the ``control``
attribute of a ``DLPoly`` object to a ``Control``, however, this is
not recommended as newer DLPoly features will only be available in the
new-style control files..

New-style control API
---------------------

.. automodule:: dlpoly.new_control
   :members:
   :special-members: __init__
   :undoc-members:


Old-style control API
_____________________

.. automodule:: dlpoly.control
   :members:
   :special-members: __init__
   :undoc-members:
