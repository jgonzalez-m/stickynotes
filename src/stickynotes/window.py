# window.py
#
# Copyright 2025 jorge gonzalez m
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib, Gdk, Pango
from .note import StickyNote
import json
from datetime import datetime

@Gtk.Template(resource_path='/org/gnome/StickyNotes/stickynotes/window.ui')
class StickyNotesWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'StickyNotesWindow'
    
    search_entry = Gtk.Template.Child()
    notes_grid = Gtk.Template.Child()
    empty_state_box = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        self.notes = {}
        self.note_previews = {}
        
        self.setup_actions()
        self.setup_search()
        
        self.notes_grid.set_valign(Gtk.Align.START)
        self.notes_grid.set_halign(Gtk.Align.FILL)
        self.notes_grid.set_hexpand(True)
        self.notes_grid.set_vexpand(True)
        self.notes_grid.set_homogeneous(True)
        self.notes_grid.set_selection_mode(Gtk.SelectionMode.NONE)
        
        self.empty_state_box.set_valign(Gtk.Align.CENTER)
        self.empty_state_box.set_visible(True)
        
        GLib.idle_add(self.load_notes)
        self.present()

    def load_notes(self):
        app = self.get_application()
        if not app:
            print("No application found")
            return False
        
        print("\n=== Loading notes in main window ===")
        
        stored_notes = app.notes
        active_notes = app.get_notes()
        
        print(f"Found {len(stored_notes)} stored notes and {len(active_notes)} active notes")
        
        child = self.notes_grid.get_first_child()
        while child:
            next_child = child.get_next_sibling()
            self.notes_grid.remove(child)
            child = next_child
        self.note_previews.clear()
        self.notes.clear()
        
        processed_notes = {}
        
        for note_id, note in active_notes.items():
            print(f"Processing active note: {note_id}")
            processed_notes[note_id] = note
            
            preview = NotePreviewCard(note)
            preview.connect('activate', self.on_note_preview_activated)
            self.notes_grid.append(preview)
            self.note_previews[note_id] = preview
            self.notes[note_id] = note
        
        for note_id, note_data in stored_notes.items():
            if note_id not in processed_notes:
                print(f"Processing stored note: {note_id}")
                note = StickyNote(app, note_data)
                note.set_visible(False)
                
                preview = NotePreviewCard(note)
                preview.connect('activate', self.on_note_preview_activated)
                self.notes_grid.append(preview)
                self.note_previews[note_id] = preview
                self.notes[note_id] = note
        
        notes_exist = bool(self.notes)
        print(f"Notes exist: {notes_exist}")
        
        self.empty_state_box.set_visible(not notes_exist)
        self.notes_grid.get_parent().set_visible(notes_exist)
        self.notes_grid.set_visible(notes_exist)
        
        if notes_exist:
            print("Making sure all previews are visible")
            self.notes_grid.show()
            child = self.notes_grid.get_first_child()
            while child:
                child.set_visible(True)
                child.show()
                child = child.get_next_sibling()
        
        self.debug_grid_state()
        return False

    def setup_actions(self):
        new_note_action = Gio.SimpleAction.new('new-note', None)
        new_note_action.connect('activate', self.on_new_note)
        self.add_action(new_note_action)
        
        toggle_action = Gio.SimpleAction.new('toggle-window', None)
        toggle_action.connect('activate', self.on_toggle_window)
        self.add_action(toggle_action)

    def setup_search(self):
        self.search_entry.connect('search-changed', self.on_search_changed)

    def on_search_changed(self, search_entry):
        search_text = search_entry.get_text().lower()
        self.filter_notes(search_text)

    def filter_notes(self, search_text):
        has_visible_notes = False
        
        if not search_text:
            for preview in self.note_previews.values():
                preview.set_visible(True)
                has_visible_notes = True
        else:
            for note_id, note in self.notes.items():
                if note_id in self.note_previews:
                    preview = self.note_previews[note_id]
                    note_data = note.save_note()
                    content = note_data.get('content', '').lower()
                    
                    visible = search_text in content
                    preview.set_visible(visible)
                    if visible:
                        has_visible_notes = True
        
        self.empty_state_box.set_visible(not has_visible_notes)
        self.notes_grid.set_visible(has_visible_notes)

    def update_notes_grid(self):
        app = self.get_application()
        if not app:
            print("No application found")
            return False
        
        print("Updating notes grid")
        
        active_notes = app.get_notes()
        stored_notes = app.notes
        
        notes_to_remove = []
        for note_id in self.note_previews:
            if note_id not in stored_notes and note_id not in active_notes:
                notes_to_remove.append(note_id)
        
        for note_id in notes_to_remove:
            preview = self.note_previews[note_id]
            if preview.get_parent():
                self.notes_grid.remove(preview)
            del self.note_previews[note_id]
            if note_id in self.notes:
                del self.notes[note_id]
            print(f"Removed note {note_id} from grid")
        
        for note_id, note_data in stored_notes.items():
            if note_id in active_notes:
                note = active_notes[note_id]
            else:
                note = StickyNote(app, note_data)
            
            self.notes[note_id] = note
            
            if note_id in self.note_previews:
                note_data = note.save_note()
                self.note_previews[note_id].update_preview(note_data)
                print(f"Updated preview for note {note_id}")
            else:
                preview = NotePreviewCard(note)
                preview.connect('activate', self.on_note_preview_activated)
                preview.set_visible(True)
                self.notes_grid.append(preview)
                self.note_previews[note_id] = preview
                print(f"Added new preview for note {note_id}")
        
        if self.notes:
            self.empty_state_box.set_visible(False)
            self.notes_grid.set_visible(True)
            child = self.notes_grid.get_first_child()
            while child:
                child.show()
                child = child.get_next_sibling()
        else:
            self.empty_state_box.set_visible(True)
            self.notes_grid.set_visible(False)
        
        if self.search_entry.get_text():
            self.filter_notes(self.search_entry.get_text().lower())
        
        return False

    def on_note_preview_activated(self, preview):
        note_id = preview.note_id
        if note_id in self.notes:
            note = self.notes[note_id]
            note.present()
            print(f"Presenting note {note_id}")

    def add_note(self, note):
        # Agregar la nota al diccionario de notas
        self.notes[note.note_id] = note
        
        # Crear y agregar el preview
        preview = NotePreviewCard(note)
        preview.connect('activate', self.on_note_preview_activated)
        preview.set_visible(True)
        self.notes_grid.append(preview)
        self.note_previews[note.note_id] = preview
        
        # Actualizar visibilidad
        self.empty_state_box.set_visible(False)
        self.notes_grid.set_visible(True)
        
        # Si hay texto en la búsqueda, aplicar el filtro
        if self.search_entry.get_text():
            self.filter_notes(self.search_entry.get_text().lower())

    def on_new_note(self, action, parameter):
        app = self.get_application()
        note = app.create_new_note()
        if note:
            self.add_note(note)

    def on_toggle_window(self, action, parameter):
        if self.is_visible():
            self.hide()
        else:
            self.update_notes_grid()
            self.present()

    def debug_grid_state(self):
        print("\nGrid State Debug:")
        print(f"Grid visible: {self.notes_grid.get_visible()}")
        print(f"Empty state visible: {self.empty_state_box.get_visible()}")
        print(f"Number of notes: {len(self.notes)}")
        print(f"Number of previews: {len(self.note_previews)}")
        print("Grid children:")
        child = self.notes_grid.get_first_child()
        while child:
            print(f"  - Child visible: {child.get_visible()}")
            child = child.get_next_sibling()

class NotePreviewCard(Gtk.FlowBoxChild):
    _base_css_applied = False
    _color_css_provider = None
    _color_styles = {
        'yellow': '#ffeb3b',
        'pink': '#f8d7da',
        'blue': '#cce5ff',
        'green': '#d1ecf1',
        'orange': '#ffe8cc',
        'purple': '#e2d5f1'
    }
    
    def __init__(self, note):
        Gtk.FlowBoxChild.__init__(self)
        self.note = note
        self.note_id = note.note_id
        
        self.set_visible(True)
        self.set_can_focus(True)
        
        self.setup_ui()
        
        self.update_from_note(note)
        
        click = Gtk.GestureClick.new()
        click.connect('pressed', self.on_click_pressed)
        self.add_controller(click)
        
        self.show()

    def on_click_pressed(self, gesture, n_press, x, y):
        self.activate()

    def setup_ui(self):
        self.card = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.card.set_size_request(200, 150)
        self.card.add_css_class('card')
        self.card.set_margin_top(6)
        self.card.set_margin_bottom(6)
        self.card.set_margin_start(6)
        self.card.set_margin_end(6)
        
        self.set_size_request(220, 170)
        self.set_visible(True)
        self.set_hexpand(True)
        
        self.title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.title_box.set_margin_top(8)
        self.title_box.set_margin_bottom(4)
        self.title_box.set_margin_start(8)
        self.title_box.set_margin_end(8)
        
        self.date_label = Gtk.Label()
        self.date_label.set_halign(Gtk.Align.START)
        self.date_label.set_hexpand(True)
        self.date_label.add_css_class('caption')
        self.date_label.add_css_class('dim-label')
        
        self.color_indicator = Gtk.Box()
        self.color_indicator.set_size_request(16, 16)
        self.color_indicator.add_css_class('color-indicator')
        
        self.title_box.append(self.date_label)
        self.title_box.append(self.color_indicator)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        
        self.content_label = Gtk.Label()
        self.content_label.set_halign(Gtk.Align.START)
        self.content_label.set_valign(Gtk.Align.START)
        self.content_label.set_hexpand(True)
        self.content_label.set_vexpand(True)
        self.content_label.set_margin_start(8)
        self.content_label.set_margin_end(8)
        self.content_label.set_margin_bottom(8)
        self.content_label.set_max_width_chars(25)
        self.content_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.content_label.set_lines(6)
        self.content_label.set_wrap(True)
        self.content_label.set_wrap_mode(Pango.WrapMode.WORD)
        self.content_label.set_xalign(0)
        self.content_label.set_yalign(0)
        
        scrolled.set_child(self.content_label)
        
        self.card.append(self.title_box)
        self.card.append(scrolled)
        
        self.set_child(self.card)
        
        self.card.set_visible(True)
        self.title_box.set_visible(True)
        self.content_label.set_visible(True)
        
        self.apply_preview_css()

    def apply_preview_css(self):
        if not NotePreviewCard._base_css_applied:
            css = """
            .card {
                border-radius: 12px;
                border: 1px solid rgba(0,0,0,0.1);
                transition: all 200ms ease;
                background-color: #ffffff;
                padding: 6px;
            }
            
            .card:hover {
                box-shadow: 0 2px 6px rgba(0,0,0,0.15);
                transform: translateY(-2px);
            }
            
            .color-indicator {
                border-radius: 50%;
                min-width: 12px;
                min-height: 12px;
                margin: 2px;
                border: 1px solid rgba(0,0,0,0.1);
            }
            """
            
            for color, value in self._color_styles.items():
                css += f"""
                .color-indicator.{color} {{
                    background-color: {value};
                }}
                """
            
            try:
                css_provider = Gtk.CssProvider()
                css_provider.load_from_data(css.encode('utf-8'))
                Gtk.StyleContext.add_provider_for_display(
                    Gdk.Display.get_default(),
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
                NotePreviewCard._base_css_applied = True
            except Exception as e:
                print(f"Error applying base CSS: {e}")

    def update_preview(self, note_data):
        """Update the preview card with the given note data"""
        content = note_data.get('content', '')
        color = note_data.get('color', 'yellow')
        timestamp = note_data.get('timestamp')
        
        if content:
            preview_text = '\n'.join(content.split('\n')[:6])
            if len(preview_text) > 150:
                preview_text = preview_text[:147] + '...'
            self.content_label.set_text(preview_text)
        else:
            self.content_label.set_text("(Nota vacía)")
        
        if timestamp:
            try:
                dt = datetime.fromisoformat(timestamp)
                date_str = dt.strftime("%d/%m/%Y")
                self.date_label.set_text(date_str)
            except:
                self.date_label.set_text("")
        
        for c in self._color_styles.keys():
            self.color_indicator.remove_css_class(c)
        self.color_indicator.add_css_class('color-indicator')
        self.color_indicator.add_css_class(color)
        
        self.show()
        self.card.show()
        self.title_box.show()
        self.content_label.show()
        self.color_indicator.show()

    def update_from_note(self, note):
        """Update preview directly from note state without calling save_note()
        This prevents infinite recursion between update_from_note and save_note"""
        buffer = note.text_view.get_buffer()
        content = buffer.get_text(
            buffer.get_start_iter(),
            buffer.get_end_iter(),
            False
        )
        
        note_data = {
            'content': content,
            'color': note.color,
            'timestamp': datetime.now().isoformat()
        }
        
        # Directly call update_preview with the data to avoid calling save_note()
        self.update_preview(note_data)
