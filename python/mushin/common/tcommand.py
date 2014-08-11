# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
a Command subclass for Twisted-using commands.
"""

# Because we run a reactor and use deferreds, the flow is slightly different
# from the usual Command flow.

# It will then parse the command line, allowing all subcommands to
# hook into this step with their respective handleOptions/parse/do methods.

# Subcommands are expected to return a deferred
# and set the exit state.

# The Twisted root command will take care of stopping the reactor and returning
# the exit value.

from twisted.internet import error

from mushin.common import failure as cfailure
from mushin.extern.command import command, tcommand

from . import logcommand


class TwistedCommand(tcommand.TwistedCommand, logcommand.LogCommand):
# FIXME: looks like we don't need to chain up to make this work
# FIXME: if we do need to chain up again, add info, and make sure we
#        adjust the logging depth since this chaining adds one level

#    def debug(self, format, *args):
#        logcommand.LogCommand.debug(self, format, *args)
#    def warning(self, format, *args):
#        logcommand.LogCommand.warning(self, format, *args)

    def do(self, args):
        d = tcommand.TwistedCommand.do(self, args)

        def connectionRefusedEb(failure):
            self.debug('connection closed, %r', failure)
            self.debug(cfailure.getAllTracebacks(failure))

            failure.trap(error.ConnectionRefusedError)
            self.debug('connection refused')
            msg = 'Could not make a connection to CouchDB.'
            raise command.CommandError(msg)

        d.addErrback(connectionRefusedEb)

        return d


class LogReactorCommand(tcommand.ReactorCommand, logcommand.LogCommand):
    pass
#    def debug(self, format, *args):
#        logcommand.LogCommand.debug(self, format, *args)
#    def warning(self, format, *args):
#        logcommand.LogCommand.warning(self, format, *args)

