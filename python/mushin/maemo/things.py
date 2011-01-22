# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import gobject
import gtk
import hildon

from mushin.model import couch
from mushin.common import format

# FIXME; move to a treeview and a treemodel
# add LiveSearch; see http://maemo.gitorious.org/hildon/hildon/blobs/hildon-2-2/examples/hildon-live-search-example.c
class ThingsWindow(hildon.StackableWindow):
    __gsignals__ = {
        'selected': (gobject.SIGNAL_RUN_LAST, None, (object, ))
    }

    def __init__(self):
        hildon.StackableWindow.__init__(self)

        self._thing_buttons = {} # thing -> button

        self._panarea = hildon.PannableArea()

        self._vbox = gtk.VBox()
        self._vbox.props.width_request = 1

        self._panarea.add_with_viewport(self._vbox)
        self.add(self._panarea)
        self.show_all()

    def add_thing(self, thing):
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # align left
        button.set_alignment(0.0, 0.5, 1.0, 0.0)
        self._thing_buttons[thing] = button
        
        self._vbox.pack_start(button, False, False, 0)

        button.set_title(thing.title)
        value = []
        if thing.projects:
            value.append('projects: %s' % ', '.join(thing.projects))
        if thing.contexts:
            value.append('contexts: %s' % ', '.join(thing.contexts))
        if thing.statuses:
            value.append('statuses: %s' % ', '.join(thing.statuses))
        if thing.due:
            value.append(format.deadline(thing.due))

        button.set_value(" - ".join(value))

        button.show()

        button.connect('clicked', self._button_clicked_cb, thing)

        button.show()

    def _button_clicked_cb(self, button, thing):
        self.emit('selected', thing)

    def remove_thing(self, thing):
        self._vbox.remove(self._thing_buttons[thing])
        
def main():
    gtk.set_application_name('example list of things')

    class OldThing(couch.Thing):
        title = 'a thing'
        projects = ['mushin', ]
        contexts = ['home', 'hacking']
        
    window = ThingsWindow()
    window.connect('destroy', lambda _: gtk.main_quit())

    window.show_all()

    for i in range(3):
        t = OldThing()
        t.title = 'thing %d' % i
        window.add_thing(t)

if __name__ == "__main__":
    main()
    gtk.main()

    #from twisted.internet import gtk2reactor
    #gtk2reactor.install()
    #from twisted.internet import reactor

    #reactor.callWhenRunning(main)
    #reactor.run()
