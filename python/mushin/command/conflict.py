# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

from mushin.common import logcommand
from mushin.command import display

class List(logcommand.LogCommand):
    summary = "List conflicts"

    def do(self, args):
        server = self.getRootCommand().getServer()

        things = list(server.view('conflict', include_docs=True))
        display.Displayer().display_things(things, due=True)

class Conflict(logcommand.LogCommand):
    description = """Manage conflicts.
"""

    subCommandClasses = [List, ]
