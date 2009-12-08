# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import sys
import datetime

from mushin.common import log, logcommand, parse
from mushin.model import couch
from mushin.command import display

class Due(logcommand.LogCommand):
    summary = "change due date"

    def do(self, args):
        shortid = args[0]
        # I often type it as D:YYYY-MM-DD ...
        if args[1].startswith('D:'):
            args[1] = args[1][2:]
        date = parse.parse_date(args[1])
        server = couch.Server()

        thing = display.lookup(server, args[0])
        if thing:
            thing.due = date
            server.save(thing)
            print 'Changed due date to %s on "%s" (%s)' % (
                thing.due, thing.title, thing.id)



class Thing(logcommand.LogCommand):
    description = """Manipulate things.
"""
    # this one is so common we use one character
    aliases = ["t", ]

    subCommandClasses = [Due, ]
