tagkit.exif_entry
===============

The ``tagkit.exif_entry`` module provides the ``ExifEntry`` class for representing and manipulating EXIF tag data from images.

**Basic Usage:**

.. code-block:: python

   from tagkit.exif_entry import ExifEntry

   # Create an entry with a string value
   entry = ExifEntry(id=271, value='Canon', ifd='IFD0')
   print(entry.name, entry.value)  # Output: Make Canon

   # Create an entry with binary data
   binary_data = b'\x89PNG\r\n'
   binary_entry = ExifEntry(id=37510, value=binary_data, ifd='Exif')

   # Format binary data in different ways
   print(binary_entry.format(binary_format="bytes"))  # b'\x89PNG\r\n'
   print(binary_entry.format(binary_format="hex"))    # hex:89504e470d0a
   print(binary_entry.format(binary_format="base64")) # base64:iVBORw0K

   # Get a dictionary representation
   print(binary_entry.to_dict(binary_format="hex"))
   # Output: {'id': 37510, 'name': 'UserComment', 'value': 'hex:89504e470d0a', 'ifd': 'Exif'}

.. autosummary::
   :toctree: _autosummary

   ExifEntry

.. automodule:: tagkit.exif_entry
   :members:
   :undoc-members:
   :show-inheritance:
