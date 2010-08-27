# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import sys
import datetime

import gobject
import gtk
import hildon

# FIXME: currently also used for context, and flag
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
    def __init__(self, new=True):
        hildon.StackableWindow.__init__(self)

        self._panarea = hildon.PannableArea()

        self._vbox = gtk.VBox()
        self._vbox.props.width_request = 1

        self._panarea.add_with_viewport(self._vbox)
        self.add(self._panarea)

        self._date_button = None # either a normal or date button
        self._title_entry = None

        ### first line: title
        hbox = gtk.HBox()
        label = gtk.Label("Title:")
        self._title_entry = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        hbox.pack_start(label, expand=False, fill=False, padding=6)
        hbox.pack_start(self._title_entry)

        self._vbox.pack_start(hbox, False, False, 0)

        ### second line: project

        hbox = gtk.HBox()
        self._vbox.pack_start(hbox, False, True, 0)

        # Add to project

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
            gtk.ICON_SIZE_BUTTON)
        button.add(image)

        button.connect('clicked', self._add_project_cb)

        hbox.pack_start(button, False, False, 0)

        # unset projects
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_DELETE,
            gtk.ICON_SIZE_BUTTON)
        button.add(image)

        button.connect('clicked',
            lambda b: self._project_selector.unselect_all(0))

        hbox.pack_start(button, False, False, 0)


        ### second part second line: context

        # Add to context
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

        # unset contexts
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_DELETE,
            gtk.ICON_SIZE_BUTTON)
        button.add(image)

        button.connect('clicked',
            lambda b: self._context_selector.unselect_all(0))

        hbox.pack_start(button, False, False, 0)


        ### next line: flags, due date

        hbox = gtk.HBox()

        self._vbox.pack_start(hbox, False, True, 0)

        # Add flag
        flag_picker = hildon.PickerButton(gtk.HILDON_SIZE_AUTO,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        flag_picker.set_title("Add flag")
        self._flag_selector = ProjectSelector()
        flag_picker.set_selector(self._flag_selector)

        hbox.pack_start(flag_picker, False, False, 0)

        # create new flag
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_NEW,
            gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.add(image)
        button.connect('clicked', self._add_flag_cb)
        # align left
        #button.set_alignment(0.0, 0.5, 1.0, 0.0)
        
        hbox.pack_start(button, False, False, 0)

        # unset flags
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_DELETE,
            gtk.ICON_SIZE_BUTTON)
        button.add(image)

        button.connect('clicked',
            lambda b: self._flag_selector.unselect_all(0))

        hbox.pack_start(button, False, False, 0)


        # start with a normal button that changes to a Date button
        # FIXME: make remove button only show when one is set
        # FIXME: make into optional date selector ?
        def _reset_date_button(hbox):
            self._date_button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
                hildon.BUTTON_ARRANGEMENT_VERTICAL)
            button = self._date_button

            button.set_title('Due Date')
            # align left
            button.set_alignment(0.0, 0.5, 1.0, 0.0)
            hbox.pack_start(button, False, False, 0)
            button.show()

            def _due_date_cb(button, parent):
                # replaces normal button with date button
                assert button == self._date_button

                parent.remove(button)

                self._date_button = hildon.DateButton(
                    gtk.HILDON_SIZE_FINGER_HEIGHT,
                    hildon.BUTTON_ARRANGEMENT_VERTICAL)
                self._date_button.set_title('Due Date')
                self._date_button.clicked()
                parent.pack_start(self._date_button, False, False, 0)
                parent.show_all()
                self._date_button.connect('clicked', _due_date_cb, hbox)

            button.connect('clicked', _due_date_cb, hbox)

        _reset_date_button(hbox)

        # remove button
        # FIXME: make image
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)

        button.set_title('Remove Due Date')

        def _remove_clicked_cb(button, hbox):
            hbox.remove(self._date_button)
            _reset_date_button(hbox)

        button.connect('clicked', _remove_clicked_cb, hbox)
        hbox.pack_end(button, False, False, 0)

        ### next line: urgency and priority
        hbox = gtk.HBox()
        self._vbox.pack_start(hbox, False, False, 0)

        def add_u_i(hbox, label):
            label = gtk.Label(label)
            button = hildon.PickerButton(
                gtk.HILDON_SIZE_FINGER_HEIGHT,
                hildon.BUTTON_ARRANGEMENT_VERTICAL)
            hbox.pack_start(label, False, False)
            hbox.pack_start(button, True, False)
            s = hildon.TouchSelector(text=True)
            button.set_selector(s)

            #s.append_text("None")
            for i in range(1, 6):
                s.append_text(str(i))

            return button

        self._urgency_button = add_u_i(hbox, "Urgency:")
        self._importance_button = add_u_i(hbox, "Importance:")
        
        ### next line: duration and recurrence
        hbox = gtk.HBox()
        self._vbox.pack_start(hbox, False, False, 0)

        def _add_d_r(label, default):
            label = gtk.Label(label)
            hbox.pack_start(label, False, False)

            entry = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
            entry.props.hildon_input_mode = gtk.HILDON_GTK_INPUT_MODE_NUMERIC
            hbox.pack_start(entry)
            button = hildon.PickerButton(
                gtk.HILDON_SIZE_FINGER_HEIGHT,
                hildon.BUTTON_ARRANGEMENT_VERTICAL)
            hbox.pack_start(button, True, False)
            s = hildon.TouchSelector(text=True)
            button.set_selector(s)
            s.append_text('minutes')
            s.append_text('hours')
            s.append_text('days')
            s.append_text('weeks')
            # default to hours; assuming arguments are column, value ?
            s.set_active(0, default)
            return entry, s

        self._duration_entry, self._duration_selector = _add_d_r('Duration', 1)
        self._recurrence_entry, self._recurrence_selector = _add_d_r(
            'Recurs every', 2)
 

        ### last line: add button
        hbox = gtk.HBox()
        self._vbox.pack_start(hbox, False, True, 0)

        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # align left
        #button.set_alignment(0.0, 0.5, 1.0, 0.0)
        if new:
            button.set_title('Add')
        else:
            button.set_title('Update')
        button.connect('clicked', self._add_cb)

        hbox.pack_start(button, True, False, 0)
 
        self.show_all()

    def _add_cb(self, button):
        self.emit('done')

    # access the data
    def get_due(self):
        if hasattr(self._date_button, 'get_date'):
            (year, month, day) =  self._date_button.get_date()
            # March is returned as month 2, so add 1
            return datetime.datetime(year, month + 1, day)

    def get_title(self):
        return self._title_entry.get_text()

    def _get_items(self, selector):
        """
        @rtype: list of str
        """
        # FIXME: get_selected seems wrapped wrong, needing an Iter instead of
        # giving us one; fix and recompile python-hildon 0.9.0
        # print self._project_selector.get_selected(iter, 2)

        # for now, work around it
        text = selector.get_current_text()
        items = text[1:-1].split(',')
        # empty text results in [''] instead of []
        return items[0] and items or []

    def get_projects(self):
        """
        @rtype: list of str
        """
        return self._get_items(self._project_selector)

    def get_contexts(self):
        """
        @rtype: list of str
        """
        return self._get_items(self._context_selector)

    def get_flags(self):
        """
        @rtype: list of str
        """
        return self._get_items(self._flag_selector)

    def add_projects(self, projects):
        for project in projects:
            self._project_selector.add_text(project)

    def add_contexts(self, contexts):
        for context in contexts:
            self._context_selector.add_text(context)

    def add_flags(self, flags):
        for flag in flags:
            self._flag_selector.add_text(flag)

    def add_thing(self, thing):
        self._title_entry.set_text(thing.title)

        def _populate_selector(selector, items):

            model = selector.get_model(0)

            # map project name to iter in model
            iters = dict([(row[0], row.iter) for row in model])

            for project in items:
                # add non-existent project to selector
                if not project in iters.keys():
                    selector.append_text(project)
                    iters[project] = model[-1].iter

                # select the row for this project
                selector.select_iter(0, iters[project], False)

        _populate_selector(self._project_selector, thing.projects)        
        _populate_selector(self._context_selector, thing.contexts)        
        _populate_selector(self._flag_selector, thing.flags)        

        self.thing = thing

    def _add_project_cb(self, button):
        self._show_add_dialog('Add a project', self._add_project_clicked_cb)

    # TODO: FIXME: why different ?
    def _add_context_cb(self, button):
        d = gtk.Dialog(title='Add a context')
        self._entry = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        self._entry.connect('activate', self._add_context_activate_cb)
        self._entry.props.activates_default = True
        d.vbox.add(self._entry)
        d.show_all()

    def _add_flag_cb(self, button):
        self._show_add_dialog('Add a flag', self._add_flag_clicked_cb)

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

    def _add_flag_clicked_cb(self, button, entry):
        flag = entry.get_text()
        self.add_flags([flag, ])


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

    def _get_u_i_value(self, value):
        if not value: return None
        if value == 'None': return None
        return int(value)
 
def main():
    gtk.set_application_name('add/edit thing')

    class Thing(object):
        title = 'a thing'
        projects = ['mushin', 'newproject']
        contexts = ['home', 'hacking']
        flags = ['waitingon']
        
    def done_cb(window):
        # get data out of the window
        print 'Title:', window.get_title()
        print 'Projects:', window.get_projects()
        print 'Contexts:', window.get_contexts()
        print 'Due date:', window.get_due()

        window.destroy()

    new = True
    if len(sys.argv) > 1:
        # run in edit mode
        new = False

    window = NewWindow(new)

    window.add_contexts(['hack', 'shop', 'work', 'home'])
    window.add_projects(['mushin', 'moap', 'mach'])
    window.add_flags(['next', ])

    if not new:
        t = Thing()
        t.title = sys.argv[1]
        window.add_thing(t)

    window.connect('done', done_cb)
    window.connect('destroy', lambda _: gtk.main_quit())

    window.show_all()

if __name__ == "__main__":
    main()
    gtk.main()
