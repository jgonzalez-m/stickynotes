# Sticky Notes - Storage Format Documentation

This document describes the internal storage format and data structure of the Sticky Notes application, intended for developers who need to understand or modify the note storage system.

## 1. Note Storage Format

Sticky Notes uses a JSON-based storage format to save and retrieve notes. The application stores all notes in a single JSON file.

### 1.1 Basic Note Structure

The current implementation uses a simple JSON structure for each note:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": "This is the text content of the note",
  "color": "yellow",
  "x": 100,
  "y": 150,
  "timestamp": "2025-05-26T18:22:27.572071"
}
```

### 1.2 Enhanced Note Structure

The enhanced note structure supports rich text formatting and media attachments:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "content": {
    "blocks": [
      {
        "type": "text",
        "content": "This is formatted text",
        "format": {
          "bold": false,
          "italic": true,
          "underline": false
        }
      },
      {
        "type": "image",
        "path": "media/550e8400-e29b-41d4-a716-446655440000/image1.jpg",
        "caption": "Image caption"
      },
      {
        "type": "audio",
        "path": "media/550e8400-e29b-41d4-a716-446655440000/recording.mp3",
        "duration": "2:30"
      }
    ]
  },
  "metadata": {
    "created": "2025-05-26T18:22:27.572071",
    "modified": "2025-05-26T19:30:00.000000",
    "color": "yellow",
    "tags": ["work", "important"],
    "position": {
      "x": 100,
      "y": 150
    }
  }
}
```

## 2. Note Metadata and Properties

### 2.1 Core Properties

| Property      | Type      | Description                                           |
|---------------|-----------|-------------------------------------------------------|
| `id`          | String    | UUID for the note, generated when the note is created |
| `content`     | String/Object | Text content or structured content blocks         |
| `color`       | String    | Color theme of the note (see Color System)            |
| `x`           | Integer   | X-coordinate position of the note on screen           |
| `y`           | Integer   | Y-coordinate position of the note on screen           |
| `timestamp`   | String    | ISO-8601 formatted date-time of last modification     |

### 2.2 Enhanced Metadata

In the enhanced format, the `metadata` object contains:

| Property      | Type      | Description                                           |
|---------------|-----------|-------------------------------------------------------|
| `created`     | String    | ISO-8601 timestamp when the note was created          |
| `modified`    | String    | ISO-8601 timestamp of last modification               |
| `color`       | String    | Color theme of the note                               |
| `tags`        | Array     | List of user-defined tags                             |
| `position`    | Object    | Contains x and y coordinates                          |

### 2.3 Content Blocks

The enhanced format supports different types of content blocks:

#### Text Block
```json
{
  "type": "text",
  "content": "Text content",
  "format": {
    "bold": true,
    "italic": false,
    "underline": false
  }
}
```

#### Image Block
```json
{
  "type": "image",
  "path": "relative/path/to/image.jpg",
  "caption": "Optional image caption"
}
```

#### Audio Block
```json
{
  "type": "audio",
  "path": "relative/path/to/audio.mp3",
  "duration": "2:30"
}
```

## 3. Color System

### 3.1 Available Colors

The application supports six predefined colors:

| Color Name | Color Code | Background     | Border        | Text          |
|------------|------------|----------------|---------------|---------------|
| Yellow     | `yellow`   | `#ffeb3b`      | `#ffd600`     | `#3e3500`     |
| Pink       | `pink`     | `#f8d7da`      | `#f5c6cb`     | `#721c24`     |
| Blue       | `blue`     | `#cce5ff`      | `#74b9ff`     | `#004085`     |
| Green      | `green`    | `#d1ecf1`      | `#00b894`     | `#0c5460`     |
| Orange     | `orange`   | `#ffe8cc`      | `#fdcb6e`     | `#663c00`     |
| Purple     | `purple`   | `#e2d5f1`      | `#a29bfe`     | `#4a235a`     |

### 3.2 Color Implementation

Colors are applied through CSS. Each note has a unique CSS class generated from its ID to ensure styles don't affect other notes. The color styles include:

- Background color for the note
- Border color
- Text color for better contrast
- Hover effects for UI elements

## 4. File Locations and Management

### 4.1 Note Storage File

By default, notes are stored in:
```
~/.local/share/sticky-notes.json
```

The application creates this file if it doesn't exist when a note is saved for the first time.

### 4.2 Media Storage

In the enhanced format, media files are stored in a directory structure:
```
~/.local/share/sticky-notes/media/<note-id>/
```

Each note has its own directory, identified by the note's UUID, containing all media files referenced by that note.

### 4.3 Storage Management

- The application performs atomic writes to the storage file to prevent data corruption
- Media files are copied into the storage directory, not referenced from their original locations
- File names are sanitized before storage
- Unused media files (orphans) should be cleaned up periodically

## 5. Data Migration Considerations

### 5.1 Basic to Enhanced Format Migration

When upgrading from the basic to enhanced format, the migration process:

1. Creates a backup of the original storage file
2. Converts each note's simple content string to a single text block
3. Preserves all metadata (position, color, timestamp)
4. Adds default values for new properties
5. Updates the file format version indicator

### 5.2 Migration Code Example

```python
def migrate_notes_to_enhanced_format(notes_data):
    # Create backup
    backup_file = create_backup()
    
    migrated_notes = []
    
    for note in notes_data:
        # Create enhanced format
        enhanced_note = {
            "id": note["id"],
            "content": {
                "blocks": [
                    {
                        "type": "text",
                        "content": note.get("content", ""),
                        "format": {
                            "bold": False,
                            "italic": False,
                            "underline": False
                        }
                    }
                ]
            },
            "metadata": {
                "created": note.get("timestamp", datetime.now().isoformat()),
                "modified": note.get("timestamp", datetime.now().isoformat()),
                "color": note.get("color", "yellow"),
                "tags": [],
                "position": {
                    "x": note.get("x", 100),
                    "y": note.get("y", 100)
                }
            }
        }
        
        migrated_notes.append(enhanced_note)
    
    return migrated_notes
```

### 5.3 Backward Compatibility

To maintain backward compatibility:

- The application checks the format version when loading notes
- For enhanced notes loaded in an older version, only the first text block is shown
- For basic notes loaded in newer versions, they're automatically converted to the enhanced format in memory
- On save, notes are always saved in the format supported by the current version

## 6. Implementation Considerations

### 6.1 Loading Notes

```python
def load_notes():
    try:
        with open(get_storage_path(), 'r') as f:
            notes_data = json.load(f)
            
        # Check format version and migrate if needed
        if is_basic_format(notes_data):
            notes_data = convert_to_enhanced_format(notes_data)
            
        return notes_data
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        # Handle corrupted file
        backup_and_create_new()
        return []
```

### 6.2 Saving Notes

```python
def save_notes(notes_data):
    # Ensure directory exists
    os.makedirs(os.path.dirname(get_storage_path()), exist_ok=True)
    
    # Write to temporary file first
    temp_path = get_storage_path() + '.tmp'
    with open(temp_path, 'w') as f:
        json.dump(notes_data, f, indent=2)
    
    # Atomic replace
    os.replace(temp_path, get_storage_path())
```

### 6.3 Media Management

```python
def save_media_file(note_id, source_path):
    # Create media directory for note
    media_dir = os.path.join(get_media_path(), note_id)
    os.makedirs(media_dir, exist_ok=True)
    
    # Generate safe filename
    filename = os.path.basename(source_path)
    safe_filename = sanitize_filename(filename)
    
    # Copy file
    dest_path = os.path.join(media_dir, safe_filename)
    shutil.copy2(source_path, dest_path)
    
    # Return relative path for storage
    return os.path.join('media', note_id, safe_filename)
```

