tagkit.exif_entry
===============

The ``tagkit.exif_entry`` module provides the ``ExifEntry`` class for representing and manipulating EXIF tag data from images.

**Usage Example:**

.. code-block:: python

   from tagkit.exif_entry import ExifEntry
   entry = ExifEntry(id=271, value='Canon', ifd='IFD0')
   print(entry.name, entry.value)

.. autosummary::
   :toctree: _autosummary

   ExifEntry

.. automodule:: tagkit.exif_entry
   :members:
   :undoc-members:
   :show-inheritance: 