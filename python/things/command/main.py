# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import sys

from things.common import log, logcommand

#from things.command import thing

SYNTAX = """
When adding or searching for things, the following syntax is used:

 - text         title
 - p:project    project named 'project'
 - @context     context named @context
 - !status      status flags like someday, waitingfor, nextaction
 - U:x          urgency x
 - I:x          importance i
 - C:x          % complete
 - R:xxx[WDHM]  xxx weeks/days/hours/minutes
 - T:xxx[WDHM]  xxx weeks/days/hours/minutes
 - S:YYYY-MM-HH start date
 - D:YYYY-MM-HH due date
 - E:YYYY-MM-HH end date

"""
# Colorization
COLOR_CODES = ( { 'none': "",
                  'default': "\033[0m",
                  # primary colors
                  'black': "\033[0;30m",
                  'grey': "\033[0;37m",
                  'red': "\033[0;31m",
                  'green': "\033[0;32m",
                  'blue': "\033[0;34m",
                  'purple': "\033[0;35m",
                  'cyan': "\033[0;36m",
                  'yellow': "\033[0;33m",
                  # bold colors
                  'white': "\033[1;37m",
                  'dark_grey': "\033[1;30m",
                  'dark_red': "\033[1;31m",
                  'dark_green': "\033[1;32m",
                  'dark_blue': "\033[1;34m",
                  'dark_purple': "\033[1;35m",
                  'dark_cyan': "\033[1;36m",
                  'dark_yellow': "\033[1;33m",
                  # other colors                  
                  'normal': "\x1b[0;37;40m",
                  'title': "\x1b[1;32;40m",
                  'heading': "\x1b[1;35;40m",
                  'bold': "\x1b[1;35;40m",
                  'important': "\x1b[1;31;40m",
                  'error': "\x1b[1;31;40m",
                  'reverse': "\x1b[0;7m",
                  'row0': "\x1b[0;35;40m",
                  'row1': "\x1b[0;36;40m" } )

# Default colors
DEFAULT_COLOR    = COLOR_CODES['default']
CONTEXT_COLOR    = COLOR_CODES['dark_yellow']
PROJECT_COLOR    = COLOR_CODES['dark_purple']
STATUS_COLOR     = COLOR_CODES['dark_green']
REFERENCE_COLOR  = COLOR_CODES['dark_blue']
URGENCY_COLOR    = COLOR_CODES['red']
IMPORTANCE_COLOR = COLOR_CODES['red']
COMPLETE_COLOR   = COLOR_CODES['white']
TIME_COLOR       = COLOR_CODES['cyan']
RECURRENCE_COLOR = COLOR_CODES['cyan']
START_COLOR      = COLOR_CODES['red']
DUE_COLOR        = COLOR_CODES['red']
END_COLOR        = COLOR_CODES['green']

# priority colors; from 0 to 5
P_COLORS = [
  COLOR_CODES['dark_green'],
  COLOR_CODES['yellow'],
  COLOR_CODES['dark_yellow'],
  COLOR_CODES['red'],
  COLOR_CODES['dark_red'],
  COLOR_CODES['dark_purple'],
]

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

def display(thing, colored=True):
    def color(text, code):
        if not colored:
            return text

        return code + text + DEFAULT_COLOR

    def pcolor(text, priority):
        # color according to priority
        if not colored:
            return text

        return P_COLORS[int(priority)] + text + DEFAULT_COLOR

    blocks = []
    blocks.append(color('%s' % thing.shortid(), TIME_COLOR))
    blocks.append(pcolor('(%.2f)' % thing.priority(), thing.priority()))
    blocks.append(thing.title)

    if thing.contexts:
        blocks.extend([color('@%s' % c, CONTEXT_COLOR)
            for c in thing.contexts]) 
    if thing.projects:
        blocks.extend([color('p:%s' % p, PROJECT_COLOR)
            for p in thing.projects]) 
    if thing.statuses:
        blocks.extend([color('!%s' % s, STATUS_COLOR)
             for s in thing.statuses]) 

    if thing.urgency is not None:
        blocks.append(color('U:%d', URGENCY_COLOR) % thing.urgency)
    if thing.importance is not None:
        blocks.append(color('I:%d', IMPORTANCE_COLOR) % thing.importance)

    # FIXME: format with H/M/S/...
    if thing.time is not None:
        blocks.append(color(
            'T:%d' % thing.time, TIME_COLOR))

    if thing.start is not None:
        blocks.append(color(
            'S:%s' % thing.start.strftime('%Y-%m-%d'), START_COLOR))
    if thing.due is not None:
        blocks.append(color(
            'D:%s' % thing.due.strftime('%Y-%m-%d'), DUE_COLOR))
    if thing.end is not None:
        blocks.append(color(
            'E:%s' % thing.due.strftime('%Y-%m-%d'), END_COLOR))

    if thing.complete:
        blocks.append(color('C:%s' % thing.complete, COMPLETE_COLOR))

    return " ".join(blocks)

def display_things(result):
    count = 0

    for thing in result:
        print display(thing)
        count += 1

    print '%d open things' % count

class Add(logcommand.LogCommand):
    summary = "Add a thing"

    description = """Adds a thing.\n""" + SYNTAX

    def do(self, args):
        from things.common import parse
        new = parse.parse(" ".join(args))
        print new

        from things.model import couch
        server = couch.Server()

        thing = couch.thing_from_dict(new)
        server.save(thing)

        print 'Added thing "%s" (%s)' % (thing.title, thing.id)

class Delete(logcommand.LogCommand):
    summary = "delete one thing"
    aliases = ['del', ]

    def do(self, args):
        from things.model import couch
        server = couch.Server()
        thing = lookup(server, args[0])

        if thing:
            server.delete(thing)
            print 'Deleted thing "%s" (%s)' % (thing.title, thing.id)

class List(logcommand.LogCommand):
    summary = "list all open things, ordered by priority (?)."

    def do(self, args):
        from things.model import couch
        server = couch.Server()

        # FIXME: make the view calculate and sort by priority
        display_things(server.view('open-things'))

class Search(logcommand.LogCommand):
    summary = "search for things"
    description = """Search for things.\n""" + SYNTAX

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
                self.debug('filtering on %s: %s' % (
                    attribute, filter[attribute]))
                result = [t for t in result 
                    if str(t[attribute]).find(str(filter[attribute])) > -1]

        # separate because filter has singular, Thing has plural
        for attribute in ['projects', 'contexts']:
            if filter.has_key(attribute) and attribute != fattribute:
                self.debug('filtering on %s: %s' % (
                    attribute, filter[attribute]))

                projects = filter[attribute]
                new = []
                for t in result:
                    # multiple values for an attribute should be anded
                    match = True
                    for p in projects:
                        if str(t[attribute]).find(p) == -1:
                            match = False
                            break
                    if match:
                        new.append(t)

                result = new

         
        # now filter on title
        if filter['title']:
            self.debug('filtering on title %s' % filter['title'])
            result = [t for t in result if t.title.find(filter['title']) > -1]

        display_things(result)

class Show(logcommand.LogCommand):
    summary = "show one thing"

    def do(self, args):
        from things.model import couch
        server = couch.Server()
        print lookup(server, args[0])

def lookup(server, shortid):
        # convert argument, which is shortened _id, to start/end range
        startkey = shortid
        endkey = hex(int(startkey, 16) + 1)[2:]
        # leading 0's are now dropped, so readd them
        endkey = '0' * (len(startkey) - len(endkey)) + endkey

        log.debug('lookup', 'Looking up from %s to %s' % (startkey, endkey))

        # FIXME: make the view calculate and sort by priority
        things = list(server.view('things-by-id',
            startkey=startkey, endkey=endkey))
        if len(things) == 0:
            print "No thing found."
        elif len(things) > 1:
            for t in things:
                print display(t)
            print "%d things found, please be more specific." % len(things)
        else:
            return things[0]



class GTD(logcommand.LogCommand):
    # FIXME: this causes doc.py to list commands as being doc.py
    usage = "%prog %command"
    #usage = "gtd %command"
    description = """Get things done.

Things gives you a tree of subcommands to work with.
You can get help on subcommands by using the -h option to the subcommand.
"""

    subCommandClasses = [Add, Delete, List, Search, Show, ]

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
        cmd = logcommand.command.commandToCmd(self)
        cmd.prompt = 'GTD> '
        while not cmd.exited:
            cmd.cmdloop()
