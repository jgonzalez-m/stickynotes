# note.py
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

from gi.repository import Gtk, Adw, Gio, GLib, Gdk
import uuid
from datetime import datetime
import os
from pathlib import Path

class StickyNote(Gtk.ApplicationWindow):
    def __init__(self, app, note_data=None):
        # Handle both 'app' and 'application' parameters for better compatibility
        super().__init__(application=app)
        
        # Datos de la nota
        self.note_id = note_data.get('id', str(uuid.uuid4())) if note_data else str(uuid.uuid4())
        self.color = note_data.get('color', 'yellow') if note_data else 'yellow'
        self.title = note_data.get('title', '') if note_data else ''
        
        # Ensure CSS is loaded
        self.load_css()
        
        # Initialize window position tracking
        self.initial_window_x = note_data.get('x', 100) if note_data else 100
        self.initial_window_y = note_data.get('y', 100) if note_data else 100
        self.window_x = self.initial_window_x
        self.window_y = self.initial_window_y
        
        # Store initial position for later use
        # Note: In GTK4, we can't directly set window position in constructor
        # Position will be set when the window is mapped
        self.connect('realize', self.on_realize)
        
        
        # Configurar ventana
        self.set_default_size(250, 200)
        self.set_resizable(True)
        
        # Set window properties
        self.set_hide_on_close(True)
        self.set_title("Sticky Note")
        
        # Add styling classes
        style_context = self.get_style_context()
        style_context.add_class('sticky-note')
        
        # Add a unique CSS class for this note instance
        self.unique_class = f'note-{self.note_id.replace("-", "")}'
        style_context.add_class(self.unique_class)
        
        # Add Wayland-specific support
        if Gdk.Display.get_default().get_name() == 'wayland':
            style_context.add_class('csd')  # Client-side decorations
            style_context.add_class('wayland')
        
        # We'll use the position tracking already initialized
        
        # We'll attach the drag controller to the header_drag later
        
        # Crear interfaz
        self.setup_ui()
        
        # Cargar contenido si existe
        if note_data and 'content' in note_data:
            self.text_view.get_buffer().set_text(note_data['content'])
        
        # Aplicar color
        self.set_note_color(self.color)
        
        # Conectar eventos para auto-guardado
        self.text_view.get_buffer().connect('changed', self.on_text_changed)
        
    def load_css(self):
        """Cargar estilos CSS desde el archivo"""
        try:
            css_provider = Gtk.CssProvider()
            css_file = Gio.File.new_for_path('/home/kooke/Proyectos/stickynotes/src/stickynotes/css/note.css')
            
            # Leer el contenido del archivo y reemplazar UNIQUE_ID
            success, contents, _ = css_file.load_contents()
            if success:
                css_text = contents.decode('utf-8')
                css_text = css_text.replace('UNIQUE_ID', self.note_id.replace('-', ''))
                css_provider.load_from_data(css_text.encode('utf-8'))
                
                # Obtener el contexto de estilo y aplicar el proveedor
                style_context = self.get_style_context()
                style_context.add_provider(
                    css_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
                )
                
                # Agregar clases CSS necesarias
                style_context.add_class('sticky-note')
                style_context.add_class(f'sticky-note-{self.note_id.replace("-", "")}')
                
                print(f"Note CSS loaded successfully for note {self.note_id}")
            else:
                print("Failed to load CSS file contents")
                
        except Exception as e:
            print(f"Error loading note CSS: {e}")
        
    def setup_ui(self):
        # Container principal
        self.main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(self.main_box)
        
        # Header con botones - Using a WindowHandle for better drag support
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        header.set_css_classes(['toolbar'])
        header.set_spacing(6)
        header.set_margin_start(6)
        header.set_margin_end(6)
        header.set_margin_top(6)
        
        # Botón de color
        self.color_button = Gtk.MenuButton()
        self.color_button.set_icon_name('color-select-symbolic')
        self.color_button.set_tooltip_text('Cambiar color')
        
        # The menu will be set up in setup_actions()
        
        # Ensure the button is sensitive and visible
        self.color_button.set_sensitive(True)
        self.color_button.set_visible(True)
        
        # Botón de nueva nota (+)
        new_note_button = Gtk.Button()
        new_note_button.set_icon_name('list-add-symbolic')
        new_note_button.set_tooltip_text('Crear nueva nota')
        new_note_button.connect('clicked', self.on_new_note_clicked)
        
        # Botón cerrar
        close_button = Gtk.Button()
        close_button.set_icon_name('window-close-symbolic')
        close_button.set_tooltip_text('Cerrar nota')
        close_button.connect('clicked', self.on_close_clicked)
        
        # Agregar botones al header
        header.append(self.color_button)
        header.append(new_note_button)  # Añadir botón de nueva nota
        header.append(Gtk.Box())  # Spacer
        header.append(close_button)
        
        # Área de texto
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        scrolled.set_margin_start(6)
        scrolled.set_margin_end(6)
        scrolled.set_margin_bottom(6)
        
        self.text_view = Gtk.TextView()
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        self.text_view.set_cursor_visible(True)
        scrolled.set_child(self.text_view)
        
        # Add drag area for the header
        header_drag = Gtk.WindowHandle()
        header_drag.set_child(header)  # Wrap the header in the drag handle
        
        # Make the header draggable
        self.drag_controller = Gtk.GestureDrag.new()
        self.drag_controller.connect('drag-begin', self.on_drag_begin)
        self.drag_controller.connect('drag-update', self.on_drag_update)
        self.drag_controller.connect('drag-end', self.on_drag_end)
        header_drag.add_controller(self.drag_controller)
        
        # Set the handle as draggable
        header_drag.set_can_target(True)
        header_drag.set_cursor(Gdk.Cursor.new_from_name("grab", None))
        
        # Agregar al container principal
        self.main_box.append(header_drag)  # Use header_drag instead of header directly
        self.main_box.append(scrolled)
        
        # Acciones
        self.setup_actions()
    
    def setup_actions(self):
        # Remove existing action if it exists
        try:
            self.remove_action('set-color')
        except:
            pass
        
        # Create and add the color action
        color_action = Gio.SimpleAction.new(
            'set-color',
            GLib.VariantType.new('s')
        )
        color_action.connect('activate', self.on_color_changed)
        self.add_action(color_action)
        
        # Create color menu
        color_menu = Gio.Menu()
        colors = [
            ('Amarillo', 'yellow'),
            ('Rosa', 'pink'), 
            ('Azul', 'blue'),
            ('Verde', 'green'),
            ('Naranja', 'orange'),
            ('Púrpura', 'purple')
        ]
        
        for color_name, color_code in colors:
            # Create menu item with proper action format
            detailed_action = f"win.set-color('{color_code}')"  # Use parentheses format with quoted parameter
            item = Gio.MenuItem.new(color_name, detailed_action)
            color_menu.append_item(item)
        
        self.color_button.set_menu_model(color_menu)
        print("Color menu setup completed")
    
    def set_note_color(self, color):
        print(f"Changing note color to: {color}")
        
        # Validar el color
        valid_colors = ['yellow', 'pink', 'blue', 'green', 'orange', 'purple']
        if color not in valid_colors:
            print(f"Warning: Invalid color {color}, defaulting to yellow")
            color = 'yellow'
        
        # Obtener el contexto de estilo
        style_context = self.get_style_context()
        
        # Remover colores anteriores
        for c in valid_colors:
            style_context.remove_class(c)
        
        # Agregar el nuevo color
        style_context.add_class(color)
        
        # Almacenar el color
        self.color = color
        
        print(f"Successfully applied {color} style")
    
    def on_color_changed(self, action, parameter):
        # Handle the color parameter correctly
        if parameter:
            color = parameter.get_string()
            # Remove any quotes that might have been included
            color = color.strip("'\"")
            print(f"Color change requested to: {color}")
            self.set_note_color(color)
            self.save_note()
    
    def on_drag_begin(self, gesture, x, y):
        print(f"Drag begin at coordinates: x={x}, y={y}")  # Debug logging
        self.drag_start_x = x
        self.drag_start_y = y
        # Store initial window position
        self.initial_window_x = self.window_x
        self.initial_window_y = self.window_y
    
    def on_drag_update(self, gesture, offset_x, offset_y):
        print(f"Drag update - offset: x={offset_x}, y={offset_y}")
        
        try:
            # Calculate new position based on initial position and offset
            new_x = int(self.initial_window_x + offset_x)
            new_y = int(self.initial_window_y + offset_y)
            
            # Update internal position tracking
            self.window_x = new_x
            self.window_y = new_y
            
            # In GTK4, we need to use surface positioning
            if self.get_surface():
                # Get the native surface to position it
                surface = self.get_native()
                if surface:
                    surface.get_surface().set_device_position(None, new_x, new_y)
                    print(f"Window moved to: x={new_x}, y={new_y}")
        except Exception as e:
            print(f"Error moving window: {e}")
    
    def on_drag_end(self, gesture, offset_x, offset_y):
        print(f"Drag ended at offset: x={offset_x}, y={offset_y}")  # Debug logging
        # Save the final position
        self.save_note()
    
    def on_text_changed(self, buffer):
        # Auto-guardar después de cambios
        GLib.timeout_add(1000, self.save_note)  # Guardar después de 1 segundo
    
    def on_close_clicked(self, button):
        self.save_note()
        app = self.get_application()
        app.remove_note(self.note_id)
        
        # Update the main window's note grid
        main_window = app.get_main_window()
        if main_window:
            main_window.remove_note(self.note_id)
            
        self.close()
    
    def on_new_note_clicked(self, button):
        # Create a new note
        app = self.get_application()
        app.create_new_note()
    
    def save_note(self):
        app = self.get_application()
        
        # Obtener contenido
        buffer = self.text_view.get_buffer()
        content = buffer.get_text(
            buffer.get_start_iter(),
            buffer.get_end_iter(),
            False
        )
        
        # Actualizar título si está vacío
        if not self.title:
            lines = content.strip().split('\n')
            self.title = lines[0].strip() if lines and lines[0].strip() else "Nota sin título"
        
        # Obtener posición - usar valores internos que mantenemos actualizados
        # durante las operaciones de arrastre
        x, y = self.window_x, self.window_y
        
        # Datos de la nota
        note_data = {
            'id': self.note_id,
            'title': self.title,
            'content': content,
            'color': self.color,
            'x': x,
            'y': y,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save the note data to app's storage
        app.save_note_data(note_data)
        
        # Update the preview in the main window if available
        # Avoid calling update_from_note() as it might call save_note() again
        # causing infinite recursion
        main_window = app.get_main_window()
        if main_window and self.note_id in main_window.note_previews:
            # Instead of calling update_from_note(self), pass the note_data directly
            main_window.note_previews[self.note_id].update_preview(note_data)
        return note_data
        
    def on_realize(self, widget):
        """Handler called when window is realized - sets initial position"""
        try:
            # In GTK4, we need to use surface positioning
            if self.get_surface():
                # Get the native surface to position it
                surface = self.get_native()
                if surface:
                    surface.get_surface().set_device_position(None, self.window_x, self.window_y)
                    print(f"Initial window position set to: x={self.window_x}, y={self.window_y}")
        except Exception as e:
            print(f"Error setting initial window position: {e}")

