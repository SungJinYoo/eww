# -*- coding: utf-8 -*-
"""
    eww.quitterproxy
    ~~~~~~~~~~~~~~~~

    QuitterProxy is a threading.local based proxy used to override the normal
    quit behavior on demand.

    Specifically, calling quit()/exit() will normally raise the SystemExit
    exception, *and* close stdin.  We can catch the SystemExit exception, but
    if stdin is closed, it kills our socket.

    Normally that's exactly the behavior you want, but because we embed a REPL
    in the eww console, exiting the REPL can cause the entire session to exit,
    not just the REPL.

    If you want to make modifications to the quit or exit builtins, you can use
    the public register/unregister APIs on QuitterProxy for it.  More info on
    their use is available in the 'Public API' section of the documentation.

"""

import threading
import logging

LOGGER = logging.getLogger(__name__)

class QuitterProxy(object):
    """QuitterProxy provides a proxy object meant to replace __builtin__.[quit,
    exit].  You can register your own quit customization by calling
    register()/unregister().  More detail is available in the public API
    documentation.
    """

    def __init__(self, original_quit):
        """Creates the thread local and registers the original quit."""
        self.quit_routes = threading.local()
        self.original_quit = original_quit
        self.register(original_quit)

    def __repr__(self):
        """We just call self here, that way people can use e.g. 'exit' instead
        of 'exit()'.
        """
        self()

    def register(self, quit_method):
        """Used to register a quit method in a particular thread."""
        self.quit_routes.quit = quit_method

    def unregister(self):
        """Used to unregister a quit method in a particular thread."""
        try:
            del self.quit_routes.quit
        except AttributeError:
            LOGGER.debug('unregister() called, but no quit method registered.')

    def __call__(self, code=None):
        """Calls the registered quit method."""
        try:
            self.quit_routes.quit(code)
        except AttributeError:
            self.original_quit(code)

def safe_quit(code=None):
    """This version of the builtin quit method raises a SystemExit, but does
    *not* close stdin.
    """
    raise SystemExit(code)
