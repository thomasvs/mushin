# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import datetime
import sys

import couch

from twisted.internet import reactor, defer

from paisley import couchdb, views

# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import couch

import gtk
import hildon

from twisted.internet import gtk2reactor
gtk2reactor.install()

from twisted.internet import reactor, defer


from paisley import couchdb, views

class Application:
    def setup(self):
        gtk.set_application_name('mushin')
        self._window = hildon.StackableWindow()
        self._panarea = hildon.PannableArea()

        self._vbox = gtk.VBox()
        self._vbox.props.width_request = 1


        self._panarea.add_with_viewport(self._vbox)
        self._window.add(self._panarea)
        self._window.show_all()

        print 'setup'

    def add_thing(self, thing):
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        button.set_alignment(0.0, 0.5, 1.0, 0.0)
        self._vbox.pack_start(button)
        button.set_title(thing.title)
        value = []
        if thing.projects:
            value.append('projects: %s' % ', '.join(thing.projects))
        if thing.contexts:
            value.append('contexts: %s' % ', '.join(thing.contexts))
        button.set_value(" - ".join(value))

        button.show()

def test():
    foo = couchdb.CouchDB('localhost', username='thomas', password='pass')

    v = views.View(foo, "mushin", "mushin", 'open-things-due?include_docs=true', couch.Thing)
    d = v.queryView()
    wfd = defer.waitForDeferred(d)
    yield wfd
    things = list(wfd.getResult())

    for thing in things:
        print thing.start, thing.title

    #print "all things", list(things)

    print 'iterate'

    #for thing in things:
    #    print thing

    yield things
test = defer.deferredGenerator(test)

def main():
    app = Application()
    app.setup()
    d = test()
    def testCb(things):
        print 'test'
        for t in things:
            print 'adding thing', t
            app.add_thing(t)

    d.addCallback(testCb)
    return d

    
if __name__ == "__main__":
    reactor.callWhenRunning(main)
    reactor.run()

