#!/usr/bin/env python3
"""
3MF Settings Editor - GUI program to manage 3D printer settings in .3mf files
Allows viewing, selecting, and saving filtered copies of 3mf files with specific settings
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import shutil
from typing import Dict, List, Tuple
import os
import json


class ThreeMFSettingsEditor:
    """Main application class for editing 3MF printer settings"""

    def __init__(self, root):
        self.root = root
        self.root.title("3MF Settings Editor")
        self.root.geometry("900x700")
        
        self.current_file = None
        self.extracted_temp_dir = None
        self.all_files_in_archive = {}  # Maps file paths to their settings
        self.selected_settings = {}  # Track which settings are selected
        self.file_path_map = {}  # Maps tree item IDs to archive file paths
        
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="3MF File", padding="10")
        file_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)
        
        self.file_label = ttk.Label(file_frame, text="No file selected", foreground="gray")
        self.file_label.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        
        ttk.Button(file_frame, text="Open 3MF File", command=self.open_file).grid(row=0, column=0)
        
        # Settings display section
        settings_frame = ttk.LabelFrame(main_frame, text="Printer Settings", padding="10")
        settings_frame.grid(row=2, column=0, sticky="nsew", pady=(0, 10))
        settings_frame.columnconfigure(0, weight=1)
        settings_frame.rowconfigure(0, weight=1)
        
        # Treeview for settings
        tree_frame = ttk.Frame(settings_frame)
        tree_frame.grid(row=0, column=0, sticky="nsew")
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Value", "Selected"),
            height=15,
            yscrollcommand=scrollbar.set,
            show="tree headings"
        )
        scrollbar.config(command=self.tree.yview)
        
        self.tree.column("#0", width=300)
        self.tree.heading("#0", text="Setting")
        self.tree.column("Value", width=300)
        self.tree.heading("Value", text="Value")
        self.tree.column("Selected", width=100)
        self.tree.heading("Selected", text="Keep")
        self.tree.grid(row=0, column=0, sticky="nsew")
        
        # Bind checkbox behavior
        self.tree.bind("<Button-1>", self.on_tree_click)
        
        # Info label
        self.info_label = ttk.Label(main_frame, text="Open a .3mf file to see available settings", foreground="gray")
        self.info_label.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        # Buttons section
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, sticky="ew")
        
        ttk.Button(button_frame, text="Select All", command=self.select_all).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Deselect All", command=self.deselect_all).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Save Filtered Copy", command=self.save_filtered_copy).pack(side="left", padx=5)

    def open_file(self):
        """Open a 3MF file and parse its settings"""
        file_path = filedialog.askopenfilename(
            filetypes=[("3MF Files", "*.3mf"), ("All Files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            self.current_file = file_path
            self.file_label.config(text=f"File: {Path(file_path).name}", foreground="black")
            
            # Extract all files and their settings from any folder in the archive
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                self.all_files_in_archive = {}
                # Iterate through ALL files in the archive regardless of folder
                for file_in_archive in zip_ref.namelist():
                    # Extract settings based on file extension (not folder location)
                    try:
                        if file_in_archive.endswith('.config'):
                            with zip_ref.open(file_in_archive) as fh:
                                content = fh.read().decode('utf-8', errors='ignore')
                                settings = self.parse_config_file(content, file_in_archive)
                                if settings:
                                    self.all_files_in_archive[file_in_archive] = settings
                        
                        elif file_in_archive.endswith(('.model', '.xml', '.rels')):
                            with zip_ref.open(file_in_archive) as fh:
                                try:
                                    tree = ET.parse(fh)
                                    root = tree.getroot()
                                    settings = self.extract_all_settings(root, file_in_archive)
                                    if settings:
                                        self.all_files_in_archive[file_in_archive] = settings
                                except ET.ParseError:
                                    pass
                        
                        elif file_in_archive.endswith('.json'):
                            with zip_ref.open(file_in_archive) as fh:
                                try:
                                    content = json.load(fh)
                                    settings = self.parse_json_settings(content, file_in_archive)
                                    if settings:
                                        self.all_files_in_archive[file_in_archive] = settings
                                except (json.JSONDecodeError, UnicodeDecodeError):
                                    pass
                    except Exception as e:
                        pass  # Skip files that can't be parsed
            
            self.display_settings()
            total_settings = sum(len(cat_settings) for file_settings in self.all_files_in_archive.values() 
                                for cat_settings in file_settings.values())
            self.info_label.config(
                text=f"Found {len(self.all_files_in_archive)} files with {total_settings} total settings",
                foreground="green"
            )
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
            self.file_label.config(text="No file selected", foreground="gray")

    def extract_printer_settings(self, file_path: str) -> Dict[str, List[Tuple]]:
        """Extract printer-specific settings from 3MF file"""
        settings_data = {}
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                
                # Priority: Check metadata config files first
                config_files = [f for f in file_list if f.endswith('.config')]
                json_files = [f for f in file_list if f.endswith('.json')]
                model_files = [f for f in file_list if f.endswith('.model')]
                xml_files = [f for f in file_list if f.endswith('.xml')]
                
                # Process config files (these likely have printer settings)
                for config_file in config_files:
                    try:
                        with zip_ref.open(config_file) as file_handle:
                            content = file_handle.read().decode('utf-8', errors='ignore')
                            config_settings = self.parse_config_file(content, config_file)
                            if config_settings:
                                for category, settings_list in config_settings.items():
                                    if category not in settings_data:
                                        settings_data[category] = []
                                    settings_data[category].extend(settings_list)
                    except Exception as e:
                        print(f"Warning: Could not parse {config_file}: {str(e)}")
                
                # Process JSON files
                for json_file in json_files:
                    try:
                        with zip_ref.open(json_file) as file_handle:
                            content = json.load(file_handle)
                            json_settings = self.parse_json_settings(content, json_file)
                            if json_settings:
                                for category, settings_list in json_settings.items():
                                    if category not in settings_data:
                                        settings_data[category] = []
                                    settings_data[category].extend(settings_list)
                    except Exception as e:
                        print(f"Warning: Could not parse {json_file}: {str(e)}")
                
                # Process model files (XML) - skips mesh elements internally
                for model_file in model_files:
                    try:
                        with zip_ref.open(model_file) as file_handle:
                            tree = ET.parse(file_handle)
                            root = tree.getroot()
                            model_settings = self.extract_all_settings(root, model_file)
                            if model_settings:
                                for category, settings_list in model_settings.items():
                                    if category not in settings_data:
                                        settings_data[category] = []
                                    settings_data[category].extend(settings_list)
                    except Exception as e:
                        print(f"Warning: Could not parse {model_file}: {str(e)}")
                
                # Process XML files
                for xml_file in xml_files:
                    try:
                        with zip_ref.open(xml_file) as file_handle:
                            tree = ET.parse(file_handle)
                            root = tree.getroot()
                            xml_settings = self.extract_all_settings(root, xml_file)
                            if xml_settings:
                                for category, settings_list in xml_settings.items():
                                    if category not in settings_data:
                                        settings_data[category] = []
                                    settings_data[category].extend(settings_list)
                    except Exception as e:
                        print(f"Warning: Could not parse {xml_file}: {str(e)}")
        
        except Exception as e:
            raise Exception(f"Error parsing 3MF file: {str(e)}")
        
        return settings_data

    def parse_config_file(self, content: str, filename: str) -> Dict[str, List[Tuple]]:
        """Parse .config files (INI-like format)"""
        settings_data = {}
        settings_list = []
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            if not line or line.startswith(';') or line.startswith('#'):
                continue
            
            # Check for section headers
            if line.startswith('[') and line.endswith(']'):
                current_section = line[1:-1]
                continue
            
            # Parse key=value pairs
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                # Filter for printer-related settings
                if any(kw in key.lower() for kw in 
                       ['printer', 'build', 'material', 'nozzle', 'bed', 'platform', 
                        'extruder', 'temp', 'speed', 'layer', 'quality', 'infill',
                        'support', 'profile', 'filament', 'setting', 'param']):
                    if current_section:
                        settings_list.append((f"{current_section}: {key}", value))
                    else:
                        settings_list.append((key, value))
        
        if settings_list:
            config_name = filename.split('/')[-1]
            settings_data[config_name] = settings_list
        
        return settings_data
    
    def parse_json_settings(self, content: dict, filename: str) -> Dict[str, List[Tuple]]:
        """Parse JSON settings files"""
        settings_data = {}
        settings_list = []
        
        def extract_json_values(obj, prefix=""):
            """Recursively extract key-value pairs from JSON"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_prefix = f"{prefix}.{key}" if prefix else key
                    
                    # Check if this looks like a printer setting
                    if any(kw in key.lower() for kw in 
                           ['printer', 'build', 'material', 'nozzle', 'bed', 'platform', 
                            'extruder', 'temp', 'speed', 'layer', 'quality', 'infill',
                            'support', 'profile', 'filament', 'setting', 'param', 'type']):
                        if isinstance(value, (str, int, float, bool)):
                            settings_list.append((new_prefix, str(value)))
                    
                    # Recurse into nested objects
                    if isinstance(value, (dict, list)):
                        extract_json_values(value, new_prefix)
            
            elif isinstance(obj, list):
                for idx, item in enumerate(obj):
                    new_prefix = f"{prefix}[{idx}]"
                    if isinstance(item, (dict, list)):
                        extract_json_values(item, new_prefix)
        
        try:
            extract_json_values(content)
        except Exception as e:
            print(f"Error extracting JSON values: {str(e)}")
        
        if settings_list:
            json_name = filename.split('/')[-1]
            settings_data[json_name] = settings_list
        
        return settings_data

    def extract_all_settings(self, root, xml_file: str) -> Dict[str, List[Tuple]]:
        """Extract all settings from XML root recursively, skipping mesh data"""
        settings_data = {}
        
        # Collect all elements with printer-related keywords
        printer_keywords = ['printer', 'build', 'material', 'nozzle', 'bed', 'platform', 
                          'extruder', 'temp', 'speed', 'layer', 'setting', 'config', 
                          'property', 'param', 'metadata', 'profile', 'quality', 'bambu',
                          'filament', 'infill', 'support', 'model', 'object']
        
        # Elements to skip (large binary/geometric data)
        skip_tags = ['mesh', 'vertices', 'triangles', 'triangle', 'vertex']
        
        metadata_list = []
        for elem in root.iter():
            tag_name = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            
            # Skip mesh and geometric data
            if any(skip in tag_name.lower() for skip in skip_tags):
                continue
            
            # Get value from text, attributes, or common value fields
            value = (elem.text or elem.get('value') or elem.get('v') or '').strip()
            
            # If element has a 'name' attribute, prefer that as the key (common in metadata)
            if 'name' in elem.attrib:
                key = elem.get('name')
                if value:
                    metadata_list.append((key, value))
            # Otherwise check if element name or attributes match printer keywords
            elif any(kw in tag_name.lower() for kw in printer_keywords):
                if value:
                    metadata_list.append((tag_name, value))
            
            # Also check element attributes for settings (skip 'name' as we already handled it)
            for attr_name, attr_value in elem.attrib.items():
                if attr_name != 'name' and attr_value and attr_value.strip():
                    attr_key = attr_name.split('}')[-1] if '}' in attr_name else attr_name
                    if any(kw in attr_key.lower() for kw in printer_keywords):
                        metadata_list.append((f"{tag_name}@{attr_key}", attr_value.strip()))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_settings = []
        for setting in metadata_list:
            if setting not in seen:
                seen.add(setting)
                unique_settings.append(setting)
        
        if unique_settings:
            settings_data["Settings from " + xml_file.split('/')[-1]] = unique_settings
        
        return settings_data

    def extract_from_metadata(self, root) -> List[Tuple]:
        """Extract metadata settings like printer name, build info, etc."""
        settings = []
        
        # Define namespace (3MF uses namespaces)
        ns = {
            '3mf': 'http://schemas.microsoft.com/3dmanufacturing/core/2015/02',
            'slic3r': 'http://slic3r.org/namespaces/slic3rpe',
            'p': 'http://schemas.microsoft.com/3dmanufacturing/production/2015/02'
        }
        
        # Look for metadata
        for key_elem in root.findall('.//{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}metadata'):
            name = key_elem.get('name', 'Unknown')
            value = key_elem.get('value', '')
            if name and value:
                # Filter for printer-specific settings
                if any(keyword in name.lower() for keyword in 
                       ['printer', 'build', 'material', 'nozzle', 'bed', 'platform', 'extruder']):
                    settings.append((name, value))
        
        # Also check for production metadata
        for elem in root.findall('.//{http://schemas.microsoft.com/3dmanufacturing/production/2015/02}*'):
            tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
            text = elem.text or elem.get('v', '')
            if text:
                settings.append((tag, text))
        
        return settings

    def extract_from_object_settings(self, root) -> List[Tuple]:
        """Extract object-specific printer settings"""
        settings = []
        
        # Look for SlicerConfig or similar elements
        for config in root.findall('.//{http://slic3r.org/namespaces/slic3rpe}config'):
            for child in config:
                tag = child.tag.split('}')[-1] if '}' in child.tag else child.tag
                value = child.text or child.get('v', '')
                if value:
                    settings.append((tag, value))
        
        # Look for any setting elements
        for setting in root.findall('.//setting'):
            key = setting.get('id', setting.get('name', 'Unknown'))
            value = setting.text or setting.get('value', '')
            if value:
                settings.append((key, value))
        
        # Look for properties that might be printer settings
        for prop in root.findall('.//{*}property'):
            name = prop.get('name', '')
            value = prop.get('value', '')
            if name and value and any(kw in name.lower() for kw in 
                                     ['printer', 'nozzle', 'bed', 'temp', 'speed', 'layer']):
                settings.append((name, value))
        
        return settings

    def extract_from_build(self, root) -> List[Tuple]:
        """Extract build platform and print settings"""
        settings = []
        
        # Look for build element attributes
        for build in root.findall('.//{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}build'):
            build_id = build.get('buildid', '')
            if build_id:
                settings.append(('Build ID', build_id))
        
        return settings

    def display_settings(self):
        """Display folder structure and settings in the tree view"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Reset selected settings and file path map
        self.selected_settings = {}
        self.file_path_map = {}
        
        # Create root item with archive filename
        archive_name = Path(self.current_file).name if self.current_file else "3MF File"
        root_id = self.tree.insert("", "end", text=f"[{archive_name}]", values=("", ""))
        
        # Build folder structure
        folder_tree = {}
        for file_path in sorted(self.all_files_in_archive.keys()):
            parts = file_path.split('/')
            current = folder_tree
            
            # Build nested folder structure
            for i, part in enumerate(parts[:-1]):
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add the file with its settings, tagging it with the actual path
            filename = parts[-1]
            current[filename] = {'_archive_path': file_path, **self.all_files_in_archive[file_path]}
        
        # Recursively display the folder tree
        self._build_tree_items(root_id, folder_tree, self.selected_settings)
    
    def _build_tree_items(self, parent_id, folder_dict, selected_settings, path_prefix=""):
        """Recursively build tree items from folder structure"""
        for name, content in sorted(folder_dict.items()):
            if isinstance(content, dict):
                # Check if this is a file with settings or a folder
                if '_archive_path' in content:
                    # It's a file with settings
                    archive_path = content['_archive_path']
                    file_id = self.tree.insert(parent_id, "end", text=f"📄 {name}", values=("", ""))
                    
                    # Map tree item to archive path
                    self.file_path_map[file_id] = archive_path
                    
                    # Initialize settings tracking for this file
                    if file_id not in selected_settings:
                        selected_settings[file_id] = {}
                    
                    # Add settings as children of the file
                    file_content = {k: v for k, v in content.items() if k != '_archive_path'}
                    for category, settings_list in sorted(file_content.items()):
                        category_id = self.tree.insert(file_id, "end", text=category, values=("", ""))
                        
                        for setting_name, setting_value in settings_list:
                            item_id = self.tree.insert(category_id, "end", text=setting_name, 
                                                      values=(setting_value, "☐"))
                            selected_settings[file_id][item_id] = {
                                'name': setting_name,
                                'value': setting_value,
                                'selected': False
                            }
                else:
                    # It's a folder - create folder item
                    folder_id = self.tree.insert(parent_id, "end", text=f"📁 {name}", values=("", ""))
                    new_path = f"{path_prefix}/{name}" if path_prefix else name
                    self._build_tree_items(folder_id, content, selected_settings, new_path)

    def on_tree_click(self, event):
        """Handle checkbox click in tree view"""
        item = self.tree.identify('item', event.x, event.y)
        if not item:
            return
        
        # Walk up to find which file this setting belongs to
        current = item
        file_id = None
        
        # Look through all our tracked file nodes to find the ancestor
        for potential_file_id in self.selected_settings.keys():
            if item in self.selected_settings[potential_file_id]:
                file_id = potential_file_id
                break
        
        # Only toggle if we found a file and the item exists in selected_settings
        if file_id and file_id in self.selected_settings and item in self.selected_settings[file_id]:
            setting = self.selected_settings[file_id][item]
            setting['selected'] = not setting['selected']
            
            # Update checkbox display
            new_checkbox = "☑" if setting['selected'] else "☐"
            values = self.tree.item(item)['values']
            self.tree.item(item, values=(values[0], new_checkbox))

    def select_all(self):
        """Select all settings"""
        for file_settings in self.selected_settings.values():
            for setting in file_settings.values():
                setting['selected'] = True
        self.refresh_display()

    def deselect_all(self):
        """Deselect all settings"""
        for file_settings in self.selected_settings.values():
            for setting in file_settings.values():
                setting['selected'] = False
        self.refresh_display()

    def refresh_display(self):
        """Refresh the tree view display"""
        for item in self.tree.get_children():
            self.update_tree_item(item)

    def update_tree_item(self, parent_id):
        """Recursively update tree item checkboxes"""
        for item in self.tree.get_children(parent_id):
            # Check if this item is a setting with a checkbox
            for file_id, file_settings in self.selected_settings.items():
                if item in file_settings:
                    setting = file_settings[item]
                    checkbox = "☑" if setting['selected'] else "☐"
                    values = self.tree.item(item)['values']
                    self.tree.item(item, values=(values[0], checkbox))
                    break
            
            # Recursively update children
            self.update_tree_item(item)

    def save_filtered_copy(self):
        """Save a copy of the 3MF file with filtered settings"""
        if not self.current_file:
            messagebox.showwarning("Warning", "Please open a file first")
            return
        
        # Get selected settings organized by file path
        selected_by_file = {}
        for file_id, file_settings in self.selected_settings.items():
            selected_items = [s for s in file_settings.values() if s['selected']]
            if selected_items and file_id in self.file_path_map:
                file_path = self.file_path_map[file_id]
                selected_by_file[file_path] = selected_items
        
        if not selected_by_file:
            messagebox.showwarning("Warning", "Please select at least one setting to keep")
            return
        
        # Ask for save location
        output_file = filedialog.asksaveasfilename(
            defaultextension=".3mf",
            filetypes=[("3MF Files", "*.3mf"), ("All Files", "*.*")],
            initialfile=f"filtered_{Path(self.current_file).name}"
        )
        
        if not output_file:
            return
        
        try:
            self.create_filtered_3mf(output_file, selected_by_file)
            messagebox.showinfo("Success", f"Filtered file saved:\n{output_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    def create_filtered_3mf(self, output_path: str, selected_by_file: dict):
        """Create a new 3MF file with only selected settings"""
        # Copy the original file
        shutil.copy2(self.current_file, output_path)
        
        # Read and modify the XML inside the 3MF (ZIP) file
        with zipfile.ZipFile(output_path, 'a') as zip_ref:
            for file_path, selected_settings in selected_by_file.items():
                if not file_path.endswith(('.config', '.model', '.xml')):
                    continue
                
                try:
                    with zip_ref.open(file_path) as xml_file:
                        tree = ET.parse(xml_file)
                        root = tree.getroot()
                    
                    # Store selected setting names for filtering
                    selected_names = {s['name'] for s in selected_settings}
                    
                    # Remove unselected metadata elements
                    for elem in root.findall('.//{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}metadata'):
                        name = elem.get('name', '')
                        if name and name not in selected_names:
                            parent = root.find('.//{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}metadata/..')
                            if parent is not None:
                                parent.remove(elem)
                    
                    # Write modified XML back to the zip
                    xml_string = ET.tostring(root, encoding='utf-8')
                    zip_ref.writestr(file_path, xml_string)
                except Exception as e:
                    print(f"Warning: Could not update {file_path}: {str(e)}")


def main():
    """Main entry point"""
    root = tk.Tk()
    app = ThreeMFSettingsEditor(root)
    root.mainloop()


if __name__ == "__main__":
    main()
