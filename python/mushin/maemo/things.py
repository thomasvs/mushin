# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import gtk
import hildon

class ThingsWindow(hildon.StackableWindow):
    def __init__(self):
        hildon.StackableWindow.__init__(self)

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
        
        self._vbox.pack_start(button)

        button.set_title(thing.title)
        value = []
        if thing.projects:
            value.append('projects: %s' % ', '.join(thing.projects))
        if thing.contexts:
            value.append('contexts: %s' % ', '.join(thing.contexts))
        button.set_value(" - ".join(value))

        button.show()

def main():
    gtk.set_application_name('example list of things')

    class Thing(object):
        title = 'a thing'
        projects = ['mushin', ]
        contexts = ['home', 'hacking']
        
    window = ThingsWindow()
    window.connect('destroy', lambda _: gtk.main_quit())

    window.show_all()

    # FIXME: why does showing less than 6 items show all buttons and
    # put text wrong ?
    for i in range(10):
        t = Thing()
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
