# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import gobject
import gtk
import hildon

class ShowWindow(hildon.StackableWindow):
    # Show a thing
    def __init__(self, thing):
        hildon.StackableWindow.__init__(self)

        self._panarea = hildon.PannableArea()

        self._table = gtk.Table(rows=8, columns=2)

        self._panarea.add_with_viewport(self._table)
        self.add(self._panarea)

        label = gtk.Label(thing.title)
        label.single_line_mode = False
        label.wrap = True
        self._table.attach(label, 0, 2, 0, 1, xoptions=0, yoptions=0)
        self._table.props.border_width = 6
        self._table.props.column_spacing = 6
        self._table.props.row_spacing = 6

        self._row = 1

        def add_label(name, value):
            if value:
                label = gtk.Label(name)
                label.set_justify(gtk.JUSTIFY_LEFT)
                label.props.xalign = 0.0
                self._table.attach(label, 0, 1, self._row, self._row + 1,
                    xoptions=0, yoptions=0)
                label = gtk.Label(value)
                self._table.attach(label, 1, 2, self._row, self._row + 1)
                self._row += 1

        def add_list(name, value):
            add_label(name, ", ".join(value))

        add_list("Projects:", thing.projects)
        add_list("Contexts:", thing.contexts)

        # flags
        # covey
        # dates
        add_label('Due:', thing.due)

        self.show_all()

def main():
    gtk.set_application_name('show a thing')

    class Thing(object):
        title = 'a thing'
        projects = ['mushin', ]
        contexts = ['home', 'hacking']
        due = '1902'
        
    thing = Thing()
    window = ShowWindow(thing)
    window.connect('destroy', lambda _: gtk.main_quit())

    window.show_all()

if __name__ == "__main__":
    main()
    gtk.main()
