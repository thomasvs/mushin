# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# no further imports here, since we don't want to import a reactor just yet
import gtk

def start():
    gtk.set_application_name('mushin')

    from mushin.maemo import start
    window = start.StartWindow()
    window.connect('destroy', lambda _: gtk.main_quit())

def main(argv):
    from twisted.internet import gtk2reactor
    gtk2reactor.install()
    from twisted.internet import reactor

    reactor.callWhenRunning(start)

    reactor.run()
