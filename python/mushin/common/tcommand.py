# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
a Command subclass for Twisted-using commands.
"""

import sys

from mushin.extern.command import tcommand

from twisted.internet import reactor, defer

# Because we run a reactor and use deferreds, the flow is slightly different
# from the usual Command flow.

# It will then parse the command line, allowing all subcommands to
# hook into this step with their respective handleOptions/parse/do methods.

# Subcommands are expected to return a deferred
# and set the exit state.

# The Twisted root command will take care of stopping the reactor and returning
# the exit value.


from mushin.extern.command import tcommand

from . import logcommand

class TwistedCommand(tcommand.TwistedCommand, logcommand.LogCommand):
    def debug(self, format, *args):
        logcommand.LogCommand.debug(self, format, *args)
    def warning(self, format, *args):
        logcommand.LogCommand.warning(self, format, *args)

class LogReactorCommand(tcommand.ReactorCommand, logcommand.LogCommand):
    def debug(self, format, *args):
        logcommand.LogCommand.debug(self, format, *args)
    def warning(self, format, *args):
        logcommand.LogCommand.warning(self, format, *args)

