# main.py
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

# src/main.py
#!/usr/bin/env python3

# src/main.py
#!/usr/bin/env python3

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib
import sys
import json
import os

# Verify resources are available before importing template classes
try:
    # Check if the resource bundle is already registered
    resources = Gio.resources_enumerate_children('/org/gnome/StickyNotes/', Gio.ResourceLookupFlags.NONE)
    if not resources:
        print("ERROR: Resources not registered. Make sure to run through the launcher script.")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: Resources not available: {e}")
    print("Make sure to run through the launcher script that loads resources.")
    sys.exit(1)

from .window import StickyNotesWindow, StickyNote

class StickyNotesApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='org.gnome.StickyNotes')
        self.notes = {}
        self.main_window = None
        self.data_file = os.path.expanduser('~/.local/share/sticky-notes.json')
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        
        # Cargar datos
        self.load_notes_data()
    
    def do_activate(self):
        # Create main window if it doesn't exist
        if not self.main_window:
            self.main_window = StickyNotesWindow(application=self)
        
        # Print debug information
        self.debug_note_state()
        
        # Create a list to store restored notes
        restored_notes = []
        
        # Restore existing notes or create a new one
        if not self.notes:
            print("No stored notes found, creating new note")
            note = self.create_new_note()
            restored_notes.append(note)
        else:
            print(f"Restoring {len(self.notes)} notes")
            # Restore notes that aren't already open
            active_notes = self.get_notes()
            for note_id, note_data in self.notes.items():
                if note_id not in active_notes:
                    print(f"Restoring note {note_id}")
                    note = self.create_note_from_data(note_data)
                    restored_notes.append(note)
        
        # First show the main window
        self.main_window.present()
        
        # Then, update the grid with all notes (both restored and existing)
        print("Updating main window grid")
        self.main_window.load_notes()
        
        # Finally, present all restored notes
        for note in restored_notes:
            note.present()
    
    def do_startup(self):
        Adw.Application.do_startup(self)
        
        # Acciones globales
        new_note_action = Gio.SimpleAction.new('new-note', None)
        new_note_action.connect('activate', self.on_new_note)
        self.add_action(new_note_action)
        
        quit_action = Gio.SimpleAction.new('quit', None)
        quit_action.connect('activate', self.on_quit)
        self.add_action(quit_action)
        
        about_action = Gio.SimpleAction.new('about', None)
        about_action.connect('activate', self.on_about)
        self.add_action(about_action)
        
        # Atajos de teclado
        self.set_accels_for_action('app.new-note', ['<Control>n'])
        self.set_accels_for_action('app.quit', ['<Control>q'])
    
    def create_new_note(self):
        note = StickyNote(self)
        
        # Update main window grid
        if self.main_window:
            self.main_window.add_note(note)
        
        note.present()
        return note
    
    def create_note_from_data(self, note_data):
        # Check if note window already exists
        for window in self.get_windows():
            if isinstance(window, StickyNote) and window.note_id == note_data['id']:
                window.present()
                return window
        
        print(f"Creating new note window for note {note_data['id']}")
        # Create new note window
        note = StickyNote(application=self, note_data=note_data)
        
        # Update main window grid
        if self.main_window:
            print(f"Adding note {note_data['id']} to main window")
            self.main_window.add_note(note)
            self.main_window.update_notes_grid()  # Force grid update
        
        return note
    
    def on_new_note(self, action, parameter):
        self.create_new_note()
    
    def on_quit(self, action, parameter):
        self.quit()
    
    def on_about(self, action, parameter):
        about = Adw.AboutWindow(
            transient_for=self.main_window,
            application_name="Sticky Notes",
            application_icon="org.gnome.StickyNotes",
            developer_name="Tu Nombre",
            version="1.0.0",
            developers=["Tu Nombre"],
            copyright="© 2024 Tu Nombre",
            license_type=Gtk.License.GPL_3_0,
            website="https://github.com/tu-usuario/sticky-notes",
            issue_url="https://github.com/tu-usuario/sticky-notes/issues"
        )
        about.present()
    
    def remove_note(self, note_id):
        # Remove from storage
        if note_id in self.notes:
            del self.notes[note_id]
            self.save_notes_data()
        
        # Update main window grid
        if self.main_window:
            self.main_window.remove_note(note_id)
    
    def save_note_data(self, note_data):
        self.notes[note_data['id']] = note_data
        self.save_notes_data()
    
    def load_notes_data(self):
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r') as f:
                    self.notes = json.load(f)
        except Exception as e:
            print(f"Error cargando datos: {e}")
            self.notes = {}
    
    def save_notes_data(self):
        try:
            with open(self.data_file, 'w') as f:
                json.dump(self.notes, f, indent=2)
        except Exception as e:
            print(f"Error guardando datos: {e}")
    
    def get_notes(self):
        """Returns a dictionary of active note windows"""
        active_notes = {}
        for window in self.get_windows():
            if isinstance(window, StickyNote):
                active_notes[window.note_id] = window
        return active_notes
        
    def get_main_window(self):
        """Returns the main application window"""
        if not self.main_window:
            self.main_window = StickyNotesWindow(application=self)
        return self.main_window
        
    def debug_note_state(self):
        """Print debug information about current note state"""
        print("\nNote State Debug:")
        print(f"Stored notes: {len(self.notes)}")
        for note_id, note_data in self.notes.items():
            print(f"  - Note {note_id}: {note_data.get('content', '')[:30]}...")
        
        active_notes = self.get_notes()
        print(f"Active notes: {len(active_notes)}")
        for note_id, note in active_notes.items():
            print(f"  - Note {note_id}: {note.save_note().get('content', '')[:30]}...")

def main(version):
    app = StickyNotesApp()
    return app.run(sys.argv)
