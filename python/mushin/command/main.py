# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import datetime
import sys

from mushin.extern.command import command
from mushin.extern.paisley import views

from mushin.common import log, logcommand, parse, format, tcommand, app
from mushin.model import couch
from mushin.command import project, display, conflict
from mushin.command import list as llist, replicate, thing

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
    log.init()

    # make sure argv, coming from the command line, is converted to
    # unicode
    argv = [a.decode('utf-8') for a in argv]
    c = GTD()

    # use a list so a callback gets it by reference and can modify it
    ret = [None, ]

    d = c.parse(argv)
    def cb(r, ret):
        ret[0] = r

    def systemEb(failure):
        failure.trap(SystemError)
        sys.stderr.write('mushin: error: %s\n' % e.args)
        return 255
    d.addCallback(cb, ret)
    d.addErrback(systemEb)

    ret = ret[0]
    if ret is None:
        return 0

    return ret

class Add(logcommand.LogCommand):
    summary = "Add a thing"

    description = """Adds a thing.\n""" + SYNTAX

    def do(self, args):
        new = parse.parse(u" ".join(args))
        if not new.has_key('start'):
            new['start'] = datetime.datetime.now()

        server = self.getRootCommand().getServer()

        thing = couch.thing_from_dict(new)
            
        d = server.save(thing)

        def saveCb(ret):
            self.stdout.write('Added thing "%s" (%s)\n' % (
                thing.title.encode('utf-8'), ret['id']))
        d.addCallback(saveCb)

        return d

class Delay(logcommand.LogCommand):
    summary = "delay one thing"

    def do(self, args):
        server = self.getRootCommand().getServer()
        shortid = args[0]
        d = lookup(self, server, shortid)
        def lookupCb(thing):
            if not thing:
                self.stdout.write('No thing found for %s\n' % shortid)
                return
            deltaHours = parse.parse_timedelta(args[1])
            if not deltaHours:
                self.stdout.write('Delay %s is not valid\n' % args[1])
                return

            if not thing.due:
                self.stdout.write('Thing %s has no due date set\n' % shortid)
                return

            thing.due += datetime.timedelta(hours=deltaHours)

            d2 = server.save(thing)
            def savedCb(_):
                self.stdout.write('Thing %s delayed by %s\n' % (
                    shortid, format.formatTime(deltaHours * 60)))
            d2.addCallback(savedCb)
            return d2

        d.addCallback(lookupCb)
        return d


class Delete(logcommand.LogCommand):
    summary = "delete one thing"
    aliases = ['del', ]

    def do(self, args):
        server = self.getRootCommand().getServer()
        d = lookup(self, server, args[0])

        def lookupCb(thing):
            if thing:
                d2 = server.delete(thing)
                def deleteCb(_):
                    self.stdout.write('Deleted thing "%s" (%s)\n' % (
                        thing.title.encode('utf-8'), thing.id))
                d2.addCallback(deleteCb)
                return d2
        d.addCallback(lookupCb)
        return d

class Done(logcommand.LogCommand):
    summary = "mark a thing as done"

    def do(self, args):
        server = self.getRootCommand().getServer()
        d = lookup(self, server, args[0], ignoreDone=True)

        def lookupCb(thing):
            if thing:
                if thing.complete == 100:
                    self.stdout.write('Already done "%s" (%s)\n' % (
                        thing.title.encode('utf-8'), thing.id))
                    return 1
                else:
                    if thing.finish():
                        d2 = server.save(thing)
                        def saveCb(_):
                            self.stdout.write('Marked "%s" (%s) as done\n' % (
                                thing.title.encode('utf-8'), thing.id))
                            return 0
                        d2.addCallback(saveCb)
                        return d2
                    else:
                        server.save(thing)
                        self.stdout.write('Rescheduling for %s "%s" (%s)\n' % (
                            thing.due, thing.title.encode('utf-8'), thing.id))
        d.addCallback(lookupCb)
        return d


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

        server = self.getRootCommand().getServer()
        d = lookup(self, server, shortid)

        def lookupCb(thing):
            if not thing:
                self.stdout.write('No thing found for %s\n' % shortid)
                return

            def pre_input_hook():
                readline.insert_text(display.display(
                    thing, shortid=False, colored=False))
                readline.redisplay()

                # Unset the hook again 
                readline.set_pre_input_hook(None)

            readline.set_pre_input_hook(pre_input_hook)

            line = raw_input("GTD edit> ").decode('utf-8')
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

            d2 = server.save(thing)
            def saveCb(_, thing):
                self.stdout.write('Edited thing "%s" (%s)\n' % (
                    thing.title.encode('utf-8'), thing.id))
            d2.addCallback(saveCb, thing)
            return d2

        d.addCallback(lookupCb)
        return d

class Search(logcommand.LogCommand):
    summary = "search for things"
    description = """Search for things.\n""" + SYNTAX

    def addOptions(self):
        self.parser.add_option('-c', '--count',
                          action="store_true", dest="count",
                          help="only show the number of items matching")

    def do(self, args):
        from mushin.common import parse
        filter = parse.parse(" ".join(args))
        self.debug('parsed filter: %r' % filter)

        server = self.getRootCommand().getServer()

        # pick the view giving us the most resolution
        result = []
        found = False

        for fattribute in ['urgency', 'importance']:
            if filter.has_key(fattribute):
                found = True
                self.debug('viewing on %s' % fattribute)
                view = views.View(server._db, server._dbName, 'mushin',
                    'open-things-by-%s' % fattribute, couch.Thing,
                    include_docs=True,
                    key=filter[fattribute])
                break

        # fall back to getting all
        if not found:
            self.debug('getting all open things')
            view = views.View(server._db, server._dbName, 'mushin',
                'open-things', couch.Thing,
                include_docs=True,
                key=filter[fattribute])

        d = view.queryView()
        def viewCb(result):
            # now apply all filters in a row
            for attribute in ['urgency', 'importance', 'time']:
                if filter.has_key(attribute) and attribute != fattribute:
                    self.debug('filtering on %s: %s' % (
                        attribute, filter[attribute]))
                    result = [t for t in result 
                        if str(t[attribute]).find(str(filter[attribute])) > -1]

            # separate because filter has singular, Thing has plural
            for attribute in ['projects', 'contexts', 'statuses']:
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
            result = list(result)
            if result and filter['title']:
                self.debug('filtering on title %s' % filter['title'])
                result = [t for t in result if t.title.find(filter['title']) > -1]

            if self.options.count:
                self.stdout.write('%d open things\n' % len(result))
            else:
                display.Displayer(self.stdout).display_things(result)
        d.addCallback(viewCb)

        return d

class Show(logcommand.LogCommand):
    summary = "show one thing"

    def do(self, args):
        server = self.getRootCommand().getServer()
        # FIXME: format nicer
        d = lookup(self, server, args[0])
        def lookupCb(thing):
            if thing:
                self.stdout.write("%s\n" % thing)
        d.addCallback(lookupCb)
        return d

def lookup(cmd, server, shortid, ignoreDone=False):
        # convert argument, which is shortened _id, to start/end range
        startkey = shortid
        try:
            endkey = hex(int(startkey, 16) + 1)[2:]
        except ValueError:
            cmd.stdout.write("Please give a valid id.\n")
            return

        # leading 0's are now dropped, so readd them
        endkey = '0' * (len(startkey) - len(endkey)) + endkey

        log.debug('lookup', 'Looking up from %s to %s' % (startkey, endkey))

        # FIXME: make the view calculate and sort by priority
        d = server.view('things-by-id-reversed', include_docs=True,
            startkey=startkey, endkey=endkey)

        def viewCb(things):
            things = list(things)
            if len(things) == 0:
                cmd.stdout.write("No thing found.\n")
                return

            # we let just one result go through, even if ignoreDone is True,
            # because our caller can show output about a task that is already done.
            if len(things) == 1:
                return things[0]

            if ignoreDone:
                things = [t for t in things if t.complete < 100]

            if len(things) > 1:
                for t in things:
                    cmd.stdout.write("%s\n" % display.display(t))
                cmd.stdout.write("%d things found, please be more specific.\n" % 
                    len(things))
                return

            return things[0]
        d.addCallback(viewCb)
        return d

class GTD(tcommand.TwistedCommand):
    # FIXME: this causes doc.py to list commands as being doc.py
    usage = "%prog %command"
    #usage = "gtd %command"
    description = """Get things done.

Things gives you a tree of subcommands to work with.
You can get help on subcommands by using the -h option to the subcommand.
"""

    subCommandClasses = [Add, conflict.Conflict, Delay, Delete, Done, Edit,
        llist.List,
        project.Project, replicate.Replicate, Search, Show, 
        thing.Thing]

    def addOptions(self):
        self.parser.add_option('-D', '--database',
                          action="store", dest="database",
                          default="mushin",
                          help="database to connect to (default: %default)")
        self.parser.add_option('-v', '--version',
                          action="store_true", dest="version",
                          help="show version information")

    def handleOptions(self, options):
        if options.version:
            # FIXME: todo
            #from mushin.configure import configure
            #self.stdout.write("mushin %s\n" % configure.version)
            sys.exit(0)
        self.dbName = options.database
        self.info("Using database %s", self.dbName)

    def do(self, args):
        # start a command line interpreter

        from mushin.extern.command import manholecmd
        class MyCmdInterpreter(manholecmd.CmdInterpreter):
            cmdClass = logcommand.command.commandToCmdClass(self)
            cmdClass.prompt = 'GTD> '

        class MyCmdManhole(manholecmd.CmdManhole):
            interpreterClass = MyCmdInterpreter
            

        manholecmd.runWithProtocol(MyCmdManhole)

    def getServer(self):
        # FIXME: should not be importing couchdb
        from couchdb import client
        try:
            server = couch.Server(db=self.dbName)
        except client.ResourceNotFound:
            raise command.CommandExited(
                1, "Could not find database %s" % self.db)
        return server

    def getNewServer(self):
        return app.Server(dbName=self.dbName)
