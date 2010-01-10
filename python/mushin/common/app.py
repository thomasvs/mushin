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

class Project(object):
    name = None
    things = None

    def fromDict(self, d):
        # key, value, id
        self.name = d['key']
        self.things = d['value']

class Server:
    def __init__(self):
        self._couch = couchdb.CouchDB('localhost')

    def _getThingsByDue(self, which, factory, limit=None, include_docs=True):
        """
        Returns: a deferred for a generator that generates the things.

        @param which:   one of 'due', 'today', 'overdue'
        @type  which:   str
        @param limit:   if specified,
                        the number of days to limit due or overdue to
        @param factory: an object factory method (for example, constructor)
        """
        now = datetime.datetime.now()
        daystart = datetime.datetime(year=now.year, month=now.month,
            day=now.day)
        dayend = daystart + datetime.timedelta(days=1)

        args = 'include_docs=%s' % (
            include_docs and 'true' or 'false')
        
        # FIXME: due dates, and hence keys, can possibly end with Z
        startkey = endkey = None

        if which == 'today':
            startkey = daystart.strftime('%Y-%m-%dT%H:%M:%S')
            endkey = dayend.strftime('%Y-%m-%dT%H:%M:%S')
        elif which == 'due':
            startkey = daystart.strftime('%Y-%m-%dT%H:%M:%S')
            if limit:
                end = daystart + datetime.timedelta(days=limit)
                endkey = end.strftime('%Y-%m-%dT%H:%M:%S')
        elif which == 'overdue':
            endkey = dayend.strftime('%Y-%m-%dT%H:%M:%S')
            if limit:
                start = dayend - datetime.timedelta(days=limit)
                startkey = start.strftime('%Y-%m-%dT%H:%M:%S')
        
        if startkey:
            args += '&startkey="%s"' % startkey
        if endkey:
            args += '&endkey="%s"' % endkey

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

    def getThingsDue(self, limit=None):
        """
        @returns: a deferred for a generator that generates
                  uncompleted due (up to end of today) things
        @rtype:   L{defer.Deferred} of generator
        """
        d = self._getThingsByDue('due', couch.Thing, limit=limit)
        return d

    def getThingsDueCount(self, limit=None):
        """
        @returns: a deferred for a count of
                  uncompleted due (up to end of today) things
        @rtype:   L{defer.Deferred} of int
        """
        d = self._getThingsByDue('due', Count, limit=limit, include_docs=False)
        d.addCallback(lambda r: len(list(r)))
        return d


    def getThingsOverdue(self, limit=None):
        """
        @returns: a deferred for a generator that generates
                  uncompleted overdue (since start of today) things
        @rtype:   L{defer.Deferred} of generator
        """
        d = self._getThingsByDue('overdue', couch.Thing, limit=limit)
        return d

    def getThingsOverdueCount(self, limit=None):
        """
        @returns: a deferred for a count of
                  uncompleted overdue (since start of today) things
        @rtype:   L{defer.Deferred} of int
        """
        d = self._getThingsByDue('overdue', Count, limit=limit,
            include_docs=False)
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

    def _getThingsByStatus(self, status, factory, include_docs=True):
        """
        Returns: a deferred for a generator that generates the things.

        @param status: one of 'waitingfor', 'nextaction'
        """
        args = 'include_docs=%s' % (
            include_docs and 'true' or 'false')
        
        view = views.View(self._couch, 'mushin', 'mushin',
            'by-status?%s&startkey="%s"&endkey="%s"' % (args, status, status),
            factory)

        d = view.queryView()
        return d

    def getThingsNextAction(self):
        """
        @returns: a deferred for a generator that generates
                  things to do next
        @rtype:   L{defer.Deferred} of generator
        """
        d = self._getThingsByStatus('next', couch.Thing)
        return d

    def getThingsNextActionCount(self):
        """
        @returns: a deferred for a count of
                  things to do next
        @rtype:   L{defer.Deferred} of int
        """
        d = self._getThingsByStatus('next', Count, include_docs=False)
        d.addCallback(lambda r: len(list(r)))
        return d

    def getThingsWaitingFor(self):
        """
        @returns: a deferred for a generator that generates
                  things being waited for
        @rtype:   L{defer.Deferred} of generator
        """
        d = self._getThingsByStatus('waitingfor', couch.Thing)
        return d

    def getThingsWaitingForCount(self):
        """
        @returns: a deferred for a count of
                  things being waited for
        @rtype:   L{defer.Deferred} of int
        """
        d = self._getThingsByStatus('waitingfor', Count, include_docs=False)
        d.addCallback(lambda r: len(list(r)))
        return d

    def getContexts(self):
        """
        @returns: a deferred for a generator that generates
                  contexts
        @rtype:   L{defer.Deferred} of generator
        """
        view = views.View(self._couch, 'mushin', 'mushin',
            'contexts?group=true', Project)

        d = view.queryView()
        return d

    def getProjects(self):
        """
        @returns: a deferred for a generator that generates
                  projects
        @rtype:   L{defer.Deferred} of generator
        """
        view = views.View(self._couch, 'mushin', 'mushin',
            'projects?group=true', Project)

        d = view.queryView()
        return d

    def getThingsByContext(self, context):
        view = views.View(self._couch, 'mushin', 'mushin',
            'by-context?startkey="%s"&endkey="%s"&include_docs=true' % (
                context, context), couch.Thing)
        d = view.queryView()
        return d


