# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import gobject
import gtk
import hildon

from mushin.model import couch
from mushin.common import format

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
        add_list("Status:", thing.statuses)

        # covey
        covey = "%.2f" % thing.priority()
        how = {
            1: 'not very',
            2: 'a little',
            3: '',
            4: 'quite',
            5: 'very',
        }
        if thing.urgency:
            covey += ', %s urgent' % how[thing.urgency]
        if thing.importance:
            covey += ', %s important' % how[thing.importance]

        add_label('Priority:', covey)

        # dates
        add_label('Due:', format.deadline(thing.due))
        add_label('Started:', format.ago(thing.start))

        self.show_all()

def main():
    import datetime

    gtk.set_application_name('show a thing')

    thing = couch.Thing(
        title='a thing',
        projects=['mushin', ],
        contexts=['home', 'hacking'],
        statuses=['waitingfor'],
        start=datetime.datetime(year=2009, month=1, day=1),
        due=datetime.datetime(year=2035, month=1, day=1),
        )
    window = ShowWindow(thing)
    window.connect('destroy', lambda _: gtk.main_quit())

    window.show_all()

if __name__ == "__main__":
    main()
    gtk.main()
