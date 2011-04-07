# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import sys
import datetime

from mushin.common import log, logcommand, parse
from mushin.model import couch
from mushin.command import display

from twisted.internet import defer

class List(logcommand.LogCommand):
    summary = "list all open projects"

    def do(self, args):
        server = self.getRootCommand().getServer()
        displayer = display.Displayer(self.stdout)

        projects = server.db.view('mushin/open-projects-by-priority',
            group=True)

        orderable = []

        d = defer.Deferred()

        for project in projects:
            completed, total, priority, docid = project.value
            if completed != total:
                if not docid:
                    self.stderr.write(
                        'ERROR: project %r does not have a doc\n' % project)
                    continue

                d.addCallback(lambda _, did: server.load(did), docid)

                def loadCb(thing, orderable, proj):
                    assert thing.id
                    completed, total, priority, docid = proj.value
                    orderable.append((priority, (float(completed) / total), 
                        # FIXME: the %-30s includes the ansi codes
                        "%s %s (%2d %%) %s %s\n" % (
                        displayer.shortid(thing.shortid()),
                        displayer.priority("(%.2f)" % priority, priority),
                        int(completed * 100.0 / total),
                        displayer.project(proj.key),
                        thing.title,
                    )))
                d.addCallback(loadCb, orderable, project)

        def loopedCb(_, orderable, args):
            orderable.sort()
            orderable.reverse()

            if args:
                count = int(args[0])
                self.debug('limiting to %d projects' % count)
                orderable = orderable[:count]

            for p, c, line in orderable:
                self.stdout.write(line)
        d.addCallback(loopedCb, orderable, args)

        d.callback(None)
        return d

class Project(logcommand.LogCommand):
    summary = "manipulate projects"

    subCommandClasses = [List, ]
