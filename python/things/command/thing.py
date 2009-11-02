# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import sys
import datetime

from things.common import log, logcommand, parse
from things.model import couch
from things.command import display

class Due(logcommand.LogCommand):
    summary = "change due date"

    def do(self, args):
        shortid = args[0]
        date = parse.parse_date(args[1])
        server = couch.Server()

        print 'Change due date to', date
        thing = display.lookup(server, args[0])
        if thing:
            thing.due = date
            server.save(thing)
            print 'Changed thing "%s" (%s)' % (thing.title, thing.id)



class Thing(logcommand.LogCommand):
    description = """Manipulate things.
"""
    # this one is so common we use one character
    aliases = ["t", ]

    subCommandClasses = [Due, ]
