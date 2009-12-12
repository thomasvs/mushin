# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import datetime
import math

from mushin.common import mapping

class Thing(mapping.Document):
    type = mapping.TextField()

    title = mapping.TextField()
    description = mapping.TextField()

    # attributes from Getting Things Done, David Allen
    projects = mapping.ListField(mapping.TextField())
    contexts = mapping.ListField(mapping.TextField())
    statuses = mapping.ListField(mapping.TextField())
    references = mapping.ListField(mapping.TextField())

    # attributes from Seven Habits of Highly Effective People, Stephen Covey
    urgency = mapping.IntegerField()
    importance = mapping.IntegerField()

    time = mapping.IntegerField()     # in seconds
    complete = mapping.IntegerField() # percentage of completion

    start = mapping.DateTimeField(default=datetime.datetime.now())
    due = mapping.DateTimeField()
    end = mapping.DateTimeField()
    recurrence = mapping.IntegerField() # in seconds

    def shortid(self):
        return self.id[:6]

    # lifted from yagtd.py
    def _needed_hours(self):
        """Compute (needed) time in hours."""

        # FIXME: what if the delta has days ?
        # well, it's not a delta anymore is it?
        T = (self.time or 0) / 60. / 60.

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
            delta = (self.due - now) - datetime.timedelta(self.time or 0)
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
            P = self.urgency or 0

        #if __debug__: print "Pressure=", P
        return P

    def priority(self):
        """Compute priority."""

        I = self.importance or 0

        P = min((self.urgency or 0) + 2, self._schedule_pressure())
        U = max(self.urgency or 0, P)

        E = self._effort()

        Prio = math.sqrt(2*U*U + 2*I*I + E*E) / math.sqrt(5)

        #if __debug__: print "Piority=", Prio
        return Prio

    def set_from_dict(self, d):
        """
        Set my attributes from the given dict.
        """
        for attr in [
            'title',
            'contexts', 'projects', 'statuses', 'references',
            'urgency', 'importance',
            'complete',
            'time', 'recurrence',
            'start', 'due', 'end'
        ]:
            setattr(self, attr, d.get(attr, None))

    # method for paisley View objectFactory
    def fromDict(self, d):
        # a dict from Paisley
        # FIXME: this is poking at internals of python-couchdb
        # FIXME: do we need copy ?
        self._data = d['doc'].copy()
        return

class Server:
    def __init__(self, uri='http://localhost:5984'):
        from couchdb import client
        server = client.Server(uri)
        self.db = server['mushin']

    def view(self, name, **kwargs):
        # example: open-things
        # include_docs gives us the full docs, so we can recreate Things
        return Thing.view(self.db, 'mushin/%s' % name, **kwargs)

    def load(self, thingid):
        return Thing.load(self.db, thingid)

    def save(self, thing):
        return thing.store(self.db)    

    def delete(self, thing):
        return self.db.delete(thing)

def thing_from_dict(d):
    """
    Load object from a given dict, yagtd style.
    """
    if not d['title']:
        raise ValueError('No title given.')

    thing = Thing()
    thing.type = 'thing'

    thing.set_from_dict(d)

    return thing
