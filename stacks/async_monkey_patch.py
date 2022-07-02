"""
This module just monkey patches everything needed for Gevent.

Note: this module MUST NOT import anything that may be monkey patched
later, or you'll hit:
https://github.com/gevent/gevent/issues/1016

See also:
http://www.gevent.org/intro.html#monkey-patching

The monkey patches are not applied if this is run under ipython, however -
since gevent crashes ipython.

Usage:

.. code:: python

   import stacks.async_monkey_patch

"""

import sys
from os import getenv

if 'IPython' not in sys.modules and not getenv('BYPASS_GEVENT'):
    # Patch socket, threads etc - all applicable to the stdlib
    import gevent.monkey
    gevent.monkey.patch_all()

    print('Monkey patches applied for gevent.')
