# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import datetime
import math

from mushin.common import mapping, log

class Thing(mapping.Document, log.Loggable):
    type = mapping.TextField(default='thing')

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

    time = mapping.IntegerField()     # duration, in seconds
    complete = mapping.IntegerField() # percentage of completion, 0 to 100 ?

    # tasks should always have a start date set when created
    # however, setting a default here makes it use that default in those
    # cases where it (wrongly) doesn't have one as soon as you access it
    # with .start
    # We choose to not set a default
    # start = mapping.DateTimeField(default=datetime.datetime.now)
    start = mapping.DateTimeField()
    due = mapping.DateTimeField() # e.g. 2009-02-20T00:00:00
    end = mapping.DateTimeField()
    updated = mapping.DateTimeField() # when it was last updated
    recurrence = mapping.IntegerField() # in seconds

    def shortid(self):
        # last 6 chars reversed
        return self.id[:-7:-1]

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

    def finish(self):
        """
        Complete a thing.
        If the thing has recurrence, reschedule.

        return: True if it really is completed, False if rescheduled.
        """
        if self.recurrence:
            self.debug('done recurring thing, rescheduling')
            self.complete = None
            if not self.due:
                self.due = datetime.datetime.now()

            self.start = self.due
            self.due = self.start + \
                datetime.timedelta(seconds=self.recurrence)
            return False
        else:
            self.debug('done non-recurring thing')
            self.complete = 100
            self.end = datetime.datetime.now()
            return True

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
    def __init__(self, uri='http://localhost:5984', db='mushin'):
        from couchdb import client
        server = client.Server(uri)
        self.db = server[db]

        from mushin.extern.paisley import client
        # FIXME: get host/port
        self._db = client.CouchDB('localhost', 5984)
        self._dbName = db

    def view(self, name, **kwargs):
        # example: open-things
        # include_docs gives us the full docs, so we can recreate Things
        return Thing.view(self.db, 'mushin/%s' % name, **kwargs)

    def load(self, thingid):
        return Thing.load(self.db, thingid)

    def save(self, thing):
        thing.updated = datetime.datetime.now()
        # FIXME: get a real accessor
        return self._db.saveDoc(self._dbName, thing._data)

    def delete(self, thing):
        return self._db.deleteDoc(self._dbName, thing.id, thing.rev)

def thing_from_dict(d):
    """
    Load object from a given dict, yagtd style.
    """
    if not d['title']:
        raise ValueError('No title given.')

    thing = Thing()
    # now set by default
    # thing.type = 'thing'

    thing.set_from_dict(d)

    return thing
