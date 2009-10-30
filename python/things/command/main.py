# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import sys

from things.common import log, logcommand

#from things.command import thing

def main(argv):
    c = GTD()
    try:
        ret = c.parse(argv)
    except SystemError, e:
        sys.stderr.write('rip: error: %s\n' % e.args)
        return 255
    except ImportError, e:
        # FIXME: decide how to handle
        raise
        # deps.handleImportError(e)
        # ret = -1

    if ret is None:
        return 0

    return ret

class List(logcommand.LogCommand):
    def do(self, args):
        from things.model import couch
        server = couch.Server()
        count = 0
        for thing in server.view('open-things'):
            print 'U:%s I:%s %s' % (thing.urgency or '?', thing.importance or '?', thing.description)
            count += 1

        print '%d open things' % count

class GTD(logcommand.LogCommand):
    # FIXME: this causes doc.py to list commands as being doc.py
    usage = "%prog %command"
    usage = "gtd %command"
    description = """Get things done.

Things gives you a tree of subcommands to work with.
You can get help on subcommands by using the -h option to the subcommand.
"""

    subCommandClasses = [List, ]

    def addOptions(self):
        # FIXME: is this the right place ?
        log.init()

        self.parser.add_option('-v', '--version',
                          action="store_true", dest="version",
                          help="show version information")

    def handleOptions(self, options):
        if options.version:
            #from things.configure import configure
            #print "rip %s" % configure.version
            sys.exit(0)

    def do(self, args):
        print 'start command line interpreter'
