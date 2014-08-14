# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import datetime
import sys
import getpass

from twisted.internet import defer, error

from mushin.extern.command import command
from mushin.extern.command import manholecmd
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
    log.logTwisted()
    log.adaptStandardLogging('paisley', 'paisley', None)

    # get twisted logging in our logging
    log.logTwisted()

    # use observer for standard logging paisley uses
    from twisted.python import log as tplog
    observer = tplog.PythonLoggingObserver()
    observer.start()

    # make sure argv, coming from the command line, is converted to
    # unicode
    argv = [a.decode('utf-8') for a in argv]

    c = GTD()

    log.debug('main', 'invoking parse')

    from twisted.web import error

    try:
        ret = c.parse(argv)
        log.debug('main', 'invoked parse, ret %r' % ret)
    except command.CommandExited, e:
        ret = e.status
        if ret != 0:
            sys.stderr.write('mushin: error: %s\n' % e.output)
    except SystemError, e:
        sys.stderr.write('mushin: error: %s\n' % e.args)
        return 255
    except error.Error, e:
        sys.stderr.write('mushin: couchdb error: %s\n' % e)
        return 255
    except Exception, e:
        sys.stderr.write('mushin: internal error: %r\n' % e)
        return 255

    if ret is None:
        return 0

    return ret

class Add(tcommand.TwistedCommand):
    summary = "Add a thing"

    description = """Adds a thing.\n""" + SYNTAX

    def doLater(self, args):
        new = parse.parse(u" ".join(args))
        if not new.has_key('start'):
            new['start'] = datetime.datetime.now()

        newThing = couch.thing_from_dict(new)

        server = self.getRootCommand().getServer()

        d = server._db.infoDB(self.getRootCommand().dbName)

        def infoDBCb(_):
            createdBy = server.getCreatedBy()
            if not createdBy:
                # it's possible we don't have a session yet, try and get
                # a hoodie createdBy from the database name
                if server._dbName.startswith('user%2F'):
                    createdBy = server._dbName[7:]

            if createdBy:
                self.debug('createdBy %s' % createdBy)
                newThing.createdBy = createdBy

                # we assume it's now hoodie, so if no id is set, set a
                # hoodie-compatible one that starts with type
                if not 'id' in new:
                    newThing.setHoodieId()
                    self.debug('set hoodie-compatible id %s' % newThing.id)

            return server.save(newThing)
        d.addCallback(infoDBCb)

        def saveCb(ret):
            self.stdout.write('Added thing "%s" (%s)\n' % (
                newThing.title.encode('utf-8'),
                ret['id'][::-1].encode('utf-8')))
        d.addCallback(saveCb)

        return d

class Delay(tcommand.TwistedCommand):
    summary = "delay one thing"

    def doLater(self, args):
        server = self.getRootCommand().getServer()
        shortid = args[0]
        d = lookup(self, server, shortid)
        def lookupCb(thing):
            if not thing:
                self.stdout.write('No thing found for %s\n' % shortid.encode('utf-8'))
                return
            deltaHours = parse.parse_timedelta(args[1])
            if not deltaHours:
                self.stdout.write('Delay %s is not valid\n' % args[1])
                return

            if not thing.due:
                self.stdout.write('Thing %s has no due date set\n' % shortid.encode('utf-8'))
                return

            thing.due += datetime.timedelta(hours=deltaHours)

            d2 = server.save(thing)
            def savedCb(_):
                self.stdout.write('Thing %s delayed by %s\n' % (
                    shortid.encode('utf-8'), format.formatTime(deltaHours * 60)))
            d2.addCallback(savedCb)
            return d2

        d.addCallback(lookupCb)
        return d


class Delete(tcommand.TwistedCommand):
    summary = "delete one thing"
    aliases = ['del', ]

    def doLater(self, args):
        server = self.getRootCommand().getServer()
        d = lookup(self, server, args[0])

        def lookupCb(thing):
            if thing:
                d2 = server.delete(thing)
                def deleteCb(_):
                    self.stdout.write('Deleted thing "%s" (%s)\n' % (
                        thing.title.encode('utf-8'), thing.id[::-1].encode('utf-8')))
                d2.addCallback(deleteCb)
                return d2
        d.addCallback(lookupCb)
        return d

class Done(tcommand.TwistedCommand):
    summary = "mark a thing as done"

    def doLater(self, args):
        server = self.getRootCommand().getServer()
        d = lookup(self, server, args[0], ignoreDone=True)

        def lookupCb(thing):
            if thing:
                if thing.complete == 100:
                    self.stdout.write('Already done "%s" (%s)\n' % (
                        thing.title.encode('utf-8'), thing.id[::-1].encode('utf-8')))
                    return 1
                else:
                    if thing.finish():
                        d2 = server.save(thing)
                        def saveCb(_):
                            self.stdout.write('Marked "%s" (%s) as done\n' % (
                                thing.title.encode('utf-8'), thing.id[::-1].encode('utf-8')))
                            return 0
                        d2.addCallback(saveCb)
                        return d2
                    else:
                        server.save(thing)
                        self.stdout.write(
                            'Rescheduling for %s "%s" (%s)\n' % (
                                thing.due, thing.title.encode('utf-8'),
                                thing.id[::-1].encode('utf-8')))
        d.addCallback(lookupCb)
        return d


class Edit(tcommand.TwistedCommand):
    summary = "edit a thing"
    usage = "#shortid"

    def doLater(self, args):
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
                self.stdout.write('No thing found for %s\n' %
                    shortid.encode('utf-8'))
                return

            self.getRootCommand()._stdio.teardown()

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
            self.getRootCommand()._stdio.setup()
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
                    thing.title.encode('utf-8'), thing.id[::-1].encode('utf-8')))
            d2.addCallback(saveCb, thing)
            return d2

        d.addCallback(lookupCb)
        return d

class Search(tcommand.TwistedCommand):
    summary = "search for things"
    description = """Search for things.\n""" + SYNTAX

    def addOptions(self):
        self.parser.add_option('-c', '--count',
                          action="store_true", dest="count",
                          help="only show the number of items matching")

    def doLater(self, args):
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
                include_docs=True)

        self.debug('calling view.queryView')
        d = view.queryView()

        def viewCb(result):
            self.debug('viewCb')
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

            return 0
        def viewEb(failure):
            self.debug('viewEb, failure %r' % failure)
            return failure
        d.addCallback(viewCb)
        d.addCallback(viewEb)

        return d

class Show(tcommand.TwistedCommand):
    summary = "show one thing"

    def doLater(self, args):
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
        endkey = shortid + 'Z'

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

from paisley import client
class InputAuthenticator(client.Authenticator, log.Loggable):
    _tries = 0

    def __init__(self, stdio):
        self._stdio = stdio

    def authenticate(self, db):
        """
        @type  db: L{paisley.client.CouchDB}
        """
        self._tries += 1

        if self._tries > 3:
            raise client.AuthenticationError('Failed 3 times to authenticate')

        d = defer.Deferred()
        if not db.username:
            # FIXME: maybe we should prompt?
            db.username = getpass.getuser()

        password = self._stdio.getPassword(
            prompt='Password for %s: ' % db.username)

        # FIXME: use API to set these?
        db.password = password
        # FIXME: provide a mode where it doesn't store these in memory,
        #        but creates a request, gets a token, and then keeps using
        #        the token
        d.addCallback(lambda _: db.getSession())
        def cb(result):
            assert result['ok'] == True, \
                "getSession failed with %r" % result
            self.debug('getSession() succeeded, %r' % result)
            # since we now use a session cookie, we can drop
            # username and password
            # FIXME: but doesn't seem to work against a hoodie db
            #db.username = None
            #db.password = None
            db.useCookies = True
            return result
        d.addCallback(cb)
        def eb(f):
            self.debug('getSession failed: %r', f)
            return f
        d.addErrback(eb)

        d.callback(None)
        return d

class GTD(tcommand.LogReactorCommand):
    # FIXME: this causes doc.py to list commands as being doc.py
    usage = "%prog %command"
    #usage = "gtd %command"
    description = """Get things done.

GTD gives you a tree of subcommands to work with.
You can get help on subcommands by using the -h option to the subcommand.
"""

    subCommandClasses = [Add, conflict.Conflict, Delay, Delete, Done, Edit,
        llist.List,
        project.Project, replicate.Replicate, Search, Show,
        thing.Thing]

    deferred = None # fired when the command interpreter is done

    _server = None # mushin.model.couch.Server
    _newServer = None

    def addOptions(self):
        self.parser.add_option('-H', '--host',
                          action="store", dest="host",
                          default="localhost",
                          help="host to connect to (default: %default)")
        self.parser.add_option('-P', '--port',
                          action="store", dest="port",
                          default="5984",
                          help="port to connect to (default: %default)")
        self.parser.add_option('-D', '--database',
                          action="store", dest="database",
                          default="mushin",
                          help="database to connect to (default: %default)")
        # with an empty default, no password will be prompted if not needed
        self.parser.add_option('-u', '--username',
                          action="store", dest="username",
                          help="username",
                          default="")
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
        self.host = options.host
        self.info("Using host %s", self.host)
        self.port = int(options.port)
        self.info("Using port %d", self.port)
        self.username = options.username
        self.info("Using username %s", self.username)

        self._stdio = manholecmd.Stdio()

    def do(self, args):
        # start a command line interpreter

        class MushinCmdInterpreter(manholecmd.CmdInterpreter, log.Loggable):
            cmdClass = logcommand.command.commandToCmdClass(self)
            cmdClass.prompt = 'GTD> '

        class MushinCmdManhole(manholecmd.CmdManhole, log.Loggable):
            interpreterClass = MushinCmdInterpreter

            def lineReceivedErrback(self, failure):
                failure.trap(command.CommandExited)
                e = failure.value
                ret = e.status
                if ret != 0:
                    self.terminal.write('mushin: error: %s\n' % e.output)

        self.deferred = defer.Deferred()

        self._stdio.setup()
        self._stdio.connect(MushinCmdManhole,
            connectionLostDeferred=self.deferred)

        def alwaysEb(failure):
            self.debug('got failure %r', failure)
            self._stdio.teardown()
            return failure

        # we should expect error.ConnectionDone as a normal exit condition
        def connectionDoneEb(failure):
            failure.trap(error.ConnectionDone)
            self.debug('connection done, ignoring')

        def connectionRefusedEb(failure):
            self.debug('connection closed, %r', failure)
            failure.trap(error.ConnectionRefused)
            self.debug('connection refused')
            self.stderr.write('Could not make a connection to CouchDB.\n')
            return failure

        def eb(failure):
            self.stderr.write('Unhandled failure: %r.\n' % failure)
            return failure

        self.deferred.addCallback(lambda _: self._stdio.teardown())
        self.deferred.addErrback(alwaysEb)
        self.deferred.addErrback(connectionDoneEb)
        self.deferred.addErrback(connectionRefusedEb)
        self.deferred.addErrback(eb)

        return self.deferred

    # FIXME: this is a direct
    def getServer(self):
        """
        @rtype: L{couch.Server}
        """

        # FIXME: should not be importing couchdb
        from couchdb import client
        if self._server:
            return self._server

        try:
            self._server = couch.Server(host=self.host, port=self.port,
                db=self.dbName,
                authenticator=InputAuthenticator(self._stdio),
                username=self.username)
        except client.ResourceNotFound:
            raise command.CommandExited(
                1, "Could not find database %s" % self.db)

        return self._server

    def getNewServer(self):
        """
        @rtype: L{app.Server}
        """
        if self._newServer:
            return self._newServer

        self._newServer = app.Server(host=self.host, port=self.port,
            dbName=self.dbName,
            authenticator=InputAuthenticator(self._stdio),
            username=self.username)

        # FIXME: big hack: replace the .log attribute which just happens
        # to have the same signature
        self._newServer._couch.log = self

        return self._newServer

    def getPassword(self, prompt='Password: '):
        return self._stdio.getPassword(prompt=prompt)

