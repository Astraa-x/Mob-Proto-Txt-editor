# Metin2 Mob Proto Editor

A comprehensive GUI tool for editing Metin2 `mob_proto.txt` files with full functionality for loading, editing, and saving mob data.

## Features

- **Complete File Support**: Load and save `mob_proto.txt` with all 67 columns
- **Table Editor**: Excel-like interface for editing all mob properties
- **Search & Filter**: Find mobs by name, VNUM, type, or any other field
- **Mass Editing**: Apply changes to multiple mobs at once (EXP multipliers, etc.)
- **Undo/Redo**: Full undo/redo support for all changes
- **Backup Creation**: Automatic backups before saving
- **CSV Export/Import**: Export to CSV for external editing
- **Data Validation**: Ensures file format compatibility with Metin2 server

## Installation

1. Ensure Python 3.6+ is installed
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Starting the Application
```
python mob_proto_editor.py
```

The application will automatically load `mob_proto.txt` if it exists in the same directory.

### Basic Operations

1. **Open File**: File → Open or Ctrl+O
2. **Save File**: File → Save or Ctrl+S
3. **Search**: Use the search box in the toolbar
4. **Filter by Type**: Use the dropdown to filter by mob type (MONSTER, BOSS, etc.)

### Editing Data

- **Single Cell**: Click any cell to edit individual values
- **Multiple Selection**: Select rows and use Edit → Mass Edit for bulk changes
- **Undo/Redo**: Ctrl+Z to undo, Ctrl+Y to redo

### Mass Editing

Access via Edit → Mass Edit or the toolbar button:

- **Multiply**: Multiply values (e.g., EXP x2, GOLD x1.5)
- **Add**: Add to existing values (e.g., +100 HP to all mobs)
- **Set**: Set specific values for selected mobs

Common use cases:
- Double all EXP: Select EXP column, multiply by 2
- Increase gold drops: Select GOLD_MIN/GOLD_MAX, multiply by 1.5
- Level adjustment: Select LEVEL, add 5

### Export/Import

- **Export to CSV**: File → Export to CSV (for Excel editing)
- **Import from CSV**: File → Import from CSV (restore from Excel)

## File Format

The editor maintains full compatibility with Metin2 server format:
- Tab-separated values
- UTF-8 encoding
- All 67 standard columns supported
- Automatic backup creation

## Supported Columns

All standard mob_proto.txt columns are supported:
- Basic stats (VNUM, NAME, LEVEL, etc.)
- Combat stats (DAMAGE_MIN/MAX, HP, DEF, etc.)
- Resistances (RESIST_SWORD, RESIST_FIRE, etc.)
- Special flags (AI_FLAG, RACE_FLAG, IMMUNE_FLAG, etc.)
- Skills and special abilities

## Safety Features

- **Automatic Backups**: Created before each save with timestamp
- **Undo System**: Up to 50 undo levels
- **Data Validation**: Prevents invalid data entry
- **File Format Preservation**: Maintains server compatibility

## Keyboard Shortcuts

- Ctrl+O: Open file
- Ctrl+S: Save file
- Ctrl+Z: Undo
- Ctrl+Y: Redo

## Troubleshooting

### PyQt5 Installation Issues
If PyQt5 fails to install:
```
pip install PyQt5 --user
```

### File Encoding Issues
The editor uses UTF-8 encoding. If you see strange characters:
1. Ensure your mob_proto.txt is UTF-8 encoded
2. Use a text editor like Notepad++ to convert if needed

### Large Files
For very large mob files (>10,000 entries):
- Use filters to work with subsets
- Consider CSV export for major bulk operations

## Tips

1. **Before Major Changes**: Create a manual backup copy
2. **Mass Editing**: Select specific rows first, or changes apply to all visible mobs
3. **Testing**: Always test changes on a development server first
4. **Performance**: Use filters when working with large files (1000+ mobs)

## File Structure

- `mob_proto_editor.py` - Main application
- `requirements.txt` - Python dependencies
- `README.md` - This documentation
- `mob_proto.txt` - Your mob data file (not included)

## Version History

- v1.0: Initial release with full editing capabilities
