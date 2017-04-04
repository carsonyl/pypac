Developer interface
===================

These are the interfaces that PyPAC exposes to developers.

Main interface
--------------

.. automodule:: pypac.api

.. autoclass:: pypac.PACSession
   :special-members:
   :members:


.. autofunction:: pypac.get_pac

.. autofunction:: pypac.collect_pac_urls

.. autofunction:: pypac.download_pac


PAC parsing and execution
-------------------------

.. automodule:: pypac.parser

.. autoclass:: pypac.parser.PACFile
   :special-members:
   :members:

.. autofunction:: pypac.parser.parse_pac_value

.. autofunction:: pypac.parser.proxy_url

.. autoclass:: pypac.parser.MalformedPacError

.. autoclass:: pypac.parser.PyimportError

.. autoclass:: pypac.parser.PacComplexityError


PAC JavaScript functions
^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: pypac.parser_functions
   :members:


Proxy resolution
----------------

.. automodule:: pypac.resolver

.. autoclass:: pypac.resolver.ProxyResolver

.. autofunction:: pypac.resolver.add_proxy_auth

.. autofunction:: pypac.resolver.proxy_parameter_for_requests

.. autoclass:: pypac.resolver.ProxyConfigExhaustedError


WPAD functions
--------------

.. automodule:: pypac.wpad
   :members:


Windows stuff
-------------

.. automodule:: pypac.windows
   :members:

.. autoclass:: pypac.windows.NotWindowsError
