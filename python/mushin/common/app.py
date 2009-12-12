# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import datetime

from mushin.extern.paisley import couchdb, views

from mushin.model import couch

"""
Main application class to interface with CouchDB.
"""

class Count(object):
    def fromDict(self, d):
        # key, value, id
        pass

class Server:
    def __init__(self):
        self._couch = couchdb.CouchDB('localhost')

    def _getThingsByDue(self, which, factory, include_docs=True):
        """
        Returns: a deferred for a generator that generates the things.

        @param which: one of 'due', 'today', 'overdue'
        """
        now = datetime.datetime.now()
        daystart = datetime.datetime(year=now.year, month=now.month,
            day=now.day)
        dayend = daystart + datetime.timedelta(days=1)

        args = 'include_docs=%s' % (
            include_docs and 'true' or 'false')
        
        # FIXME: due dates, and hence keys, can possibly end with Z
        if which in ['today', 'due']:
            args += '&startkey="%s"' % \
                daystart.strftime('%Y-%m-%dT%H:%M:%S')
        if which in ['today', 'overdue']:
            args += '&endkey="%s"' % \
                dayend.strftime('%Y-%m-%dT%H:%M:%S')

        view = views.View(self._couch, 'mushin', 'mushin',
            'open-things-due?%s' % args,
            factory)

        d = view.queryView()
        return d


    def getThings(self):
        view = views.View(self._couch, 'mushin', 'mushin',
            'open-things-due?include_docs=true', couch.Thing)
        d = view.queryView()
        return d

    def getThingsDue(self):
        """
        Returns: a deferred for a generator that generates the due things.
        """
        view = views.View(self._couch, 'mushin', 'mushin',
            'open-things-due?include_docs=true', couch.Thing)
        d = view.queryView()
        return d

    def getThingsDueCount(self):
        """
        Returns: a deferred that will fire the number of due items.
        """
        # FIXME: there has to be a better way
        view = views.View(self._couch, 'mushin', 'mushin',
            'open-things-due', Count)
        d = view.queryView()
        d.addCallback(lambda r: len(list(r)))
        return d

    def getThingsDue(self):
        """
        @returns: a deferred for a generator that generates
                  uncompleted due (up to end of today) things
        @rtype:   L{defer.Deferred} of generator
        """
        d = self._getThingsByDue('due', couch.Thing)
        return d

    def getThingsDueCount(self):
        """
        @returns: a deferred for a count of
                  uncompleted due (up to end of today) things
        @rtype:   L{defer.Deferred} of int
        """
        d = self._getThingsByDue('due', Count, include_docs=False)
        d.addCallback(lambda r: len(list(r)))
        return d


    def getThingsOverdue(self):
        """
        @returns: a deferred for a generator that generates
                  uncompleted overdue (since start of today) things
        @rtype:   L{defer.Deferred} of generator
        """
        d = self._getThingsByDue('overdue', couch.Thing)
        return d

    def getThingsOverdueCount(self):
        """
        @returns: a deferred for a count of
                  uncompleted overdue (since start of today) things
        @rtype:   L{defer.Deferred} of int
        """
        d = self._getThingsByDue('overdue', Count, include_docs=False)
        d.addCallback(lambda r: len(list(r)))
        return d

    def getThingsToday(self):
        """
        @returns: a deferred for a generator that generates
                  uncompleted things due today
        @rtype:   L{defer.Deferred} of generator
        """
        d = self._getThingsByDue('today', couch.Thing)
        return d

    def getThingsTodayCount(self):
        """
        @returns: a deferred for a count of
                  uncompleted things due today
        @rtype:   L{defer.Deferred} of int
        """
        d = self._getThingsByDue('today', Count, include_docs=False)
        d.addCallback(lambda r: len(list(r)))
        return d

