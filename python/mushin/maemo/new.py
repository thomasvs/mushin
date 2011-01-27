# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

import sys
import datetime

import gobject
import gtk
import hildon

from mushin.model import couch
from mushin.common import log

# FIXME: currently also used for context, and status
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


class NewWindow(hildon.StackableWindow, log.Loggable):

    __gsignals__ = {
        'done': (gobject.SIGNAL_RUN_LAST, None, ( ))
    }

    _start = None

    # Create a new thing
    def __init__(self, new=True):
        hildon.StackableWindow.__init__(self)

        self._panarea = hildon.PannableArea()

        self._table = gtk.Table(rows=5, columns=6)
        self._table.props.width_request = 1

        self._panarea.add_with_viewport(self._table)
        self.add(self._panarea)

        self._date_button = None # either a normal or date button
        self._title_entry = None

        self._tags = {
            'project': {},
            'context': {},
            'status': {},
        }

        self._loaded = False # set to true by calling .loaded()
        ### first line: title
        label = gtk.Label("Title:")
        self._title_entry = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)

        self._table.attach(label, 0, 1, 0, 1)
        self._table.attach(self._title_entry, 1, 6, 0, 1)

        ### second line: project

        # Add to project

        project_picker = hildon.PickerButton(gtk.HILDON_SIZE_AUTO,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        project_picker.set_title("Add to project")
        self._project_selector = ProjectSelector()
        project_picker.set_selector(self._project_selector)

        self._table.attach(project_picker, 0, 1, 1, 2)
        self._tags['project']['selector'] = self._project_selector

        # create new project
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_NEW,
            gtk.ICON_SIZE_BUTTON)
        button.add(image)

        button.connect('clicked', self._add_project_cb)

        self._table.attach(button, 1, 2, 1, 2)

        # unset projects
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_DELETE,
            gtk.ICON_SIZE_BUTTON)
        button.add(image)

        button.connect('clicked',
            lambda b: self._project_selector.unselect_all(0))

        self._table.attach(button, 2, 3, 1, 2)

        ### second part second line: context

        # Add to context
        context_picker = hildon.PickerButton(gtk.HILDON_SIZE_AUTO,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        context_picker.set_title("Add to context")
        self._context_selector = ProjectSelector()
        context_picker.set_selector(self._context_selector)

        self._table.attach(context_picker, 0, 1, 2, 3)
        self._tags['context']['selector'] = self._context_selector

        # create new context
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_NEW,
            gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.add(image)
        button.connect('clicked', self._add_context_cb)
        # align left
        #button.set_alignment(0.0, 0.5, 1.0, 0.0)
        
        self._table.attach(button, 1, 2, 2, 3)

        # unset contexts
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_DELETE,
            gtk.ICON_SIZE_BUTTON)
        button.add(image)

        button.connect('clicked',
            lambda b: self._context_selector.unselect_all(0))

        self._table.attach(button, 2, 3, 2, 3)


        ### next line: statuses, due date

        # Add status
        status_picker = hildon.PickerButton(gtk.HILDON_SIZE_AUTO,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        status_picker.set_title("Add status")
        self._status_selector = ProjectSelector()
        status_picker.set_selector(self._status_selector)

        self._tags['status']['selector'] = self._status_selector
        self._table.attach(status_picker, 0, 1, 3, 4)

        # create new status
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_NEW,
            gtk.HILDON_SIZE_FINGER_HEIGHT)
        button.add(image)
        button.connect('clicked', self._add_status_cb)
        # align left
        #button.set_alignment(0.0, 0.5, 1.0, 0.0)
        
        self._table.attach(button, 1, 2, 3, 4)

        # unset statuses
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_DELETE,
            gtk.ICON_SIZE_BUTTON)
        button.add(image)

        button.connect('clicked',
            lambda b: self._status_selector.unselect_all(0))

        self._table.attach(button, 2, 3, 3, 4)

        self._reset_date_button()

        # remove button
        # FIXME: make image
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_DELETE,
            gtk.ICON_SIZE_BUTTON)
        button.add(image)

        def _remove_clicked_cb(button):
            self._table.remove(self._date_button)
            self._reset_date_button()

        button.connect('clicked', _remove_clicked_cb)
        self._table.attach(button, 2, 3, 4, 5)

        ### next line: urgency and priority

        def add_u_i(label, row):
            label = gtk.Label(label)
            label.props.xalign = 0.0
            button = hildon.PickerButton(
                gtk.HILDON_SIZE_FINGER_HEIGHT,
                hildon.BUTTON_ARRANGEMENT_VERTICAL)
            self._table.attach(label, 3, 5, 1 + row, 2 + row, xpadding=6)
            self._table.attach(button, 5, 6, 1 + row, 2 + row, xpadding=6)
            s = hildon.TouchSelector(text=True)
            button.set_selector(s)

            #s.append_text("None")
            for i in range(1, 6):
                s.append_text(str(i))

            return button

        self._urgency_button = add_u_i("Urgency:", row=0)
        self._importance_button = add_u_i("Importance:", row=1)
        
        ### next line: duration and recurrence
        def _add_d_r(label, row, default=0):
            label = gtk.Label(label)
            label.props.xalign = 0.0
            self._table.attach(label, 3, 4, 3 + row, 4 + row, xpadding=6)

            entry = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
            entry.props.hildon_input_mode = gtk.HILDON_GTK_INPUT_MODE_NUMERIC
            self._table.attach(entry, 4, 5, 3 + row, 4 + row)
            button = hildon.PickerButton(
                gtk.HILDON_SIZE_FINGER_HEIGHT,
                hildon.BUTTON_ARRANGEMENT_VERTICAL)
            self._table.attach(button, 5, 6, 3 + row, 4 + row)
            s = hildon.TouchSelector(text=True)
            button.set_selector(s)
            s.append_text('minutes')
            s.append_text('hours')
            s.append_text('days')
            s.append_text('weeks')
            # default to hours; assuming arguments are column, value ?
            s.set_active(0, default)
            return entry, s

        self._duration_entry, self._duration_selector = _add_d_r('Duration', 0)
        self._recurrence_entry, self._recurrence_selector = _add_d_r(
            'Recurs every', 1)
 

        ### last line: add button
        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # align left
        #button.set_alignment(0.0, 0.5, 1.0, 0.0)
        if new:
            button.set_title('Add')
        else:
            button.set_title('Update')
        button.connect('clicked', self._add_or_update_cb)

        self._table.attach(button, 0, 3, 6, 7)
 
        ### completion
        label = gtk.Label("% Complete")
        label.props.xalign = 0.0
        self._table.attach(label, 3, 4, 6, 7, xpadding=6)

        self._complete_entry = hildon.Entry(gtk.HILDON_SIZE_FINGER_HEIGHT)
        self._complete_entry.props.hildon_input_mode = gtk.HILDON_GTK_INPUT_MODE_NUMERIC
        self._table.attach(self._complete_entry, 4, 5, 6, 7)

        button = hildon.PickerButton(
            gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        image = gtk.image_new_from_stock(gtk.STOCK_APPLY,
            gtk.ICON_SIZE_BUTTON)
        button.add(image)

        self._table.attach(button, 5, 6, 6, 7)

        def _complete_clicked_cb(button):
            # we might have made other changes that are not set on thing
            self.get_thing(self.thing)

            self.thing.finish()
            self.add_thing(self.thing)

            # self._complete_entry.set_text('100')

        button.connect('clicked', _complete_clicked_cb)
 

        self.show_all()

    # start with a normal button that changes to a Date button
    # FIXME: make remove button only show when one is set
    # FIXME: make into optional date selector ?
    def _reset_date_button(self):
        if self._date_button:
            self._table.remove(self._date_button)

        self._date_button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)

        self._date_button.set_title('Due Date')
        self._table.attach(self._date_button, 0, 1, 4, 5)

        def _clicked_cb(button):
            self._set_date_button()
            self._date_button.clicked()

        self._date_button.connect('clicked', _clicked_cb)

        self._date_button.show()

    # set to an actual date button
    def _set_date_button(self):
        if self._date_button:
            self._table.remove(self._date_button)

        self._date_button = hildon.DateButton(
            gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        self._date_button.set_title('Due Date')
        self._table.attach(self._date_button, 0, 1, 4, 5)
        self._date_button.show()


    def _add_or_update_cb(self, button):
        # don't allow clicking until everything is loaded
        if self._loaded:
            if not self._start:
                self._start = datetime.datetime.now()
            # if it's recurring, make sure due is set
            recurrence = self.get_recurrence()
            if recurrence:
                due = self.get_due()
                if not due:
                    due = self._start + datetime.timedelta(seconds=recurrence)
                    self._set_due(due)


            self.emit('done')
        else:
            banner = hildon.hildon_banner_show_information(self, 'warning',
                "Please wait until projects, contexts and statuses are loaded")

    ### access the data
    def get_title(self):
        return self._title_entry.get_text()

    # get items from one of the selectors
    def _get_items(self, selector):
        """
        @rtype: list of str
        """
        # FIXME: get_selected seems wrapped wrong, needing an Iter instead of
        # giving us one; fix and recompile python-hildon 0.9.0
        # print self._project_selector.get_selected(iter, 2)

        # for now, work around it
        text = selector.get_current_text()

        if not text:
            return None

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

    def get_statuses(self):
        """
        @rtype: list of str
        """
        return self._get_items(self._status_selector)

    def get_due(self):
        if hasattr(self._date_button, 'get_date'):
            (year, month, day) =  self._date_button.get_date()
            # March is returned as month 2, so add 1
            return datetime.datetime(year, month + 1, day)

    def _get_u_i(self, button):
        value = button.get_value()
        if value is None or value == '':
            return None

        return int(value)

    def get_urgency(self):
        """
        @rtype: int or None
        """
        return self._get_u_i(self._urgency_button)

    def get_importance(self):
        """
        @rtype: int or None
        """
        return self._get_u_i(self._importance_button)

    def _get_d_r(self, entry, button):
        value = entry.get_text()
        unit = button.get_active(0)

        if value is None or value == '':
            return None

        value = int(value)

        if unit == 0:
            return value * 60
        if unit == 1:
            return value * 60 * 60
        if unit == 2:
            return value * 60 * 60 * 24
        if unit == 3:
            return value * 60 * 60 * 24 * 7

    def get_duration(self):
        """
        @returns: duration in seconds
        @rtype:   int or None
        """
        return self._get_d_r(self._duration_entry, self._duration_selector)

    def get_recurrence(self):
        """
        @returns: recurrence in seconds
        @rtype:   int or None
        """
        return self._get_d_r(self._recurrence_entry, self._recurrence_selector)
         
    def get_complete(self):
        """
        @rtype: int or None
        """
        t = self._complete_entry.get_text()

        if not t:
            return None

        return int(t)

    def add_tag(self, tag, items):
        for item in items:
            self._tags[tag]['selector'].add_text(item)

    def add_projects(self, projects):
        self.add_tag('project', projects)

    def add_contexts(self, contexts):
        self.add_tag('context', contexts)

    def add_statuses(self, statuses):
        self.add_tag('status', statuses)

    def _set_d_r(self, entry, button, value):
        if value is None:
            return

        minutes = value / 60
        hours = minutes / 60
        days = hours / 24
        weeks = days / 7

        if hours * 60 != minutes:
            button.set_active(0, 0)
            entry.set_text(str(minutes))
        elif days * 24 != hours:
            button.set_active(0, 1)
            entry.set_text(str(hours))
        elif weeks * 7 != days:
            button.set_active(0, 2)
            entry.set_text(str(days))
        else:
            button.set_active(0, 3)
            entry.set_text(str(weeks))

    def _set_due(self, due):
        self._set_date_button()
        # month starts from 0, so subtract one
        self._date_button.set_date(
            due.year, due.month - 1, due.day)

    def _populate_selector(self, selector, items):
        self.debug('populating %r with items %r', selector, items)

        model = selector.get_model(0)

        # map project name to iter in model
        iters = dict([(row[0], row.iter) for row in model])

        for item in items:
            # add non-existent project to selector
            if not item in iters.keys():
                self.debug('adding item %r', item)
                selector.add_text(item)
                iters[item] = model[-1].iter

            # select the row for this item
            self.debug('selecting %r', item)
            selector.select_iter(0, iters[item], False)

    # FIXME: rename to set_thing ?
    def add_thing(self, thing):
        self._title_entry.set_text(thing.title)

        self._populate_selector(self._project_selector, thing.projects)        
        self._populate_selector(self._context_selector, thing.contexts)        
        self._populate_selector(self._status_selector, thing.statuses)        

        if thing.due:
            self._set_due(thing.due)

        if thing.urgency:
            self._urgency_button.set_active(thing.urgency - 1)
        if thing.importance:
            self._importance_button.set_active(thing.importance - 1)

        self._set_d_r(
            self._duration_entry, self._duration_selector, thing.time)
        self._set_d_r(
            self._recurrence_entry, self._recurrence_selector, thing.recurrence)

        self._complete_entry.set_text(str(thing.complete))

        self._start = thing.start

        self.thing = thing

    def get_thing(self, thing):
        """
        Fill in values from the window into the given thing.
        """
        thing.title =  self.get_title()
        thing.projects = self.get_projects()
        thing.contexts = self.get_contexts()
        thing.statuses = self.get_statuses()
        thing.start = self._start
        thing.due = self.get_due()

        thing.urgency = self.get_urgency()
        thing.importance = self.get_importance()
        thing.time = self.get_duration()
        thing.recurrence = self.get_recurrence()
        thing.complete = self.get_complete()

    def _add_project_cb(self, button):
        self._show_add_dialog('Add a project', 'project', self._add_clicked_cb)

    def _add_context_cb(self, button):
        self._show_add_dialog('Add a context', 'context', self._add_clicked_cb)

    def _add_status_cb(self, button):
        self._show_add_dialog('Add a status', 'status', self._add_clicked_cb)

    def _show_add_dialog(self, title, tag, callback):
        d = gtk.Dialog(title=title)
        box = gtk.HBox()
        d.vbox.add(box)

        entry = hildon.Entry(gtk.HILDON_SIZE_AUTO)
        entry.set_input_mode(gtk.HILDON_GTK_INPUT_MODE_ALPHA
            | gtk.HILDON_GTK_INPUT_MODE_NUMERIC)
        #entry.connect('activate', callback, tag)
        entry.props.activates_default = True
        box.add(entry)

        button = hildon.Button(gtk.HILDON_SIZE_FINGER_HEIGHT,
            hildon.BUTTON_ARRANGEMENT_VERTICAL)
        # align left
        button.set_alignment(0.0, 0.5, 1.0, 0.0)
        button.set_title('Add')
        button.connect('clicked', callback, entry, d, tag)
        
        box.pack_start(button)

        d.show_all()

    def _add_clicked_cb(self, button, entry, d, tag):
        item = entry.get_text()
        self._populate_selector(self._tags[tag]['selector'], [item, ])
        d.destroy()

        #add = AddWindow()
        #add.show_all()
 
    def loaded(self):
        self._loaded = True

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

    # compare with mushin.model.couch.Thing
    # FIXME: flags or statuses ? 

    class Thing(object):
        pass

    class OldThing(couch.Thing):
        title = 'a thing'
        projects = [u'mushin', u'newproject']
        contexts = [u'home', u'hacking']
        statuses = [u'waitingon']
        # march
        # due = datetime.datetime(2011, 3, 20)
        complete = 50
        urgency = 2
        importance = 4

        time = 3600
        recurrence = 60 * 60 * 24 * 7
        
    def done_cb(window):
        t = Thing()
        window.get_thing(t)

        print 'Title:', t.title
        print 'Projects:', t.projects
        print 'Contexts:', t.contexts
        print 'Flags:', t.statuses
        print 'Start date:', t.start
        print 'Due date:', t.due

        print 'Urgency:', t.urgency
        print 'Importance:', t.importance
        print 'Duration:', t.time
        print 'Recurrence:', t.recurrence
        print '% complete:', t.complete

        window.destroy()

    new = False
    if len(sys.argv) > 1:
        new = True

    window = NewWindow(new)

    window.add_contexts(['hack', 'shop', 'work', 'home'])
    window.add_projects(['mushin', 'moap', 'mach'])
    window.add_statuses(['next', ])
    window.loaded()

    if not new:
        t = OldThing()
        window.add_thing(t)

    window.connect('done', done_cb)
    window.connect('destroy', lambda _: gtk.main_quit())

    window.show_all()

if __name__ == "__main__":
    log.init()
    main()
    gtk.main()
