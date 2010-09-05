# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import gobject
import gtk
import hildon

class ListsWindow(hildon.StackableWindow):
    __gsignals__ = {
        'selected': (gobject.SIGNAL_RUN_LAST, None, (str, ))
    }

    def __init__(self):
        hildon.StackableWindow.__init__(self)

        self._panarea = hildon.PannableArea()

        # self._vbox = gtk.VBox()
        self._vbox = gtk.Table()
        self._counter = 0
        self._vbox.props.width_request = 1

        self._panarea.add_with_viewport(self._vbox)
        self.add(self._panarea)
        self.show_all()

    def add_list(self, list_name, list_length):
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # align left
        button.set_alignment(0.0, 0.5, 1.0, 0.0)
        
        # 4 by 3 grid
        row = self._counter % 4
        col = self._counter / 4
        self._vbox.attach(button, row, row + 1, col, col + 1, True, True, 0)
        self._counter += 1
        # self._vbox.pack_start(button, False, False, 0)

        button.set_title(list_name)
        button.set_value("%d things" % list_length)
        button.connect('clicked', self._button_clicked_cb, list_name)

        button.show()

    def _button_clicked_cb(self, button, list_name):
        self.emit('selected', list_name)

def main():
    gtk.set_application_name('example lists')

       
    window = ListsWindow()

    window.connect('destroy', lambda _: gtk.main_quit())

    def selected_cb(window, list_name):
        print 'selected list name', list_name
        gtk.main_quit()
    window.connect('selected', selected_cb)

    window.show_all()

    for i in range(3):
        window.add_list('list %d' % i, i ** 2)

if __name__ == "__main__":
    main()
    gtk.main()
