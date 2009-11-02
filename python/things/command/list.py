# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import sys
import datetime

from things.common import log, logcommand, parse
from things.model import couch
from things.command import display

class Due(logcommand.LogCommand):
    summary = "list all due open things, ordered by due date."
    description = """
List all due open things, including due today.

Things are ordered by due date, showing the most pressing thing to do at the
bottom.
"""

    def do(self, args):
        server = couch.Server()

        # FIXME: make the view calculate and sort by priority
        now = datetime.datetime.now()
        daystart = datetime.datetime(year=now.year, month=now.month,
            day=now.day)
        things = server.view('open-things-due', descending=True)
        things = [t for t in things if t.due >= daystart]
        display.display_things(things, due=True)

class Open(logcommand.LogCommand):
    summary = "list all open things, ordered by priority (?)."

    def do(self, args):
        server = couch.Server()

        # FIXME: make the view calculate and sort by priority
        display.display_things(server.view('open-things'))

class Overdue(logcommand.LogCommand):
    summary = "list all overdue open things, reverse-ordered by due date."
    description = """
List all overdue open things, including due today.

Things are reverse-ordered by due date, showing the 
bottom.
"""

    def do(self, args):
        server = couch.Server()

        # FIXME: make the view calculate and sort by priority
        now = datetime.datetime.now()
        daystart = datetime.datetime(year=now.year, month=now.month,
            day=now.day)
        dayend = daystart + datetime.timedelta(days=1)
        things = server.view('open-things-due')
        things = [t for t in things if t.due < dayend]
        display.display_things(things, due=True)

class Today(logcommand.LogCommand):
    summary = "list all open things due today"

    def do(self, args):
        server = couch.Server()

        # FIXME: make the view calculate and sort by priority
        now = datetime.datetime.now()
        daystart = datetime.datetime(year=now.year, month=now.month,
            day=now.day)
        dayend = daystart + datetime.timedelta(days=1)
        things = server.view('open-things-due')
        things = [t for t in things if daystart <= t.due < dayend]
        display.display_things(things, due=True)



class List(logcommand.LogCommand):
    # FIXME: this causes doc.py to list commands as being doc.py
    usage = "%prog %command"
    #usage = "gtd %command"
    description = """List things.
"""

    subCommandClasses = [Due, Open, Overdue, Today, ]
