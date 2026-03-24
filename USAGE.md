# 3MF Settings Editor - Usage Guide

## Overview
This GUI application allows you to inspect 3D printer-specific settings stored in .3mf files and create filtered copies with only the settings you want to keep.

## Features
- **Open 3MF Files**: Load .3mf files to view all printer settings
- **Categorized View**: Settings are organized by category (Metadata, Object Settings, Build Settings)
- **Selective Filtering**: Use checkboxes to select which settings to keep
- **Bulk Operations**: Select All or Deselect All buttons for quick changes
- **Save Filtered Copies**: Create new .3mf files with only your selected settings

## How to Use

### 1. Run the Application
```bash
python 3mf_settings_editor.py
```
This will open the GUI window.

### 2. Open a 3MF File
- Click the **"Open 3MF File"** button
- Select a .3mf file from your computer
- The application will parse the file and display all available printer settings

### 3. View and Select Settings
- Settings are organized by category (expand categories to see individual settings)
- Each setting shows its current value
- Click the checkbox (☐) next to a setting to select/deselect it (checked: ☑)
- Selected settings will be kept in the filtered copy

### 4. Quick Actions
- **Select All**: Selects all settings at once
- **Deselect All**: Deselects all settings (start fresh)

### 5. Save Filtered Copy
- Once you've selected the settings you want to keep, click **"Save Filtered Copy"**
- Choose a location and filename for the new .3mf file
- The new file will be created with only the selected settings retained

## Settings Categories

### Metadata
- Printer name
- Build plate information
- Material settings
- Nozzle configuration
- Bed temperature settings
- Custom metadata from your slicer

### Object Settings
- Layer heights
- Print speeds
- Infill settings
- Support settings
- Other per-object configuration

### Build Settings
- Build IDs
- Platform information
- Build configuration

## Use Cases

1. **Clean Up Settings**: Remove slicer-specific settings before sharing files
2. **Standardize Files**: Keep only essential printer settings across multiple files
3. **Backup Settings**: Create copies with specific configuration saved
4. **Mixed Material Prep**: Select only the settings relevant to your printer

## Requirements
- Python 3.6+
- No external packages required (uses standard library only)

## Notes
- The original .3mf file is never modified
- Filtered copies are standalone files that can be opened in any 3D printing software
- Settings are displayed exactly as they are stored in the file
- Complex nested XML structures are simplified for easy viewing
