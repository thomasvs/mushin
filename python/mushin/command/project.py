# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import sys
import datetime

from mushin.common import log, logcommand, parse
from mushin.model import couch
from mushin.command import display

class List(logcommand.LogCommand):
    summary = "list all open projects"

    def do(self, args):
        server = couch.Server()
        displayer = display.Displayer()

        projects = server.db.view('mushin/open-projects-by-priority',
            group=True)
        orderable = []
        for project in projects:
            completed, total, priority, docid = project.value
            if completed != total:
                doc = server.load(docid)
                orderable.append((priority, (float(completed) / total), 
                    # FIXME: the %-30s includes the ansi codes
                    "%s %s (%2d %%) %s %s\n" % (
                    # FIXME: hardcode cut off point
                    displayer.shortid(docid[:6]),
                    displayer.priority("(%.2f)" % priority, priority),
                    int(completed * 100.0 / total),
                    displayer.project(project.key),
                    doc.title,
                )))

        orderable.sort()
        orderable.reverse()

        if args:
            count = int(args[0])
            self.debug('limiting to %d projects' % count)
            orderable = orderable[:count]

        for p, c, line in orderable:
            self.stdout.write(line)

class Project(logcommand.LogCommand):
    summary = "manipulate projects"

    subCommandClasses = [List, ]
