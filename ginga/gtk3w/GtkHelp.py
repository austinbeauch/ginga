#
# GtkHelp.py -- customized Gtk3 widgets
#
# This is open-source software licensed under a BSD license.
# Please see the file LICENSE.txt for details.
#
import sys
import os.path
import math

from ginga.misc import Bunch, Callback
import ginga.toolkit

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import GObject
from gi.repository import Pango
import cairo

ginga.toolkit.use('gtk3')


class WidgetMask(object):
    def __init__(self, *args):
        self.cb_fn = None
        self.cb_args = []
        self.cb_kwdargs = {}

        self.connected = False
        self.changed = False

    def sconnect(self, signal, cb_fn, *args, **kwdargs):
        self.cb_fn = cb_fn
        self.cb_args = args
        self.cb_kwdargs = kwdargs

        self.connect(signal, self.cb)
        self.connected = True

    def change(self):
        if self.connected:
            self.changed = True

    def cb(self, *args):
        if self.changed:
            self.changed = False
            return

        newargs = list(args)
        newargs.extend(self.cb_args)
        kwdargs = self.cb_kwdargs.copy()
        return self.cb_fn(*newargs, **kwdargs)


class TopLevel(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self)

class CheckButton(WidgetMask, Gtk.CheckButton):
    def __init__(self, *args, **kwdargs):
        WidgetMask.__init__(self)
        Gtk.CheckButton.__init__(self, *args, **kwdargs)

    def set_active(self, newval):
        oldval = self.get_active()
        if oldval != newval:
            self.change()

        super(CheckButton, self).set_active(newval)

class ToggleButton(WidgetMask, Gtk.ToggleButton):
    def __init__(self, *args, **kwdargs):
        WidgetMask.__init__(self)
        Gtk.ToggleButton.__init__(self, *args, **kwdargs)

    def set_active(self, newval):
        oldval = self.get_active()
        if oldval != newval:
            self.change()

        super(ToggleButton, self).set_active(newval)

    def toggle(self):
        oldval = self.get_active()
        newval = not oldval
        super(ToggleButton, self).set_active(newval)


class RadioButton(WidgetMask, Gtk.RadioButton):
    def __init__(self, *args, **kwdargs):
        WidgetMask.__init__(self)
        Gtk.RadioButton.__init__(self, *args, **kwdargs)

    def set_active(self, newval):
        oldval = self.get_active()
        if oldval != newval:
            self.change()

        super(RadioButton, self).set_active(newval)

    def toggle(self):
        oldval = self.get_active()
        newval = not oldval
        super(RadioButton, self).set_active(newval)


class CheckMenuItem(WidgetMask, Gtk.CheckMenuItem):
    def __init__(self, *args, **kwdargs):
        WidgetMask.__init__(self)
        Gtk.CheckMenuItem.__init__(self, *args, **kwdargs)

    def set_active(self, newval):
        oldval = self.get_active()
        if oldval != newval:
            self.change()

        super(CheckMenuItem, self).set_active(newval)


class SpinButton(WidgetMask, Gtk.SpinButton):
    def __init__(self, *args, **kwdargs):
        WidgetMask.__init__(self)
        Gtk.SpinButton.__init__(self, *args, **kwdargs)

    def set_value(self, newval):
        oldval = self.get_value()
        if oldval != newval:
            self.change()

        super(SpinButton, self).set_value(newval)


class HScale(WidgetMask, Gtk.HScale):
    def __init__(self, *args, **kwdargs):
        WidgetMask.__init__(self)
        Gtk.HScale.__init__(self, *args, **kwdargs)

    def set_value(self, newval):
        oldval = self.get_value()
        if oldval != newval:
            self.change()

        super(HScale, self).set_value(newval)

class VScale(WidgetMask, Gtk.VScale):
    def __init__(self, *args, **kwdargs):
        WidgetMask.__init__(self)
        Gtk.VScale.__init__(self, *args, **kwdargs)

    def set_value(self, newval):
        oldval = self.get_value()
        if oldval != newval:
            self.change()

        super(VScale, self).set_value(newval)


class ComboBoxMixin(object):

    def set_active(self, newval):
        oldval = self.get_active()
        if oldval != newval:
            self.change()

        super(ComboBox, self).set_active(newval)

    def insert_alpha(self, text):
        model = self.get_model()
        tup = (text, )
        j = 0
        for i in range(len(model)):
            j = i
            if model[i][0] > text:
                model.insert(j, tup)
                return
        model.insert(j+1, tup)

    def insert_text(self, idx, text):
        model = self.get_model()
        tup = (text, )
        model.insert(idx, tup)

    def delete_alpha(self, text):
        model = self.get_model()
        for i in range(len(model)):
            if model[i][0] == text:
                del model[i]
                return

    def clear(self):
        model = self.get_model()
        model.clear()

    def show_text(self, text):
        model = self.get_model()
        for i in range(len(model)):
            if model[i][0] == text:
                self.set_active(i)
                return

class ComboBox(WidgetMask, Gtk.ComboBox, ComboBoxMixin):
    def __init__(self, *args, **kwdargs):
        WidgetMask.__init__(self)
        Gtk.ComboBox.__init__(self, *args, **kwdargs)


## class ComboBoxEntry(WidgetMask, Gtk.ComboBoxEntry, ComboBoxMixin):
##     def __init__(self, *args, **kwdargs):
##         WidgetMask.__init__(self)
##         Gtk.ComboBoxEntry.__init__(self, *args, **kwdargs)


class Notebook(WidgetMask, Gtk.Notebook):
    def __init__(self, *args, **kwdargs):
        WidgetMask.__init__(self)
        Gtk.Notebook.__init__(self, *args, **kwdargs)

    def set_group_id(self, id):
        super(Notebook, self).set_group_name(str(id))

    def set_current_page(self, new_idx):
        old_idx = self.get_current_page()
        if old_idx != new_idx:
            self.change()

        super(Notebook, self).set_current_page(new_idx)


class MultiDragDropTreeView(Gtk.TreeView):
    '''TreeView that captures mouse events to make drag and drop work
    properly
    See: https://gist.github.com/kevinmehall/278480#file-multiple-selection-dnd-class-py
    '''

    def __init__(self):
        super(MultiDragDropTreeView, self).__init__()

        self.connect('button_press_event', self.on_button_press)
        self.connect('button_release_event', self.on_button_release)
        self.defer_select = False

    def on_button_press(self, widget, event):
        # Here we intercept mouse clicks on selected items so that we can
        # drag multiple items without the click selecting only one
        target = self.get_path_at_pos(int(event.x), int(event.y))
        if (target
           and event.type == Gdk.EventType.BUTTON_PRESS
           and not (event.state & (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK))
           and self.get_selection().path_is_selected(target[0])):
            # disable selection
            self.get_selection().set_select_function(lambda *ignore: False)
            self.defer_select = target[0]

    def on_button_release(self, widget, event):
        # re-enable selection
        self.get_selection().set_select_function(lambda *ignore: True)

        target = self.get_path_at_pos(int(event.x), int(event.y))
        if (self.defer_select and target
           and self.defer_select == target[0]
           and not (event.x==0 and event.y==0)): # certain drag and drop
            self.set_cursor(target[0], target[1], False)

        self.defer_select=False


class MDISubWindow(Callback.Callbacks):

    def __init__(self, widget, label):
        super(MDISubWindow, self).__init__()

        self.widget = widget

        vbox = Gtk.VBox()
        vbox.set_border_width(4)
        hbox = Gtk.HBox()
        close = Gtk.Button("x")
        maxim = Gtk.Button("^")
        minim = Gtk.Button("v")
        hbox.pack_start(close, False, False, 0)
        hbox.pack_start(minim, False, False, 0)
        hbox.pack_start(maxim, False, False, 0)

        evbox = Gtk.EventBox()
        evbox.add(label)
        evbox.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("gray90"))
        self.label = evbox
        self.evbox = evbox
        hbox.pack_start(evbox, True, True, 2)

        vbox.pack_start(hbox, False, False, 0)
        vbox.pack_start(widget, True, True, 4)

        # what size does the widget want to be?
        rect = widget.get_allocation()
        self.x, self.y, wd, ht = rect.x, rect.y, rect.width, rect.height
        ## wd = widget.get_preferred_width()
        ## ht = widget.get_preferred_height()
        ## wd, ht = widget.get_size_request()
        self.width, self.height = max(wd, 300), max(ht, 300)

        frame = Gtk.EventBox()
        frame.set_size_request(self.width, self.height)
        frame.props.visible_window = True
        frame.set_border_width(0)
        frame.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("gray70"))
        self.frame = frame

        frame.add(vbox)
        frame.show_all()

        for name in ('close', 'maximize', 'minimize'):
            self.enable_callback(name)

        maxim.connect('clicked', lambda *args: self.make_callback('maximize'))
        minim.connect('clicked', lambda *args: self.make_callback('minimize'))
        close.connect('clicked', lambda *args: self.make_callback('close'))


class MDIWidget(Gtk.Layout):
    """
    Multiple Document Interface type widget for Gtk.

    NOTE: *** This is a work in progress! ***
    """
    def __init__(self):
        Gtk.Layout.__init__(self)

        self.children = []
        self.cur_index = -1
        self.selected_child = None
        self.kbdmouse_mask = 0
        self.cascade_offset = 50
        self.minimized_width = 50

        self.connect("motion_notify_event", self.motion_notify_event)
        self.connect("button_press_event", self.button_press_event)
        self.connect("button_release_event", self.button_release_event)
        mask = self.get_events()
        self.set_events(mask
                        | Gdk.EventMask.ENTER_NOTIFY_MASK
                        | Gdk.EventMask.LEAVE_NOTIFY_MASK
                        | Gdk.EventMask.FOCUS_CHANGE_MASK
                        | Gdk.EventMask.STRUCTURE_MASK
                        | Gdk.EventMask.BUTTON_PRESS_MASK
                        | Gdk.EventMask.BUTTON_RELEASE_MASK
                        | Gdk.EventMask.KEY_PRESS_MASK
                        | Gdk.EventMask.KEY_RELEASE_MASK
                        | Gdk.EventMask.POINTER_MOTION_MASK
                        | Gdk.EventMask.POINTER_MOTION_HINT_MASK
                        | Gdk.EventMask.SCROLL_MASK)

        self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse("gray50"))

    def append_page(self, widget, label):

        subwin = MDISubWindow(widget, label)
        self.children.append(subwin)

        subwin.evbox.connect("button_press_event", self.select_child_cb, subwin)
        subwin.frame.connect("button_press_event", self.start_resize_cb, subwin)
        subwin.add_callback('maximize', lambda *args: self.maximize_page(subwin))
        subwin.add_callback('minimize', lambda *args: self.minimize_page(subwin))

        self.put(subwin.frame, self.cascade_offset, self.cascade_offset)

        self.update_subwin_position(subwin)
        self.update_subwin_size(subwin)

        return subwin

    def set_tab_reorderable(self, w, tf):
        pass
    def set_tab_detachable(self, w, tf):
        pass

    def get_tab_label(self, w):
        return None

    def page_num(self, widget):
        index, subwin = self._widget_to_index(widget)
        return index

    def get_nth_page(self, idx):
        if 0 <= idx < len(self.children):
            subwin = self.children[idx]
            return subwin.widget
        return None

    def set_current_page(self, idx):
        subwin = self.children[idx]
        frame = subwin.frame
        #frame.show()
        self.raise_widget(subwin)
        self.cur_index = idx

    def get_current_page(self):
        return self.cur_index

    def _widget_to_index(self, widget):
        index = 0
        for subwin in self.children:
            if subwin.widget == widget:
                return index, subwin
            index += 1
        return -1, None

    def remove_page(self, idx):
        subwin = self.children[idx]
        self.remove(subwin.widget)

    def remove(self, widget):
        idx, subwin = self._widget_to_index(widget)
        if subwin is not None:
            self.children.remove(subwin)
            self.cur_index = -1
            frame = subwin.frame
            super(MDIWidget, self).remove(frame)
            widget.unparent()

    def get_widget_position(self, widget):
        rect = widget.get_allocation()
        x, y, width, height = rect.x, rect.y, rect.width, rect.height
        return x, y

    def get_widget_size(self, widget):
        rect = widget.get_allocation()
        x, y, width, height = rect.x, rect.y, rect.width, rect.height
        return width, height

    def update_subwin_position(self, subwin):
        rect = subwin.frame.get_allocation()
        x, y, wd, ht = rect.x, rect.y, rect.width, rect.height
        subwin.x, subwin.y = x, y

    def update_subwin_size(self, subwin):
        rect = subwin.frame.get_allocation()
        x, y, wd, ht = rect.x, rect.y, rect.width, rect.height
        subwin.width, subwin.height = wd, ht

    def raise_widget(self, subwin):
        frame = subwin.frame
        # Hack to bring widget to the top--no documentation on any other
        # way to accomplish this
        super(MDIWidget, self).remove(frame)
        frame.unparent()
        self.put(frame, subwin.x, subwin.y)

    def select_child_cb(self, layout, event, subwin):
        ex, ey = event.x_root, event.y_root

        x, y = self.get_widget_position(subwin.frame)
        subwin.x, subwin.y = x, y

        # make this the selected widget
        idx = self.page_num(subwin.widget)
        if idx >= 0:
            self.set_current_page(idx)

        self.selected_child = Bunch.Bunch(subwin=subwin, action='move',
                                          x_origin=x, y_origin=y, dx=ex, dy=ey)
        return True

    def start_resize_cb(self, widget, event, subwin):
        self.update_subwin_size(subwin)

        ex, ey = event.x_root, event.y_root
        x, y = self.get_widget_position(subwin.frame)
        subwin.x, subwin.y = x, y

        self.selected_child = Bunch.Bunch(subwin=subwin, action='resize',
                                          x_origin=x, y_origin=y, dx=ex, dy=ey)
        return True

    def button_press_event(self, widget, event):
        x = event.x; y = event.y
        button = self.kbdmouse_mask
        if event.button != 0:
            button |= 0x1 << (event.button - 1)
        return True

    def button_release_event(self, widget, event):
        x = event.x_root; y = event.y_root
        button = self.kbdmouse_mask
        if event.button != 0:
            button |= 0x1 << (event.button - 1)

        if self.selected_child is not None:
            bnch = self.selected_child
            subwin = bnch.subwin
            if bnch.action == 'move':
                x = int(subwin.x + (x - bnch.dx))
                y = int(subwin.y + (y - bnch.dy))
                self.move_page(subwin, x, y)

            elif bnch.action == 'resize':
                wd = int(subwin.width + (x - bnch.dx))
                ht = int(subwin.height + (y - bnch.dy))
                self.resize_page(subwin, wd, ht)

            self.selected_child = None
        return True

    def motion_notify_event(self, widget, event):
        button = self.kbdmouse_mask
        x, y, state = event.x_root, event.y_root, event.state

        if state & Gdk.ModifierType.BUTTON1_MASK:
            button |= 0x1
        elif state & Gdk.ModifierType.BUTTON2_MASK:
            button |= 0x2
        elif state & Gdk.ModifierType.BUTTON3_MASK:
            button |= 0x4

        if (button & 0x1) and (self.selected_child is not None):
            bnch = self.selected_child
            subwin = bnch.subwin
            if bnch.action == 'move':
                x = int(subwin.x + (x - bnch.dx))
                y = int(subwin.y + (y - bnch.dy))
                # this works better if it is not self.move_page()
                self.move(subwin.frame, x, y)

            elif bnch.action == 'resize':
                wd = int(subwin.width + (x - bnch.dx))
                ht = int(subwin.height + (y - bnch.dy))
                # this works better if it is not self.resize_page()
                subwin.frame.set_size_request(wd, ht)

        return True

    def tile_pages(self):
        # calculate number of rows and cols, try to maintain a square
        # TODO: take into account the window geometry
        num_widgets = len(self.children)
        rows = int(round(math.sqrt(num_widgets)))
        cols = rows
        if rows**2 < num_widgets:
            cols += 1

        # find out how big each window should be
        rect = self.get_allocation()
        _x, _y, width, height = rect.x, rect.y, rect.width, rect.height
        wd, ht = width // cols, height // rows

        # and move and resize them into place
        for i in range(0, rows):
            for j in range(0, cols):
                index = i*cols + j
                if index < num_widgets:
                    subwin = self.children[index]

                    self.resize_page(subwin, wd, ht)

                    x, y = j * wd, i * ht
                    self.move_page(subwin, x, y)

                    self.raise_widget(subwin)

    def cascade_pages(self):
        x, y = 0, 0
        for subwin in self.children:
            self.move_page(subwin, x, y)
            self.raise_widget(subwin)
            x += self.cascade_offset
            y += self.cascade_offset

    def use_tabs(self, tf):
        pass

    def move_page(self, subwin, x, y):
        self.move(subwin.frame, x, y)
        subwin.x, subwin.y = x, y

    def resize_page(self, subwin, wd, ht):
        subwin.frame.set_size_request(wd, ht)
        subwin.width, subwin.height = wd, ht

    def maximize_page(self, subwin):
        rect = self.get_allocation()
        x, y, wd, ht = rect.x, rect.y, rect.width, rect.height

        self.raise_widget(subwin)
        self.resize_page(subwin, wd, ht)
        self.move_page(subwin, 0, 0)

    def minimize_page(self, subwin):
        rect = self.get_allocation()
        _x, _y, width, height = rect.x, rect.y, rect.width, rect.height

        rect = subwin.frame.get_allocation()
        x, y, wd, ht = rect.x, rect.y, rect.width, rect.height

        rect = subwin.label.get_allocation()
        _x, _y, wd, ht = rect.x, rect.y, rect.width, rect.height

        self.resize_page(subwin, self.minimized_width, ht)
        self.move_page(subwin, x, height-ht)
        #self.lower_widget(subwin)

    def close_page(self, subwin):
        pass


class FileSelection(object):

    def __init__(self, parent_w, action=Gtk.FileChooserAction.OPEN,
                 title="Select a file"):
        self.parent = parent_w
        # Create a new file selection widget
        self.filew = Gtk.FileChooserDialog(title=title, action=action)
        self.filew.connect("destroy", self.close)
        if action == Gtk.FileChooserAction.SAVE:
            self.filew.add_buttons(Gtk.STOCK_SAVE, 1, Gtk.STOCK_CANCEL, 0)
        else:
            self.filew.add_buttons(Gtk.STOCK_OPEN, 1, Gtk.STOCK_CANCEL, 0)
        self.filew.set_default_response(1)
        self.filew.connect("response", self.file_ok_sel)

        # Connect the cancel_button to destroy the widget
        #self.filew.cancel_button.connect("clicked", self.close)

    def popup(self, title, callfn, initialdir=None, filename=None):
        """Let user select and load file."""
        self.cb = callfn
        self.filew.set_title(title)
        if initialdir:
            self.filew.set_current_folder(initialdir)

        if filename:
            #self.filew.set_filename(filename)
            self.filew.set_current_name(filename)

        self.filew.show()

    # Get the selected filename
    def file_ok_sel(self, w, rsp):
        self.close(w)
        if rsp == 0:
            return

        filepath = self.filew.get_filename()
        self.cb(filepath)

    def close(self, widget):
        self.filew.hide()


class DirectorySelection(FileSelection):
    """Handle directory selection dialog."""
    def __init__(self, parent_w):
        super(DirectorySelection, self).__init__(
            parent_w, action=Gtk.FileChooserAction.SELECT_FOLDER,
            title="Select a directory")

    def popup(self, title, callfn, initialdir=None):
        """Let user select a directory."""
        super(DirectorySelection, self).popup(title, callfn, initialdir)


class Timer(Callback.Callbacks):
    """Abstraction of a GUI-toolkit implemented timer."""

    def __init__(self, duration=0.0):
        """Create a timer set to expire after `duration` sec.
        """
        super(Timer, self).__init__()

        self.duration = duration
        # For storing aritrary data with timers
        self.data = Bunch.Bunch()

        self._timer = None

        for name in ('expired', 'canceled'):
            self.enable_callback(name)

    def start(self, duration=None):
        """Start the timer.  If `duration` is not None, it should
        specify the time to expiration in seconds.
        """
        if duration is None:
            duration = self.duration

        self.set(duration)

    def set(self, duration):

        self.stop()

        # Gtk timer set in milliseconds
        time_ms = int(duration * 1000.0)
        self._timer = GObject.timeout_add(time_ms, self._redirect_cb)

    def _redirect_cb(self):
        self._timer = None
        self.make_callback('expired')

    def stop(self):
        try:
            if self._timer is not None:
                GObject.source_remove(self._timer)
                self._timer = None
        except:
            pass

    def cancel(self):
        """Cancel this timer.  If the timer is not running, there
        is no error.
        """
        self.stop()
        self.make_callback('canceled')

    clear = cancel


def combo_box_new_text():
    liststore = Gtk.ListStore(GObject.TYPE_STRING)
    combobox = ComboBox()
    combobox.set_model(liststore)
    cell = Gtk.CellRendererText()
    combobox.pack_start(cell, True)
    combobox.add_attribute(cell, 'text', 0)
    return combobox

def get_scroll_info(event):
    """
    Returns the (degrees, direction) of a scroll motion Gtk event.
    """
    valid, dx, dy = event.get_scroll_deltas()
    if valid:
        # we have a trackpad or some device that reports pixel deltas
        delta = math.sqrt(dx ** 2 + dy ** 2)
        if dy < 0:
            delta = -delta

        ang_rad = math.atan2(dy, dx)
        direction = math.degrees(ang_rad) - 90.0
        direction = math.fmod(direction + 360.0, 360.0)

        # TODO: is this accurate?--NOT TESTED
        num_degrees = delta / 8.0

    else:
        valid, direction = event.get_scroll_direction()
        if valid:
            if event.direction == Gdk.ScrollDirection.UP:
                direction = 0.0
            elif event.direction == Gdk.ScrollDirection.DOWN:
                direction = 180.0
            elif event.direction == Gdk.ScrollDirection.LEFT:
                direction = 270.0
            elif event.direction == Gdk.ScrollDirection.RIGHT:
                direction = 90.0

        else:
            direction = None

        # TODO: does Gtk encode the amount of scroll?
        # 15 deg is standard 1-click turn for a wheel mouse
        num_degrees = 15.0

    return (num_degrees, direction)

def get_icon(iconpath, size=None):
    if size is not None:
        wd, ht = size
    else:
        wd, ht = 24, 24
    pixbuf = pixbuf_new_from_file_at_size(iconpath, wd, ht)
    return pixbuf

def get_font(font_family, point_size):
    font = Pango.FontDescription('%s %d' % (font_family, point_size))
    return font

def pixbuf_new_from_xpm_data(xpm_data):
    xpm_data = bytes('\n'.join(xpm_data))
    return GdkPixbuf.Pixbuf.new_from_xpm_data(xpm_data)

def pixbuf_new_from_array(data, rgbtype, bpp):
    # NOTE: there is a bug in gtk3 with pixbuf_new_from_array()
    # See: http://stackoverflow.com/questions/24062779/how-to-correctly-covert-3d-array-into-continguous-rgb-bytes/24070152#24070152
    #return GdkPixbuf.Pixbuf.new_from_array(data, rgbtype, bpp)

    height, width, depth = data.shape
    pixl = GdkPixbuf.PixbufLoader.new_with_type('pnm')
    # P6 is the magic number of PNM format,
    # and 255 is the max color allowed
    pixl.write((b"P6 %d %d 255 " % (width, height)) + data.tobytes(order='C'))
    pix = pixl.get_pixbuf()
    pixl.close()
    return pix

def pixbuf_new_from_data(rgb_buf, rgbtype, hasAlpha, bpp, dawd, daht, stride):
    return GdkPixbuf.Pixbuf.new_from_data(rgb_buf, rgbtype, hasAlpha, bpp,
                                          dawd, daht, stride, None, None)

def pixbuf_new_from_file_at_size(foldericon, width, height):
    return GdkPixbuf.Pixbuf.new_from_file_at_size(foldericon,
                                                  width, height)

def make_cursor(widget, iconpath, x, y):
    image = Gtk.Image()
    image.set_from_file(iconpath)
    pixbuf = image.get_pixbuf()
    screen = widget.get_screen()
    display = screen.get_display()
    return Gdk.Cursor(display, pixbuf, x, y)

def set_default_style():
    style_provider = Gtk.CssProvider()

    module_home = os.path.split(sys.modules[__name__].__file__)[0]
    gtk_css = os.path.join(module_home, 'gtk_css')
    with open(gtk_css, 'rb') as css_f:
        css_data = css_f.read()

    style_provider.load_from_data(css_data)

    Gtk.StyleContext.add_provider_for_screen(
        Gdk.Screen.get_default(), style_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

#END
