# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import datetime
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

    __gsignals__ = {
        'done': (gobject.SIGNAL_RUN_LAST, None, ( ))
    }

    # Create a new thing
    def __init__(self):
        hildon.StackableWindow.__init__(self)

        self._panarea = hildon.PannableArea()

        self._vbox = gtk.VBox()
        self._vbox.props.width_request = 1

        self._panarea.add_with_viewport(self._vbox)
        self.add(self._panarea)

        ### first line: title
        hbox = gtk.HBox()
        label = gtk.Label("Title:")
        self._entry = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        hbox.pack_start(label)
        hbox.pack_start(self._entry)

        self._vbox.pack_start(hbox, False, False, 0)

        ### second line: project

        hbox = gtk.HBox()

        # Add to project
        self._vbox.pack_start(hbox, False, True, 0)

        project_picker = hildon.PickerButton(gtk.HILDON_SIZE_AUTO,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        project_picker.set_title("Add to project")
        self._project_selector = ProjectSelector()
        project_picker.set_selector(self._project_selector)

        hbox.pack_start(project_picker, False, False, 0)

        # create new project
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_NEW,
            gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.add(image)
        button.connect('clicked', self._add_project_cb)
        # align left
        #button.set_alignment(0.0, 0.5, 1.0, 0.0)
        
        hbox.pack_start(button, False, False, 0)

        #button.set_title('New ...')

        ### third line: context

        hbox = gtk.HBox()

        # Add to context
        self._vbox.pack_start(hbox, False, True, 0)

        context_picker = hildon.PickerButton(gtk.HILDON_SIZE_AUTO,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        context_picker.set_title("Add to context")
        self._context_selector = ProjectSelector()
        context_picker.set_selector(self._context_selector)

        hbox.pack_start(context_picker, False, False, 0)

        # create new context
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_NEW,
            gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.add(image)
        button.connect('clicked', self._add_context_cb)
        # align left
        #button.set_alignment(0.0, 0.5, 1.0, 0.0)
        
        hbox.pack_start(button, False, False, 0)

        ### due date

        hbox = gtk.HBox()

        self._vbox.pack_start(hbox, False, True, 0)

        # start with a normal button that changes to a Date button
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # align left
        button.set_alignment(0.0, 0.5, 1.0, 0.0)
        button.set_title('Due Date')
        def _due_date_cb(button):
            hbox.remove(button)
            self._date_button = hildon.DateButton(gtk.HILDON_SIZE_FINGER_HEIGHT,
                hildon.BUTTON_ARRANGEMENT_VERTICAL)
            self._date_button.set_title('Due Date')
            self._date_button.clicked()
            hbox.pack_start(self._date_button, False, False, 0)
            hbox.show_all()

        button.connect('clicked', _due_date_cb)

        #self._date_button = hildon.DateButton(gtk.HILDON_SIZE_FINGER_HEIGHT,
        #    hildon.BUTTON_ARRANGEMENT_VERTICAL)
        #self._date_button.set_title('Due Date')

        hbox.pack_start(button, False, False, 0)


        ### last line: add button
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # align left
        button.set_alignment(0.0, 0.5, 1.0, 0.0)
        button.set_title('Add')
        button.connect('clicked', self._add_cb)

        self._vbox.pack_start(button, False, True, 0)
 
        self.show_all()

    def _add_cb(self, button):
        self.emit('done')

    # access the data
    def get_due(self):
        (year, month, day) =  self._date_button.get_date()
        # March is returned as month 2, so add 1
        return datetime.datetime(year, month + 1, day)

    def get_title(self):
        return self._entry.get_text()

    def get_projects(self):
        """
        @rtype: list of str
        """
        # FIXME: get_selected seems wrapped wrong, needing an Iter instead of
        # giving us one; fix and recompile python-hildon 0.9.0
        # print self._project_selector.get_selected(iter, 2)

        # for now, work around it
        text = self._project_selector.get_current_text()
        projects = text[1:-1].split(',')
        # empty text results in [''] instead of []
        return projects[0] and projects or []

    def get_contexts(self):
        """
        @rtype: list of str
        """
        # FIXME: get_selected seems wrapped wrong, needing an Iter instead of
        # giving us one; fix and recompile python-hildon 0.9.0
        # print self._context_selector.get_selected(iter, 2)

        # for now, work around it
        text = self._context_selector.get_current_text()
        contexts = text[1:-1].split(',')
        # empty text results in [''] instead of []
        return contexts[0] and contexts or []


    def add_contexts(self, contexts):
        for context in contexts:
            self._context_selector.add_text(context)

    def add_projects(self, projects):
        for project in projects:
            self._project_selector.add_text(project)

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

        self.thing = thing

    def _add_project_cb(self, button):
        self._show_add_dialog('Add a project', self._add_project_clicked_cb)

    def _add_context_cb(self, button):
        d = gtk.Dialog(title='Add a context')
        self._entry = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        self._entry.connect('activate', self._add_context_activate_cb)
        self._entry.props.activates_default = True
        d.vbox.add(self._entry)
        d.show_all()

    def _show_add_dialog(self, title, callback):
        d = gtk.Dialog(title=title)
        box = gtk.HBox()
        d.vbox.add(box)

        entry = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        entry.connect('activate', self._add_context_activate_cb)
        entry.props.activates_default = True
        box.add(entry)

        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # align left
        button.set_alignment(0.0, 0.5, 1.0, 0.0)
        button.set_title('Add')
        button.connect('clicked', callback, entry)
        
        box.pack_start(button)

        d.show_all()


    def _add_project_clicked_cb(self, button, entry):
        project = entry.get_text()
        self.add_projects([project, ])

    def _add_context_activate_cb(self, entry):
        print 'entry activated', entry.get_text()


        #add = AddWindow()
        #add.show_all()

class AddWindow(hildon.StackableWindow):
    # Add a project or context through an entry
    def __init__(self, what='category'):
        hildon.StackableWindow.__init__(self)

        self._vbox = gtk.VBox()
        self.add(self._vbox)

        self._vbox.add(gtk.Label('Add a new %s' % what))
        self._entry = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        self._vbox.add(self._entry)

        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_NEW, gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.add(image)
        button.connect('clicked', self._add_cb)

        self._vbox.add(button)

    def _add_cb(self, button):
        self.hide()

 
def main():
    gtk.set_application_name('add a new thing')

    class Thing(object):
        title = 'a thing'
        projects = ['mushin', ]
        contexts = ['home', 'hacking']
        
    def done_cb(window):
        # get data out of the window
        print 'Title:', window.get_title()
        print 'Projects:', window.get_projects()
        print 'Contexts:', window.get_contexts()
        print 'Due date:', window.get_due()

        window.destroy()

    window = NewWindow()
    window.add_contexts(['hack', 'shop', 'work', 'home'])
    window.add_projects(['mushin', 'moap', 'mach'])
    window.connect('done', done_cb)
    window.connect('destroy', lambda _: gtk.main_quit())

    window.show_all()

if __name__ == "__main__":
    main()
    gtk.main()
