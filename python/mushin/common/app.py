# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

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

    def getThings(self):
        view = views.View(self._couch, 'mushin', 'mushin',
            'open-things-due?include_docs=true', couch.Thing)
        d = view.queryView()
        return d

    def getThingsDue(self):
        """
        Returns: a generator that generates the due things.
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
