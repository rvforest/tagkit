tagkit.exceptions
=================

The ``tagkit.exceptions`` module defines custom exceptions used throughout tagkit for error handling.

**Usage Example:**

.. code-block:: python

   from tagkit.exceptions import TagkitError
   try:
       # some tagkit operation
       pass
   except TagkitError as e:
       print(f"Tagkit error: {e}")

.. autosummary::
   :toctree: _autosummary

   # List main exceptions here if any

.. automodule:: tagkit.exceptions
   :members:
   :undoc-members:
   :show-inheritance:
