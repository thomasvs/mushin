# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import sys
import datetime

from mushin.common import log, logcommand, parse
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
        server = self.getRootCommand().getServer()

        # FIXME: make the view calculate and sort by priority
        now = datetime.datetime.now()
        daystart = datetime.datetime(year=now.year, month=now.month,
            day=now.day)
        things = server.view('open-things-due', include_docs=True,
            descending=True)
        things = [t for t in things if t.due >= daystart]
        display.Displayer().display_things(things, due=True)

class Open(logcommand.LogCommand):
    summary = "list all open things, ordered by priority (?)."

    def do(self, args):
        server = self.getRootCommand().getServer()

        # FIXME: make the view calculate and sort by priority
        display.Displayer().display_things(server.view(
            'open-things', include_docs=True))

class Overdue(logcommand.LogCommand):
    summary = "list all overdue open things, reverse-ordered by due date."
    description = """
List all overdue open things, including due today.

Things are reverse-ordered by due date, showing the 
bottom.
"""

    def do(self, args):
        server = self.getRootCommand().getServer()

        # FIXME: make the view calculate and sort by priority
        now = datetime.datetime.now()
        daystart = datetime.datetime(year=now.year, month=now.month,
            day=now.day)
        dayend = daystart + datetime.timedelta(days=1)
        things = server.view('open-things-due', include_docs=True)
        things = [t for t in things if t.due < dayend]
        display.Displayer().display_things(things, due=True)

class Priority(logcommand.LogCommand):
    summary = "list all open things, ordered by priority."
    aliases = ['pri', ]

    def do(self, args):
        server = self.getRootCommand().getServer()

        view = 'open-things-by-priority'
        kwargs = {'descending': 'true'}
        if args:
            count = int(args[0])
            self.debug('limiting result to %d things' % count)
            kwargs['limit'] = count
        result = server.view(view, include_docs=True, **kwargs)

        display.Displayer().display_things(result)


class Today(logcommand.LogCommand):
    summary = "list all open things due today"

    def do(self, args):
        server = self.getRootCommand().getServer()

        # FIXME: make the view calculate and sort by priority
        now = datetime.datetime.now()
        daystart = datetime.datetime(year=now.year, month=now.month,
            day=now.day)
        dayend = daystart + datetime.timedelta(days=1)
        things = server.view('open-things-due', include_docs=True)
        things = [t for t in things if daystart <= t.due < dayend]
        display.Displayer().display_things(things, due=True)



class List(logcommand.LogCommand):
    # FIXME: this causes doc.py to list commands as being doc.py
    usage = "%prog %command"
    #usage = "gtd %command"
    description = """List things.
"""
    aliases = ['l', ]

    subCommandClasses = [Due, Open, Overdue, Priority, Today, ]
