# 3MF Settings Editor

A GUI application for inspecting, filtering, and managing 3D printer-specific settings in .3mf files.

## What is it?

3MF (3D Manufacturing Format) files can contain embedded printer settings like:
- Build plate configuration
- Nozzle specifications  
- Material properties
- Slicer-specific configurations

This tool lets you:
- **View** all printer-specific settings embedded in a .3mf file
- **Select** which settings to keep using checkboxes
- **Save** a filtered copy containing only your selected settings

## Quick Start

### Windows
Double-click `run.bat` or run:
```bash
python 3mf_settings_editor.py
```

### Requirements
- Python 3.6 or later
- No external packages needed!

## Features

✅ Parse .3mf Files - Extract all embedded settings  
✅ Categorized Display - Settings organized by type  
✅ Checkbox Selection - Choose which settings to keep  
✅ Bulk Operations - Select/Deselect All buttons  
✅ Save Filtered Copies - Create new .3mf files with selected settings

## How It Works

1. Open a .3mf file
2. Extract and parse the embedded XML settings
3. Display all printer-specific settings organized by category
4. Select which settings you want to keep
5. Save a new .3mf file with only the selected settings

**Get Started**: Run `python 3mf_settings_editor.py` to launch the GUI!
