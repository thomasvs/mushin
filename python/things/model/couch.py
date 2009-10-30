# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import datetime

from couchdb import client, schema

class Thing(schema.Document):
    type = schema.TextField()

    description = schema.TextField()

    projects = schema.ListField(schema.TextField())
    contexts = schema.ListField(schema.TextField())

    urgency = schema.IntegerField()
    importance = schema.IntegerField()

    time = schema.IntegerField()

    start = schema.DateTimeField(default=datetime.datetime.now())
    due = schema.DateTimeField()

class Server:
    def __init__(self, uri='http://localhost:5984'):
        server = client.Server(uri)
        self.db = server['gtd']

    def view(self, name):
        # example: open-things
        # include_docs gives us the full docs, so we can recreate Things
        return Thing.view(self.db, 'gtd/%s' % name, include_docs=True)
