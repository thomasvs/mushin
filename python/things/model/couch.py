# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import datetime
import math

from couchdb import client, schema

class Thing(schema.Document):
    type = schema.TextField()

    title = schema.TextField()
    description = schema.TextField()

    # attributes from Getting Things Done, David Allen
    projects = schema.ListField(schema.TextField())
    contexts = schema.ListField(schema.TextField())
    statuses = schema.ListField(schema.TextField())
    references = schema.ListField(schema.TextField())

    # attributes from Seven Habits of Highly Effective People, Stephen Covey
    urgency = schema.IntegerField()
    importance = schema.IntegerField()

    time = schema.IntegerField()     # in seconds
    complete = schema.IntegerField() # percentage of completion

    start = schema.DateTimeField(default=datetime.datetime.now())
    due = schema.DateTimeField()
    end = schema.DateTimeField()
    recurrence = schema.IntegerField() # in seconds

    # lifted from yagtd.py
    def _needed_hours(self):
        """Compute (needed) time in hours."""

        # FIXME: what if the delta has days ?
        # well, it's not a delta anymore is it?
        T = self.time / 60. / 60.

        #if __debug__: print "Time=", T
        return T

    def _effort(self):
        """Determine effort needed."""

        h = self._needed_hours()
        if h:
            E = max(1, math.log(h)/math.log(3)+1.0)
        else:
            E = 0

        #if __debug__: print "Effort=", E
        return E

    def _schedule_pressure(self):
        """Determine pressure from due date."""

        now = datetime.datetime.today()  # now

        if self.due:
            # Compute delta from now and target date (- needed time)
            delta = (self.due - now) - datetime.timedelta(self.time)
            #print "delta=", delta

            if delta < datetime.timedelta(0):  # overdue
                P = 6
            elif delta < datetime.timedelta(1):  # 1 day
                P = 5
            elif delta < datetime.timedelta(7):  # 1 week
                P = 4
            elif delta < datetime.timedelta(30):  # 1 month
                P = 3
            elif delta < datetime.timedelta(90):  # 3 months
                P = 2
            else:  # > 3 months
                P = 1

        else:  # == urgency
            P = self.urgency

        #if __debug__: print "Pressure=", P
        return P

    def priority(self):
        """Compute priority."""

        I = self.importance

        P = min(self.urgency+2, self._schedule_pressure())
        U = max(self.urgency, P)

        E = self._effort()

        Prio = math.sqrt(2*U*U+2*I*I+E*E)/math.sqrt(5)

        #if __debug__: print "Piority=", Prio
        return Prio

class Server:
    def __init__(self, uri='http://localhost:5984'):
        server = client.Server(uri)
        self.db = server['gtd']

    def view(self, name, **kwargs):
        # example: open-things
        # include_docs gives us the full docs, so we can recreate Things
        return Thing.view(self.db, 'gtd/%s' % name, include_docs=True, **kwargs)