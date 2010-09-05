# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import datetime
import gtk
import hildon


from twisted.internet import defer

from mushin.common import app, log
from mushin.model import couch

from mushin.maemo import new, things, lists, show, error

class StartWindow(hildon.StackableWindow, log.Loggable):

    logCategory = 'startwindow'

    def __init__(self):
        hildon.StackableWindow.__init__(self)

        self._server = app.Server()

        self._vbox = gtk.VBox()
        #self._vbox.props.width_request = 1

        self.add(self._vbox)
        self.show_all()

        # list
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

        # projects
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # align left
        #button.set_alignment(0.0, 0.5, 1.0, 0.0)
        
        image = gtk.image_new_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_BUTTON)
        button.set_image(image)

        button.set_title('Projects')

        self._vbox.pack_start(button, False, False, 0)
        button.show()
        button.connect('clicked', self._projects_clicked_cb)

        # contexts
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # align left
        #button.set_alignment(0.0, 0.5, 1.0, 0.0)
        
        image = gtk.image_new_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_BUTTON)
        button.set_image(image)

        button.set_title('Contexts')

        self._vbox.pack_start(button, False, False, 0)
        button.show()
        button.connect('clicked', self._contexts_clicked_cb)

        # new
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

    def _handle_failure_eb(self, failure, window):
        # only show one error dialog by setting a shown attribute on failure
        hildon.hildon_gtk_window_set_progress_indicator(window, 0)
        print failure
        msg = log.getFailureMessage(failure)

        self.debug(msg)

        from twisted.internet import error as tierror
        if failure.check(tierror.ConnectionRefusedError):
            msg = 'Fatal error: CouchDB is not running.'

        if not hasattr(failure, 'shown'):
            ew = error.ErrorWindow(msg)
    
            ew.show_all()
            failure.shown = True

        # close previous things window
        window.destroy()

        raise failure

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
            ('Shop', self._server.getThingsByContextCount, {'context': 'shop'}),
            ('Phone', self._server.getThingsByContextCount, {'context': 'phone'}),
        ]

        for name, method, kwargs in methods:
            d.addCallback(lambda _, m, kw: m(**kw), method, kwargs)
            d.addCallback(lambda result, n: w.add_list(n, result), name)

            d.addErrback(self._handle_failure_eb, w)


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
            'Shop': (self._server.getThingsByContext, {'context': 'shop'}),
            'Phone': (self._server.getThingsByContext, {'context': 'phone'}),
        }
        if list_name in methods.keys():
            hildon.hildon_gtk_window_set_progress_indicator(lw, 1)

            method, kwargs = methods[list_name]
            d = method(**kwargs)
            def _cb(result):
                # show all things in a list, but in reverse order
                result = list(result)
                result.reverse()

                w = things.ThingsWindow()
                for thing in result:
                    if thing.complete != 100:
                        w.add_thing(thing)
                hildon.hildon_gtk_window_set_progress_indicator(lw, 0)
                w.connect('selected', self._thing_selected_cb)
                w.show_all()
            d.addCallback(_cb)

            def _eb(failure):
                msg = log.getFailureMessage(failure)
                self.debug(msg)

                hildon.hildon_gtk_window_set_progress_indicator(lw, 0)
                ew = error.ErrorWindow(msg)
		
                ew.show_all()

                # close previous things window
                #w.destroy()

            d.addErrback(_eb)


    # show a window to edit the selected thing
    def _thing_selected_cb(self, tw, thing):
        # first populate lists, otherwise adding the thing adds some
        # items to the beginning of the list out of order
        #w = show.ShowWindow(thing)
        # FIXME: make uneditable until we have everything 
        w = new.NewWindow(new=False)
        w.show_all()
        d = self._populate_lists(w)

        def cb(r):
            self.debug('Adding thing %r for id %r', id(thing), thing.id)
            w.add_thing(thing)
            w.connect('done', self._update_done_cb, tw)
        d.addCallback(cb)

        return d

    def _populate_lists(self, w):
        # populate the project/context/status selectors with db values

        hildon.hildon_gtk_window_set_progress_indicator(w, 1)

        d = defer.Deferred()

        d.addCallback(lambda _: self._server.getProjects())
        def _cb(result):
            w.add_projects([p.name for p in list(result)])
        d.addCallback(_cb)
        d.addErrback(self._handle_failure_eb, w)

        d.addCallback(lambda _: self._server.getContexts())
        def _cb(result):
            w.add_contexts([p.name for p in list(result)])
        d.addCallback(_cb)
        d.addErrback(self._handle_failure_eb, w)

        d.addCallback(lambda _: self._server.getStatuses())
        def _cb(result):
            w.add_statuses([p.name for p in list(result)])
        d.addCallback(_cb)
        d.addErrback(self._handle_failure_eb, w)


        d.addCallback(lambda _:
            hildon.hildon_gtk_window_set_progress_indicator(w, 0))

        d.addCallback(lambda _: w.show_all())
        d.callback(None)

        return d

    def _projects_clicked_cb(self, button):
        w = lists.ListsWindow()
        hildon.hildon_gtk_window_set_progress_indicator(w, 1)

        d = self._server.getProjects()

        def cb(result):
            for project in result:
                w.add_list(project.name, project.things)
        d.addCallback(cb)
        d.addErrback(self._handle_failure_eb, w)

        d.addCallback(lambda _:
            hildon.hildon_gtk_window_set_progress_indicator(w, 0))

        w.connect('selected', self._project_selected_cb)
        #w.show_all()

    def _project_selected_cb(self, lw, project):
        hildon.hildon_gtk_window_set_progress_indicator(lw, 1)

        d = self._server.getThingsByProject(project)

        def _cb(result):
            # show all things in a list, but in reverse order
            result = list(result)
            result.reverse()

            w = things.ThingsWindow()
            for thing in result:
                if thing.complete != 100:
                    w.add_thing(thing)
            hildon.hildon_gtk_window_set_progress_indicator(lw, 0)
            w.connect('selected', self._thing_selected_cb)
            w.show_all()
        d.addCallback(_cb)

        def _eb(failure):
            msg = log.getFailureMessage(failure)
            self.debug(msg)

            hildon.hildon_gtk_window_set_progress_indicator(lw, 0)
            ew = error.ErrorWindow(msg)
    
            ew.show_all()

            # close previous things window
            #w.destroy()

        d.addErrback(_eb)

    def _contexts_clicked_cb(self, button):
        w = lists.ListsWindow()
        hildon.hildon_gtk_window_set_progress_indicator(w, 1)

        d = self._server.getContexts()

        def cb(result):
            for context in result:
                w.add_list(context.name, context.things)
        d.addCallback(cb)
        d.addErrback(self._handle_failure_eb, w)

        d.addCallback(lambda _:
            hildon.hildon_gtk_window_set_progress_indicator(w, 0))

        w.connect('selected', self._context_selected_cb)
        #w.show_all()

    def _context_selected_cb(self, lw, context):
        hildon.hildon_gtk_window_set_progress_indicator(lw, 1)

        d = self._server.getThingsByContext(context)

        def _cb(result):
            # show all things in a list, but in reverse order
            result = list(result)
            result.reverse()

            w = things.ThingsWindow()
            for thing in result:
                if thing.complete != 100:
                    w.add_thing(thing)
            hildon.hildon_gtk_window_set_progress_indicator(lw, 0)
            w.connect('selected', self._thing_selected_cb)
            w.show_all()
        d.addCallback(_cb)

        def _eb(failure):
            msg = log.getFailureMessage(failure)
            self.debug(msg)

            hildon.hildon_gtk_window_set_progress_indicator(lw, 0)
            ew = error.ErrorWindow(msg)
    
            ew.show_all()

            # close previous things window
            #w.destroy()

        d.addErrback(_eb)




    def _new_clicked_cb(self, button):
        w = new.NewWindow()
        w.connect('done', self._new_done_cb)

        return self._populate_lists(w)

    def _update_done_cb(self, window, things_window=None):
        # if things_window is passed, tell it to remove the thing if completed
        print 'thing id', window.thing.id

        window.get_thing(window.thing)

        t = window.thing

        print 'Title:', t.title
        print 'Projects:', t.projects
        print 'Contexts:', t.contexts
        print 'Flags:', t.statuses
        print 'Due date:', t.due

        print 'Urgency:', t.urgency
        print 'Importance:', t.importance
        print 'Duration:', t.time
        print 'Recurrence:', t.recurrence
        print '% complete:', t.complete


        hildon.hildon_gtk_window_set_progress_indicator(window, 1)

        d = defer.Deferred()

        d.addCallback(lambda _: self._server.save(window.thing))
        def cb(_):
            if window.thing.complete == 100 and things_window:
                self.debug('Thing %r is done, removing from list', window.thing)
                things_window.remove_thing(window.thing)
        d.addCallback(cb)

        def eb(failure):
            if not hasattr(failure, 'shown'):
                msg = log.getFailureMessage(failure)
                ew = error.ErrorWindow(msg)
    
                ew.show_all()
                failure.shown = True

        d.addErrback(eb)

        d.addCallback(lambda _:
            hildon.hildon_gtk_window_set_progress_indicator(window, 0))

        d.addCallback(lambda _: window.destroy())
        d.callback(None)

        return d

    def _new_done_cb(self, window):
        thing = couch.Thing()
        window.get_thing(thing)
        # FIXME: a bit dodgy, should the thing be on the window already ?
        window.thing = thing
        return self._update_done_cb(window, None)
