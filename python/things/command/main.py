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

def display(thing):
    # FIXME: colorize
    blocks = []
    blocks.append('%s:(%.2f)' % (thing.id[:4], thing.priority()))
    blocks.append(thing.title)

    if thing.contexts:
        blocks.extend(['@%s' % c for c in thing.contexts]) 
    if thing.projects:
        blocks.extend(['p:%s' % p for p in thing.projects]) 
    if thing.statuses:
        blocks.extend(['!%s' % s for s in thing.statuses]) 

    if thing.urgency is not None:
        blocks.append('U:%d' % thing.urgency)
    if thing.importance is not None:
        blocks.append('I:%d' % thing.importance)

    # FIXME: format with H/M/S/...
    if thing.time is not None:
        blocks.append('T:%d' % thing.time)

    if thing.start is not None:
        blocks.append('S:%s' % thing.start.strftime('%Y-%m-%d'))
    if thing.due is not None:
        blocks.append('D:%s' % thing.due.strftime('%Y-%m-%d'))

    if thing.complete:
        blocks.append('C:%s' % thing.complete)

    return " ".join(blocks)

def display_things(result):
    count = 0

    for thing in result:
        print display(thing)
        count += 1

    print '%d open things' % count


class List(logcommand.LogCommand):
    summary = "list all open things, ordered by priority (?)."

    def do(self, args):
        from things.model import couch
        server = couch.Server()

        # FIXME: make the view calculate and sort by priority
        display_things(server.view('open-things'))

class Search(logcommand.LogCommand):
    summary = "search for things"

    description = """
    p:(project) search for things in the given project
    """
    def do(self, args):
        from things.common import parse
        filter = parse.parse(" ".join(args))

        from things.model import couch
        server = couch.Server()

        # pick the view giving us the most resolution
        result = None

        for fattribute in ['urgency', 'importance']:
            if filter.has_key(fattribute):
                self.debug('viewing on %s' % fattribute)
                result = server.view('open-things-by-%s' % fattribute,
                    key=filter[fattribute])
                break

        # fall back to getting all
        if not result:
            self.debug('getting all open things')
            result = server.view('open-things')

        # now apply all filters in a row
        for attribute in ['urgency', 'importance', 'time']:
            if filter.has_key(attribute) and attribute != fattribute:
                self.debug('filtering on %s: %s' % (attribute, filter[attribute]))
                result = [t for t in result if str(t[attribute]).find(str(filter[attribute])) > -1]

        # separate because filter has singular, Thing has plural
        for attribute in ['project', 'context']:
            if filter.has_key(attribute) and attribute != fattribute:
                self.debug('filtering on %s' % attribute)
                # FIXME: pluralize to map to couchdb Thing will not work for
                # statuses
                result = [t for t in result if str(t[attribute + 's']).find(str(filter[attribute])) > -1]
         
        # now filter on title
        if filter['title']:
            result = [t for t in result if t.title.find(filter['title']) > -1]

        display_things(result)

class Show(logcommand.LogCommand):
    summary = "show one thing"

    def do(self, args):
        from things.model import couch
        server = couch.Server()

        # convert argument, which is shortened _id, to start/end range
        startkey = args[0]
        endkey = hex(int(startkey, 16) + 1)[2:]
        self.debug('Looking up from %s to %s' % (startkey, endkey))

        # FIXME: make the view calculate and sort by priority
        things = list(server.view('things-by-id', startkey=startkey, endkey=endkey))
        if len(things) == 0:
            print "No thing found."
        elif len(things) > 1:
            for t in things:
                print display(t)
            print "%d things found, please be more specific." % len(things)
        else:
            print display(things[0])



class GTD(logcommand.LogCommand):
    # FIXME: this causes doc.py to list commands as being doc.py
    usage = "%prog %command"
    usage = "gtd %command"
    description = """Get things done.

Things gives you a tree of subcommands to work with.
You can get help on subcommands by using the -h option to the subcommand.
"""

    subCommandClasses = [List, Search, Show, ]

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
