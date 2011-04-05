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

class TwistedCommand(logcommand.LogCommand):

    def parse(self, argv):
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
            reactor.exitStatus = ret
            reactor.callLater(0, reactor.stop)
            return reactor.exitStatus

        def eb(failure):
            self.debug('parse: eb: failure %s' %
                failure.getErrorMessage())
            if failure.check(command.CommandExited):
                sys.stderr.write(failure.value.msg + '\n')
                reactor.exitStatus = failure.value.code
            else:
                sys.stderr.write(failure.getTraceback())
                
                sys.stderr.write("Failure %r: %s\n" % (
                    failure, failure.getErrorMessage()))
                reactor.exitStatus = 1

            reactor.callLater(0, reactor.stop)
            return

        d.addCallback(parseCb)
        d.addErrback(eb)

        reactor.callLater(0L, d.callback, None)
        # now run the reactor
        self.debug('parse: run the reactor')
        self.run()
        self.debug('parse: ran the reactor')

        return d

    def run(self):
        """
        Run the reactor.

        Resets .exitStatus, and returns its value after running the reactor.
        """
        # run the reactor

        self.debug('running reactor')
        # We cheat by putting the exit code in the reactor.
        reactor.exitStatus = 0
        reactor.run()
        self.debug('ran reactor')

        return reactor.exitStatus
