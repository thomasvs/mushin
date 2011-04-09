# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import sys
import datetime

from mushin.common import log, logcommand, parse, app
from mushin.model import couch
from mushin.command import display

class Due(logcommand.LogCommand):
    summary = "list all due open things, ordered by due date."
    description = """
List all due open things, including due today.

Things are ordered by due date, showing the most pressing thing to do at the
bottom.
"""

    def do(self, args):
        server = self.getRootCommand().getNewServer()
        
        d = server.getThingsDue()
        def viewCb(things):
            things = list(things)
            things.reverse()
            display.Displayer(self.stdout).display_things(things, due=True)
        d.addCallback(viewCb)
        return d

class Open(logcommand.LogCommand):
    summary = "list all open things, ordered by priority (?)."

    def do(self, args):
        server = self.getRootCommand().getServer()

        # FIXME: make the view calculate and sort by priority
        d = server.view('open-things', include_docs=True)
        d.addCallback(lambda things:
            display.Displayer(self.stdout).display_things(things))
        return d

class Overdue(logcommand.LogCommand):
    summary = "list all overdue open things, reverse-ordered by due date."
    description = """
List all overdue open things, including due today.

Things are reverse-ordered by due date, showing the least overdue item at the
bottom.
"""
    def do(self, args):
        server = self.getRootCommand().getNewServer()
        
        d = server.getThingsOverdue()
        def viewCb(things):
            display.Displayer(self.stdout).display_things(things, due=True)
        d.addCallback(viewCb)
        return d

class Priority(logcommand.LogCommand):
    summary = "list all open things, ordered by priority."
    aliases = ['pri', ]

    def do(self, args):
        server = self.getRootCommand().getServer()

        view = 'open-things-by-priority'
        kwargs = {'descending': True}
        if args:
            count = int(args[0])
            self.debug('limiting result to %d things' % count)
            kwargs['limit'] = count
        d = server.view(view, include_docs=True, **kwargs)
        d.addCallback(lambda result: display.Displayer(
            self.stdout).display_things(result))
        return d


class Today(logcommand.LogCommand):
    summary = "list all open things due today"

    def do(self, args):
        server = self.getRootCommand().getNewServer()
        
        d = server.getThingsToday()
        def viewCb(things):
            display.Displayer(self.stdout).display_things(things, due=True)
        d.addCallback(viewCb)
        return d

class List(logcommand.LogCommand):
    # FIXME: this causes doc.py to list commands as being doc.py
    usage = "%prog %command"
    #usage = "gtd %command"
    description = """List things.
"""
    aliases = ['l', ]

    subCommandClasses = [Due, Open, Overdue, Priority, Today, ]
