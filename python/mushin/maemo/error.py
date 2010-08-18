# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import gobject
import gtk
import hildon

from mushin.model import couch
from mushin.common import format

class ErrorWindow(hildon.StackableWindow):
    # show an error
    def __init__(self, error):
        hildon.StackableWindow.__init__(self)

        label = gtk.Label(error)
        self.add(label)

def main():
    import datetime

    gtk.set_application_name('show an error')

    window = ErrorWindow('reactor meltdown. fatal radiation imminent')
    window.connect('destroy', lambda _: gtk.main_quit())

    window.show_all()

if __name__ == "__main__":
    main()
    gtk.main()
