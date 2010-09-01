# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import datetime

from mushin.extern.paisley import couchdb, views

from mushin.common import log
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

class Server(log.Loggable):
    """
    Abstracts communication with the couchdb server.

    The get methods can return failure objects; for example
    twisted.web.error.Error: 404 Object Not Found
    twisted.internet.error.ConnectionRefusedError
    """

    logCategory = 'server'

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
        self.debug('getThingsByDue: view %r' % view)

        d = view.queryView()
        return d


    def getThings(self):
        view = views.View(self._couch, 'mushin', 'mushin',
            'open-things-due?include_docs=true', couch.Thing)
        self.debug('getThings: view %r' % view)

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
        self.debug('getThingsByStatus: view %r' % view)

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
        self.debug('getContexts: view %r' % view)

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
        self.debug('getProjects: view %r' % view)

        d = view.queryView()
        return d

    def _getThingsByContext(self, context, factory, include_docs=True):
        """
        Returns: a deferred for a generator that generates the things.

        @param context: the context
        """
        args = 'include_docs=%s' % (
            include_docs and 'true' or 'false')
        
        view = views.View(self._couch, 'mushin', 'mushin',
            'by-context?%s&startkey="%s"&endkey="%s"' % (
                args, context, context),
            factory)
        self.debug('getThingsByContext: view %r' % view)

        d = view.queryView()
        return d


    def getThingsByContext(self, context):
        return self._getThingsByContext(context, couch.Thing)

    def getThingsByContextCount(self, context):
        """
        @returns: a deferred for a count of
                  things in the given context
        @rtype:   L{defer.Deferred} of int
        """
        d = self._getThingsByContext(context, Count, include_docs=False)
        d.addCallback(lambda r: len(list(r)))
        return d

    def save(self, thing):
        return self.add(thing)

    def add(self, thing):
        """
        @type  thing: L{couch.Thing}
        """
        self.debug('adding thing %r', thing)
        d = self._couch.saveDoc('mushin', thing._data)
        def _saveDoc_cb(result):
            self.debug('add result %r', result)
        d.addCallback(_saveDoc_cb)
        def _saveDoc_eb(failure):
            self.debug('failure adding thing %r: %r',
                thing, log.getFailureMessage(failure))
            return failure
        d.addErrback(_saveDoc_eb)

        return d
