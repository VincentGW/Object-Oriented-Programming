#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
GIMP 3.0 Color History Viewer Plugin
Shows last 10 colors in a floating window
Left click = set FG, Right click = set BG
"""

import gi
gi.require_version('Gimp', '3.0')
from gi.repository import Gimp
gi.require_version('GimpUi', '3.0')
from gi.repository import GimpUi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
gi.require_version('Gdk', '3.0')
from gi.repository import Gdk
from gi.repository import GObject
from gi.repository import GLib
import sys
import os
import tempfile

STATE_FILE = os.path.join(tempfile.gettempdir(), 'gimp-color-history-viewer.state')
SIGNAL_FILE = os.path.join(tempfile.gettempdir(), 'gimp-color-history-viewer.signal')

class ColorHistoryViewer(Gimp.PlugIn):
    """GIMP plugin for viewing color history"""

    def do_set_i18n(self, procname):
        return False

    def do_query_procedures(self):
        return ['python-fu-color-history-viewer']

    def do_create_procedure(self, name):
        procedure = Gimp.Procedure.new(self, name,
                                       Gimp.PDBProcType.PLUGIN,
                                       self.run, None)
        procedure.set_menu_label("Color History Viewer")
        procedure.set_documentation(
            "Toggle color history viewer window",
            "Displays a floating window with your last 10 colors. "
            "Left click sets foreground, right click sets background.",
            "")
        procedure.set_attribution("Assistant", "Assistant", "2026")
        procedure.add_menu_path('<Image>/Colors/')

        procedure.add_enum_argument("run-mode", "Run mode",
                                   "The run mode", Gimp.RunMode,
                                   Gimp.RunMode.INTERACTIVE,
                                   GObject.ParamFlags.READWRITE)

        return procedure

    def run(self, procedure, config, data):
        """Toggle dialog visibility"""
        Gimp.message("Plugin run() called")
        GimpUi.init("color-history-viewer.py")

        # Check if another instance is already running
        if os.path.exists(STATE_FILE):
            # Check if the state file is stale (older than 2 seconds with no signal response)
            import time
            file_age = time.time() - os.path.getmtime(STATE_FILE)
            if file_age > 2 and not os.path.exists(SIGNAL_FILE):
                # Stale state file - remove it and start fresh
                Gimp.message("State file is stale - removing and starting fresh")
                try:
                    os.remove(STATE_FILE)
                except:
                    pass
            else:
                # Signal the running instance to toggle
                Gimp.message("State file exists - sending toggle signal")
                with open(SIGNAL_FILE, 'w') as f:
                    f.write('toggle')
                return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())

        # First instance - create state file and run
        Gimp.message("First instance - creating window")
        with open(STATE_FILE, 'w') as f:
            f.write('running')

        try:
            Gimp.message("About to create ColorHistoryWindow")
            window = ColorHistoryWindow()
            Gimp.message("Window created, calling show_all()")
            window.show_all()
            Gimp.message("show_all() called, entering Gtk.main()")
            Gtk.main()
            Gimp.message("Gtk.main() exited")
        except Exception as e:
            Gimp.message(f"Exception in run(): {e}")
            import traceback
            Gimp.message(traceback.format_exc())
        finally:
            # Clean up state file when exiting
            if os.path.exists(STATE_FILE):
                os.remove(STATE_FILE)

        return procedure.new_return_values(Gimp.PDBStatusType.SUCCESS, GLib.Error())


class ColorHistoryWindow(Gtk.Window):
    """Floating window showing color history"""

    def __init__(self):
        super().__init__(title="Color History")

        Gimp.message("Window created")

        # Configure window
        self.set_type_hint(Gdk.WindowTypeHint.UTILITY)
        self.set_keep_above(True)
        self.set_border_width(5)
        self.set_default_size(520, 60)
        self.set_resizable(False)
        self.set_deletable(False)
        self.set_destroy_with_parent(False)

        Gimp.message("Window configured, about to set_decorated(False)")

        # Remove decorations
        self.set_decorated(False)

        Gimp.message(f"set_decorated(False) called. Decorated = {self.get_decorated()}")

        self.is_visible = True

        # Don't destroy on close
        self.connect("delete-event", lambda w, e: True)

        Gimp.message("Window initialization complete")

        # Initialize color tracking
        self.color_list = []
        try:
            fg = Gimp.context_get_foreground()
            bg = Gimp.context_get_background()
            self.color_list.append(self.copy_color(fg))
            if not self.colors_equal(fg, bg):
                self.color_list.append(self.copy_color(bg))
            self.last_fg = self.copy_color(fg)
        except Exception as e:
            from gi.repository import Gegl
            black = Gegl.Color.new("black")
            self.color_list.append(black)
            self.last_fg = black

        # Create UI - vertical box with drag handle at top
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)

        # Add a small drag handle bar at the top
        drag_handle = Gtk.EventBox()
        drag_handle.set_size_request(-1, 25)

        # Horizontal box for drag handle content
        drag_hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        drag_handle.add(drag_hbox)

        # Label on the left
        drag_handle_label = Gtk.Label(label="Color History Display")
        drag_handle_label.set_markup('<i><span foreground="#CCCCCC">Color History Display</span></i>')
        drag_handle_label.set_halign(Gtk.Align.START)
        drag_hbox.pack_start(drag_handle_label, True, True, 5)

        # Row indicator dots on the right
        self.dots_area = Gtk.DrawingArea()
        self.dots_area.set_size_request(90, 25)
        self.dots_area.connect("draw", self.draw_row_dots)
        drag_hbox.pack_end(self.dots_area, False, False, 5)

        # Style the drag handle
        drag_handle.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(0.3, 0.3, 0.3, 1.0))
        vbox.pack_start(drag_handle, False, False, 0)

        # Connect drag events to the handle
        drag_handle.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.POINTER_MOTION_MASK)
        drag_handle.connect("button-press-event", self.on_drag_start)
        drag_handle.connect("motion-notify-event", self.on_drag_motion)
        drag_handle.connect("button-release-event", self.on_drag_end)

        self.drag_offset_x = 0
        self.drag_offset_y = 0
        self.dragging = False

        # Scrolling state - track which row we're showing (0-4)
        self.current_row = 0

        # Color squares container - grid layout
        grid = Gtk.Grid()
        grid.set_column_spacing(3)
        grid.set_row_spacing(3)
        grid.set_border_width(3)
        vbox.pack_start(grid, True, True, 0)

        # Add scroll event to the grid
        grid.add_events(Gdk.EventMask.SCROLL_MASK)
        grid.connect("scroll-event", self.on_scroll)

        # Create 10 color squares (showing 1 row at a time, but we have 5 rows total = 50 colors)
        self.color_buttons = []

        for i in range(10):
            event_box = Gtk.EventBox()
            event_box.connect("button-press-event", self.on_color_clicked, i)
            event_box.add_events(Gdk.EventMask.SCROLL_MASK)
            event_box.connect("scroll-event", self.on_scroll)

            drawing_area = Gtk.DrawingArea()
            drawing_area.set_size_request(48, 48)
            drawing_area.connect("draw", self.draw_color_square, i)

            event_box.add(drawing_area)
            grid.attach(event_box, i, 0, 1, 1)

            self.color_buttons.append(drawing_area)

        # Update colors periodically
        GLib.timeout_add(500, self.update_colors)

        # Check for toggle signal every 200ms
        GLib.timeout_add(200, self.check_signal)

    def check_signal(self):
        """Check if we should toggle visibility"""
        # Touch the state file to keep it fresh
        try:
            if os.path.exists(STATE_FILE):
                import time
                os.utime(STATE_FILE, None)
        except:
            pass

        # Check for toggle signal
        if os.path.exists(SIGNAL_FILE):
            try:
                os.remove(SIGNAL_FILE)
                # Toggle visibility
                if self.is_visible:
                    self.hide()
                    self.is_visible = False
                else:
                    self.show_all()
                    self.is_visible = True
            except:
                pass
        return True  # Keep checking

    def copy_color(self, color):
        """Create a copy of a color"""
        return color.duplicate()

    def draw_row_dots(self, widget, cr):
        """Draw 5 dots indicating which row is active"""
        allocation = widget.get_allocation()
        height = allocation.height

        # Draw 5 dots vertically centered
        dot_radius = 5
        spacing = 18
        start_x = 8
        center_y = height / 2

        for i in range(5):
            x = start_x + (i * spacing)

            # Active row is darker, others are medium grey
            if i == self.current_row:
                cr.set_source_rgb(0.25, 0.25, 0.25)  # Dark grey for active
            else:
                cr.set_source_rgb(0.45, 0.45, 0.45)  # Medium grey for inactive

            cr.arc(x, center_y, dot_radius, 0, 2 * 3.14159)
            cr.fill()

    def on_scroll(self, widget, event):
        """Handle scroll wheel to change rows"""
        if event.direction == Gdk.ScrollDirection.UP:
            # Scroll up - go to previous row (earlier in history)
            if self.current_row > 0:
                self.current_row -= 1
                self.redraw_all()
        elif event.direction == Gdk.ScrollDirection.DOWN:
            # Scroll down - go to next row (later in history)
            if self.current_row < 4:
                self.current_row += 1
                self.redraw_all()
        return True

    def redraw_all(self):
        """Redraw all color squares and row indicator"""
        for button in self.color_buttons:
            button.queue_draw()
        self.dots_area.queue_draw()

    def draw_color_square(self, widget, cr, index):
        """Draw a color square"""
        allocation = widget.get_allocation()
        width = allocation.width
        height = allocation.height

        # Calculate actual index in color_list based on current row
        actual_index = (self.current_row * 10) + index

        # Check if this is an empty slot
        is_empty = actual_index >= len(self.color_list)

        if not is_empty:
            # Draw the color
            color = self.color_list[actual_index]
            try:
                from gi.repository import Babl
                rgb_format = Babl.format("R'G'B' u8")
                pixel = color.get_pixel(rgb_format)
                r = pixel[0] / 255.0
                g = pixel[1] / 255.0
                b = pixel[2] / 255.0
            except:
                rgba = color.get_rgba()
                def linear_to_srgb(c):
                    if c <= 0.0031308:
                        return c * 12.92
                    else:
                        return 1.055 * (c ** (1.0/2.4)) - 0.055
                r = linear_to_srgb(rgba.red)
                g = linear_to_srgb(rgba.green)
                b = linear_to_srgb(rgba.blue)

            cr.set_source_rgb(r, g, b)
            cr.rectangle(0, 0, width, height)
            cr.fill()
        else:
            # Draw checkered pattern for empty slots
            checker_size = 4
            for y in range(0, int(height), checker_size):
                for x in range(0, int(width), checker_size):
                    if ((x // checker_size) + (y // checker_size)) % 2 == 0:
                        cr.set_source_rgb(0.8, 0.8, 0.8)
                    else:
                        cr.set_source_rgb(0.6, 0.6, 0.6)
                    cr.rectangle(x, y, checker_size, checker_size)
                    cr.fill()

        # Draw black border around each square
        cr.set_source_rgb(0, 0, 0)
        cr.set_line_width(1)
        cr.rectangle(0.5, 0.5, width - 1, height - 1)
        cr.stroke()

    def on_drag_start(self, widget, event):
        """Start dragging the window"""
        if event.button == 1:  # Left mouse button to drag the handle
            self.dragging = True
            self.drag_offset_x = event.x_root - self.get_position()[0]
            self.drag_offset_y = event.y_root - self.get_position()[1]
            return True
        return False

    def on_drag_motion(self, widget, event):
        """Drag the window"""
        if self.dragging:
            new_x = int(event.x_root - self.drag_offset_x)
            new_y = int(event.y_root - self.drag_offset_y)
            self.move(new_x, new_y)
            return True
        return False

    def on_drag_end(self, widget, event):
        """Stop dragging the window"""
        if event.button == 1:
            self.dragging = False
            return True
        return False

    def on_color_clicked(self, widget, event, index):
        """Handle color click - left = FG, right = BG"""
        # Calculate actual index based on current row
        actual_index = (self.current_row * 10) + index

        if actual_index >= len(self.color_list):
            return True

        color = self.color_list[actual_index]

        if event.button == 1:
            Gimp.context_set_foreground(color)
        elif event.button == 3:
            Gimp.context_set_background(color)

        return True

    def update_colors(self):
        """Update color history from GIMP"""
        try:
            current_fg = Gimp.context_get_foreground()
            if not self.colors_equal(current_fg, self.last_fg):
                new_color = self.copy_color(current_fg)
                self.color_list = [c for c in self.color_list if not self.colors_equal(c, new_color)]
                self.color_list.insert(0, new_color)
                self.color_list = self.color_list[:50]  # Keep max 50 colors (5 rows)
                self.last_fg = new_color

                # Redraw if on first row (to show new color immediately)
                if self.current_row == 0:
                    for button in self.color_buttons:
                        button.queue_draw()
        except:
            pass

        return True

    def colors_equal(self, color1, color2):
        """Compare two colors"""
        rgb1 = color1.get_rgba()
        rgb2 = color2.get_rgba()
        return (abs(rgb1.red - rgb2.red) < 0.001 and
                abs(rgb1.green - rgb2.green) < 0.001 and
                abs(rgb1.blue - rgb2.blue) < 0.001)


Gimp.main(ColorHistoryViewer.__gtype__, sys.argv)
