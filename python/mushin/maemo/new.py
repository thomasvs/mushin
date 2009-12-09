# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import gobject
import gtk
import hildon

# FIXME: currently also used for context
class ProjectSelector(hildon.TouchSelector):
    # FIXME: would be nice to combine TouchSelectorEntry's mode with multiselect

    def __init__(self):
        hildon.TouchSelector.__init__(self, text=True)

        self._multi = False

        #column.set_property("text-column", 0)

    def add_text(self, text):
        # when calling this before the first line of text is added, we get
        # GtkWarning: gtk_list_store_get_path:
        # assertion `iter->stamp == GTK_LIST_STORE (tree_model)->stamp' failed

        # but if calling after, then the first item gets autoselected ?
        if not self._multi:
            self._multi = True
            self.set_column_selection_mode(
                hildon.TOUCH_SELECTOR_SELECTION_MODE_MULTIPLE)

        self.append_text(text)


class NewWindow(hildon.StackableWindow):
    # Create a new thing
    def __init__(self):
        hildon.StackableWindow.__init__(self)

        self._panarea = hildon.PannableArea()

        self._vbox = gtk.VBox()
        self._vbox.props.width_request = 1

        self._panarea.add_with_viewport(self._vbox)
        self.add(self._panarea)

        self._hbox = gtk.HBox()
        label = gtk.Label("Title:")
        self._entry = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self._hbox.pack_start(label)
        self._hbox.pack_start(self._entry)

        self._vbox.pack_start(self._hbox, False, False, 0)

        # Add to project
        project_picker = hildon.PickerButton(gtk.HILDON_SIZE_AUTO,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        project_picker.set_title("Add to project")
        selector = ProjectSelector()
        for project in ['mushin', 'moap', 'mach']:
            selector.add_text(project)
        project_picker.set_selector(selector)

        self._vbox.pack_start(project_picker, False, False, 0)

        # Add to context
        context_picker = hildon.PickerButton(gtk.HILDON_SIZE_AUTO,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        context_picker.set_title("Add to context")
        selector = ProjectSelector()
        for context in ['hack', 'shop', 'work', 'home']:
            selector.add_text(context)
        context_picker.set_selector(selector)

        self._vbox.pack_start(context_picker, False, False, 0)


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
    gtk.set_application_name('add a new thing')

    class Thing(object):
        title = 'a thing'
        projects = ['mushin', ]
        contexts = ['home', 'hacking']
        
    window = NewWindow()
    window.connect('destroy', lambda _: gtk.main_quit())

    window.show_all()

if __name__ == "__main__":
    main()
    gtk.main()
