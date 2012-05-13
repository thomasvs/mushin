# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# no further imports here, since we don't want to import a reactor just yet
import gtk

def start():
    from mushin.common import log
    log.debug('main', 'starting')
    gtk.set_application_name('mushin')

    from mushin.maemo import start
    log.debug('main', 'creating window')
    window = start.StartWindow()
    log.debug('main', 'created window %r', window)
    window.connect('destroy', lambda _: gtk.main_quit())

def main(argv):
    from mushin.common import log
    log.init()
    log.debug('maemo', 'main')

    from twisted.internet import gtk2reactor
    gtk2reactor.install()
    from twisted.internet import reactor

    # set paisley to non-strict since we only have simplejson on maemo
    from mushin.extern.paisley import pjson

    assert not pjson.STRICT

    log.logTwisted()

    reactor.callWhenRunning(start)

    reactor.run()
