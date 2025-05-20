tagkit.value_formatting
=======================

The ``tagkit.value_formatting`` module provides the ``TagValueFormatter`` class for formatting EXIF tag values, including support for different binary data representations.

**Binary Format Options**

When working with binary data in EXIF tags, you can choose how to represent the data using the ``binary_format`` parameter. The following formats are supported:

- ``bytes`` (default): Returns a Python bytes literal (e.g., ``b'data'``)
- ``hex``: Returns a hex-encoded string with 'hex:' prefix (e.g., ``hex:64617461``)
- ``base64``: Returns a base64-encoded string with 'base64:' prefix (e.g., ``base64:ZGF0YQ==``)

**Usage Examples:**

.. code-block:: python

   from tagkit.value_formatting import TagValueFormatter
   from tagkit.exif_entry import ExifEntry
   
   # Create a formatter with default configuration
   formatter = TagValueFormatter.from_yaml()
   
   # Create an entry with binary data
   binary_data = b'\x89PNG\r\n'
   entry = ExifEntry(id=37510, value=binary_data, ifd='Exif')
   
   # Format binary data in different ways
   print(formatter.format(entry, binary_format="bytes"))  # b'\x89PNG\r\n'
   print(formatter.format(entry, binary_format="hex"))    # hex:89504e470d0a
   print(formatter.format(entry, binary_format="base64")) # base64:iVBORw0K
   
   # Control binary data rendering
   print(formatter.format(entry, render_bytes=False))     # <bytes: 6>

   
.. note::
   When ``render_bytes`` is ``False``, binary data will be shown as a placeholder (e.g., ``<bytes: 6>``) regardless of the ``binary_format`` setting.


.. autosummary::
   :toctree: _autosummary

.. automodule:: tagkit.value_formatting
   :members:
   :undoc-members:
   :show-inheritance: 