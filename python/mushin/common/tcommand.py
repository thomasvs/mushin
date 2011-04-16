# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
a Command subclass for Twisted-using commands.
"""

import sys

from twisted.internet import reactor, defer

# Because we run a reactor and use deferreds, the flow is slightly different
# from the usual Command flow.

# It will then parse the command line, allowing all subcommands to
# hook into this step with their respective handleOptions/parse/do methods.

# Subcommands are expected to return a deferred
# and set the exit state.

# The Twisted root command will take care of stopping the reactor and returning
# the exit value.


from mushin.extern.command import command

from . import logcommand

# FIXME: remove logcommand as a dependency
class TwistedCommand(logcommand.LogCommand):

    def parse(self, argv):
        """
        @returns: a deferred that will fire when the command is done.
        """
        self.debug('parse: chain up')
        # chain up to parent first
        # all subcommands will have a chance to chain up to the deferred
        d = defer.Deferred()
        d.addCallback(lambda _: defer.maybeDeferred(logcommand.LogCommand.parse, self, argv))

        def parseCb(ret):
            if ret is None:
                self.debug('parse returned None, help/usage printed')
                ret = 0
            elif ret:
                self.debug('parse returned %r' % ret)
            elif self.parser.help_printed or self.parser.usage_printed:
                ret = 0
            self.debug('parse: cb: done')
            return ret

        def eb(failure):
            self.debug('parse: eb: failure %s' %
                failure.getErrorMessage())
            if failure.check(command.CommandExited):
                sys.stderr.write(failure.value.msg + '\n')
                reason = failure.value.code
                return reason
            else:
                return failure

        d.addCallback(parseCb)
        d.addErrback(eb)

        d.callback(None)
        return d
