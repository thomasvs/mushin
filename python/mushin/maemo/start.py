# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import gtk
import hildon


from twisted.internet import defer

from mushin.common import app

from mushin.maemo import new, things, lists, show

class StartWindow(hildon.StackableWindow):
    def __init__(self):
        hildon.StackableWindow.__init__(self)

        self._server = app.Server()

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
        button.connect('clicked', self._lists_clicked_cb)

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
        server = app.Server()
        d = server.getThings()
        return d


    def _lists_clicked_cb(self, button):
        w = lists.ListsWindow()
        hildon.hildon_gtk_window_set_progress_indicator(w, 1)

        d = defer.Deferred()

        # an array because we want this order
        methods = [
            ('Today', self._server.getThingsTodayCount, {}),
            ('Due this week', self._server.getThingsDueCount, {'limit' :7}),
            ('Overdue', self._server.getThingsOverdueCount, {}),
            ('Due', self._server.getThingsDueCount, {}),
            ('Waiting for', self._server.getThingsWaitingForCount, {}),
            ('Next action', self._server.getThingsNextActionCount, {}),
        ]

        for name, method, kwargs in methods:
            d.addCallback(lambda _, m, kw: m(**kw), method, kwargs)
            def _cb(result):
                w.add_list(name, result)
            d.addCallback(lambda result, n: w.add_list(n, result), name)

        d.addCallback(lambda _:
            hildon.hildon_gtk_window_set_progress_indicator(w, 0))

        d.callback(None)

        w.connect('selected', self._lists_selected_cb)
        w.show_all()

    def _lists_selected_cb(self, lw, list_name):
        methods = {
            'Today': (self._server.getThingsToday, {}),
            'Due this week': (self._server.getThingsDue, {'limit': 7}),
            'Due': (self._server.getThingsDue, {}),
            'Overdue': (self._server.getThingsOverdue, {}),
            'Waiting for': (self._server.getThingsWaitingFor, {}),
            'Next action': (self._server.getThingsNextAction, {}),
        }
        if list_name in methods.keys():
            w = things.ThingsWindow()
            hildon.hildon_gtk_window_set_progress_indicator(w, 1)

            method, kwargs = methods[list_name]
            d = method(**kwargs)
            def _cb(result):
                for thing in result:
                    w.add_thing(thing)
                hildon.hildon_gtk_window_set_progress_indicator(w, 0)
            d.addCallback(_cb)

            w.connect('selected', self._thing_selected_cb)
            w.show_all()

    def _thing_selected_cb(self, tw, thing):
            w = show.ShowWindow(thing)
            w.show_all()

    def _new_clicked_cb(self, button):
        w = new.NewWindow()

        hildon.hildon_gtk_window_set_progress_indicator(w, 1)

        d = defer.Deferred()

        d.addCallback(lambda _: self._server.getProjects())
        def _cb(result):
            w.add_projects([p.name for p in list(result)])
        d.addCallback(_cb)

        d.addCallback(lambda _: self._server.getContexts())
        def _cb(result):
            w.add_contexts([p.name for p in list(result)])
        d.addCallback(_cb)

        d.addCallback(lambda _:
            hildon.hildon_gtk_window_set_progress_indicator(w, 0))

        d.addCallback(lambda _: w.show_all())
        d.callback(None)
