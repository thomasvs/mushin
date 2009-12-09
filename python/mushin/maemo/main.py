# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import gtk
import hildon

from mushin.maemo import new, things

class Server:
    def __init__(self):
        from mushin.extern.paisley import couchdb, views
        self._couch = couchdb.CouchDB('localhost')

    def getThings(self):
        from mushin.extern.paisley import couchdb, views
        from mushin.model import couch
        view = views.View(self._couch, 'mushin', 'mushin',
            'open-things-due?include_docs=true', couch.Thing)
        d = view.queryView()
        return d


class MainWindow(hildon.StackableWindow):
    def __init__(self):
        hildon.StackableWindow.__init__(self)

        self._vbox = gtk.VBox()
        #self._vbox.props.width_request = 1

        self.add(self._vbox)
        self.show_all()

        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # align left
        #button.set_alignment(0.0, 0.5, 1.0, 0.0)
        
        image = gtk.image_new_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_BUTTON)
        button.set_image(image)

        button.set_title('List')

        self._vbox.pack_start(button, False, False, 0)
        button.show()
        button.connect('clicked', self._list_clicked_cb)

        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # align left
        #button.set_alignment(0.0, 0.5, 1.0, 0.0)
        
        image = gtk.image_new_from_stock(gtk.STOCK_NEW, gtk.ICON_SIZE_BUTTON)
        button.set_image(image)

        button.set_title('New thing')

        self._vbox.pack_start(button, False, False, 0)
        button.show()
        button.connect('clicked', self._new_clicked_cb)

    def _get_data(self):
        server = Server()
        d = server.getThings()
        return d


    def _list_clicked_cb(self, button):
        print 'button clicked'
        w = things.ThingsWindow()
        hildon.hildon_gtk_window_set_progress_indicator(w, 1)
        d = self._get_data()

        def _get_dataCb(result):
            for thing in result:
                w.add_thing(thing)
            hildon.hildon_gtk_window_set_progress_indicator(w, 0)
        d.addCallback(_get_dataCb)

        w.show_all()


    def _new_clicked_cb(self, button):
        print 'button clicked'
        w = new.NewWindow()

        w.show_all()


def start():
    gtk.set_application_name('mushin')

    window = MainWindow()
    window.connect('destroy', lambda _: gtk.main_quit())

def main(argv):
    from twisted.internet import gtk2reactor
    gtk2reactor.install()
    from twisted.internet import reactor

    reactor.callWhenRunning(start)

    reactor.run()
