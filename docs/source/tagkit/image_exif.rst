tagkit.image_exif
=================

The ``tagkit.image_exif`` module provides classes and functions for extracting and working with EXIF data from image files.

**Usage Example:**

.. code-block:: python

   from tagkit.image_exif import ImageExifData
   exif_data = ImageExifData('photo.jpg')
   print(exif_data.get_tags())

.. autosummary::
   :toctree: _autosummary

   ImageExifData

.. automodule:: tagkit.image_exif
   :members:
   :undoc-members:
   :show-inheritance: 