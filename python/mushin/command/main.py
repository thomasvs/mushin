# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import datetime
import sys

from mushin.common import log, logcommand, parse
from mushin.model import couch
from mushin.command import project, display, list as llist, replicate, thing

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

class Add(logcommand.LogCommand):
    summary = "Add a thing"

    description = """Adds a thing.\n""" + SYNTAX

    def do(self, args):
        new = parse.parse(" ".join(args))

        server = couch.Server()

        thing = couch.thing_from_dict(new)
        server.save(thing)

        self.stdout.write('Added thing "%s" (%s)\n' % (thing.title, thing.id))

class Delete(logcommand.LogCommand):
    summary = "delete one thing"
    aliases = ['del', ]

    def do(self, args):
        server = couch.Server()
        thing = lookup(self, server, args[0])

        if thing:
            server.delete(thing)
            self.stdout.write('Deleted thing "%s" (%s)\n' % (
                thing.title, thing.id))

class Done(logcommand.LogCommand):
    summary = "mark a thing as done"

    def do(self, args):
        server = couch.Server()
        thing = lookup(self, server, args[0])

        if thing:
            if thing.complete == 100:
                self.stdout.write('Already done "%s" (%s)\n' % (
                    thing.title, thing.id))
            else:
                if thing.recurrence:
                    self.debug('done recurring thing, rescheduling')
                    if not thing.due:
                        thing.due = datetime.datetime.now()

                    thing.start = thing.due
                    thing.due = thing.start + \
                        datetime.timedelta(seconds=thing.recurrence)
                    server.save(thing)
                    self.stdout.write('Rescheduling for %s "%s" (%s)\n' % (
                        thing.due, thing.title, thing.id))
                else:
                    thing.complete = 100
                    thing.end = datetime.datetime.now()
                    server.save(thing)
                    self.stdout.write('Marked "%s" (%s) as done\n' % (
                        thing.title, thing.id))

class Edit(logcommand.LogCommand):
    summary = "edit a thing"
    usage = "#shortid"

    def do(self, args):
        try:
            import readline
        except ImportError:
            self.stdout.write("Cannot edit without the 'readline' module!\n")
            return

        # Parse command line 
        shortid = args[0]

        if not shortid:
            return

        server = couch.Server()
        thing = lookup(self, server, shortid)
        if not thing:
            return

        def pre_input_hook():
            readline.insert_text(display.display(
                thing, shortid=False, colored=False))
            readline.redisplay()

            # Unset the hook again 
            readline.set_pre_input_hook(None)

        readline.set_pre_input_hook(pre_input_hook)

        line = raw_input("GTD edit> ")
        # Remove edited line from history: 
        #   oddly, get_history_item is 1-based,
            #   but remove_history_item is 0-based 
        readline.remove_history_item(readline.get_current_history_length() - 1)
        try:
            d = parse.parse(line)
        except ValueError, e:
            self.stderr.write('Could not parse line: %s\n' %
                log.getExceptionMessage(e))
            return 3

        thing.set_from_dict(d)

        server.save(thing)
        self.stdout.write('Edited thing "%s" (%s)\n' % (thing.title, thing.id))

class Search(logcommand.LogCommand):
    summary = "search for things"
    description = """Search for things.\n""" + SYNTAX

    def do(self, args):
        from mushin.common import parse
        filter = parse.parse(" ".join(args))
        self.debug('parsed filter: %r' % filter)

        server = couch.Server()

        # pick the view giving us the most resolution
        result = [
        found = False

        for fattribute in ['urgency', 'importance']:
            found = True
            if filter.has_key(fattribute):
                self.debug('viewing on %s' % fattribute)
                result = server.view('open-things-by-%s' % fattribute,
                    include_docs=True,
                    key=filter[fattribute])
                break

        # fall back to getting all
        if not found and result:
            self.debug('getting all open things')
            result = server.view('open-things', include_docs=True)

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
        if result and filter['title']:
            self.debug('filtering on title %s' % filter['title'])
            result = [t for t in result if t.title.find(filter['title']) > -1]

        display.Displayer().display_things(result)

class Show(logcommand.LogCommand):
    summary = "show one thing"

    def do(self, args):
        server = couch.Server()
        # FIXME: format nicer
        self.stdout.write("%s\n" % lookup(self, server, args[0]))

def lookup(cmd, server, shortid):
        # convert argument, which is shortened _id, to start/end range
        startkey = shortid
        endkey = hex(int(startkey, 16) + 1)[2:]
        # leading 0's are now dropped, so readd them
        endkey = '0' * (len(startkey) - len(endkey)) + endkey

        log.debug('lookup', 'Looking up from %s to %s' % (startkey, endkey))

        # FIXME: make the view calculate and sort by priority
        things = list(server.view('things-by-id', include_docs=True,
            startkey=startkey, endkey=endkey))
        if len(things) == 0:
            cmd.stdout.write("No thing found.\n")
        elif len(things) > 1:
            for t in things:
                cmd.stdout.write("%s\n" % display.display(t))
            cmd.stdout.write("%d things found, please be more specific.\n" % 
                len(things))
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

    subCommandClasses = [Add, Delete, Done, Edit, llist.List,
        project.Project, replicate.Replicate, Search, Show, 
        thing.Thing]

    def addOptions(self):
        # FIXME: is this the right place ?
        log.init()

        self.parser.add_option('-v', '--version',
                          action="store_true", dest="version",
                          help="show version information")

    def handleOptions(self, options):
        if options.version:
            #from mushin.configure import configure
            #print "rip %s" % configure.version
            sys.exit(0)

    def do(self, args):
        cmd = logcommand.command.commandToCmd(self)
        cmd.prompt = 'GTD> '
        while not cmd.exited:
            cmd.cmdloop()
