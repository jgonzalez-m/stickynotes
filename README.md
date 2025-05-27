# StickyNotes

## Overview
- Name: StickyNotes
- Version: 1.0.0
- License: GPL-3.0-or-later
- Description: A GNOME application for creating and managing digital sticky notes, providing a convenient way to keep track of reminders, tasks, and notes on your desktop.

## Project Structure

### Source Code (/src)
```
src/
├── gtk/
│   └── help-overlay.ui          # Keyboard shortcuts overlay UI
├── __init__.py                  # Package initialization
├── main.py                      # Application entry point
├── window.py                    # Main window implementation
├── window.ui                    # Main window UI definition
├── stickynotes.gresource.xml    # Resource configuration
└── stickynotes.in              # Application launcher script
```

### Data Files (/data)
```
data/
├── icons/
│   └── hicolor/
│       ├── scalable/apps/       # Full-color scalable icons
│       └── symbolic/apps/       # Symbolic icons
├── org.gnome.StickyNotes.desktop.in # Desktop entry template
├── org.gnome.StickyNotes.appdata.xml.in # AppStream metadata
└── org.gnome.StickyNotes.gschema.xml    # GSettings schema
```

## Technical Documentation

### Build System
StickyNotes uses the Meson build system with the following configuration:

- **Installation Directories**:
  - Program files: `prefix/share/stickynotes`
  - Python modules: `prefix/share/stickynotes/stickynotes`
  - Executable: `prefix/bin/stickynotes`
  - Data files: `prefix/share/stickynotes`

- **Dependencies**:
  - Python 3
  - GTK 4
  - GObject Introspection
  - Meson (>= 0.59.0)

### GNOME Integration
- **GResource Configuration**: The application uses GResource for UI file management
  ```xml
  <gresource prefix="/org/gnome/StickyNotes">
    <file preprocess="xml-stripblanks">window.ui</file>
    <file preprocess="xml-stripblanks">gtk/help-overlay.ui</file>
  </gresource>
  ```
  This configuration bundles the UI files (window.ui and help-overlay.ui) into the application's resource system, making them available at runtime under the `/org/gnome/StickyNotes` prefix.

- **UI Resources**:
  - `window.ui`: Main application window layout
  - `gtk/help-overlay.ui`: Keyboard shortcuts help overlay
  These UI files are preprocessed during build to optimize size and performance.

### Storage System
The application uses a JSON-based storage system for managing notes. For detailed information about the storage format and implementation, see [STORAGE.md](STORAGE.md).

## Internationalization

The application supports multiple languages through gettext-based localization. Translations are managed in the `po` directory.

### For Translators
- Translation template (.pot) and translation files (.po) are located in the `po` directory
- The application's text domain is "sticky-notes"
- New translations can be added by:
  1. Creating a new .po file for your language
  2. Translating the strings
  3. Adding the language to LINGUAS file
  4. Submitting a pull request

### For Developers
When adding new user-visible strings:
- Ensure all strings are marked for translation using gettext
- Update the translation template using:
  ```bash
  meson compile -C builddir stickynotes-pot
  meson compile -C builddir stickynotes-update-po
  ```

## Development Setup

### Prerequisites
- Python 3.x
- GTK 4 development libraries
- Meson and Ninja build system
- GNOME development tools

### Building from Source
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stickynotes.git
   cd stickynotes
   ```

2. Configure the build:
   ```bash
   meson setup builddir
   ```

3. Build the project:
   ```bash
   meson compile -C builddir
   ```

4. Install (optional):
   ```bash
   meson install -C builddir
   ```

### Development Environment
1. Set up a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt  # if available
   ```

## User Interface

### Main Window
- **Note List**: Displays all created sticky notes
- **Create Note**: Button to create a new sticky note
- **Note Editor**: Rich text editor for note content
- **Color Picker**: Choose note background color
- **Settings**: Configure application preferences

### Features
- Create, edit, and delete sticky notes
- Rich text formatting
- Customizable note colors
- Automatic note saving
- Desktop integration

### Configuration
The application provides several customizable settings through GNOME's GSettings system:

#### Note Appearance
- **Default Color**: Set the default background color for new notes (default: yellow)
- **Default Dimensions**:
  - Width: 250 pixels
  - Height: 200 pixels

#### Auto-save Settings
- **Auto-save Interval**: Frequency of automatic note saving (default: 1000ms)

#### Synchronization
- **Sync Enable**: Option to enable note synchronization across devices
- **Sync Server**: Configure the synchronization server URL

These settings can be modified through:
- The application's preferences dialog
- GNOME Settings
- Using `gsettings` command line tool:
  ```bash
  # Example: Change default note color
  gsettings set org.gnome.StickyNotes default-color 'blue'
  
  # Example: Adjust auto-save interval
  gsettings set org.gnome.StickyNotes auto-save-interval 2000
  ```

## Contributing

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Coding Standards
- Follow PEP 8 style guide for Python code
- Use meaningful variable and function names
- Add comments for complex logic
- Keep functions focused and concise

### Testing
- Write unit tests for new functionality
- Ensure existing tests pass
- Test UI changes manually
- Verify compatibility with different GNOME versions

## License
This project is licensed under the GNU General Public License v3.0 or later - see the [COPYING](COPYING) file for details.
