# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# no further imports here, since we don't want to import a reactor just yet
import gtk

def start():
    gtk.set_application_name('mushin')

    from mushin.maemo import start
    window = start.StartWindow()
    window.connect('destroy', lambda _: gtk.main_quit())

    import hildon
    menu = hildon.AppMenu()

    button = hildon.GtkButton(gtk.HILDON_SIZE_AUTO)
    button.set_label("New")
    menu.append(button)

    menu.show_all()

def main(argv):
    from mushin.common import log
    log.init()
    log.debug('maemo', 'main')

    from twisted.internet import gtk2reactor
    gtk2reactor.install()
    from twisted.internet import reactor

    log.logTwisted()

    reactor.callWhenRunning(start)

    reactor.run()
