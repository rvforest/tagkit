tagkit.operations
=================

The ``tagkit.operations`` module provides high-level operations for extracting and processing EXIF data from images.

**Usage Example:**

.. code-block:: python

   from tagkit.operations import get_exif
   exif = get_exif(['photo1.jpg', 'photo2.jpg'])
   print(exif)

.. autosummary::
   :toctree: _autosummary

   get_exif

.. automodule:: tagkit.operations
   :members:
   :undoc-members:
   :show-inheritance:

Functions
---------

.. autofunction:: tagkit.operations.get_exif

Summary:

   Get EXIF data for one or more image files.

Args:
   - file_paths (Iterable[FilePath]): Paths to image files.
   - tag_filter (Optional[Iterable[Union[str, int]]]): Tags to filter by (names or IDs).
   - thumbnail (bool): If True, get tags from the thumbnail IFD.

Returns:
   - dict[str, dict[int, ExifEntry]]: Mapping from file path to tag ID to EXIF entry.

Example::

   get_exif(['img1.jpg', 'img2.jpg'], tag_filter=['Make', 'Model'])
