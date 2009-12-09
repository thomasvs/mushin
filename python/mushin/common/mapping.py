# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

try:
    from mushin.extern.paisley.mapping import *
except ImportError, e:
    from couchdb.schema import *
