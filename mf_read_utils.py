#%%
import zipfile
import os
from pathlib import Path
from xml.dom import minidom
import json
import xml.etree.ElementTree as ET

#%%

VALID_EXT = {".json", ".xml", ".rels", ".model", ".config"}
#%% open and extract 3mf file to a folder

def build_tree(path: Path):
    node = {
        "type": "folder",
        "name": path.name,
        "path": str(path),
        "children": []
    }

    for item in sorted(path.iterdir()):
        if item.is_dir():
            node["children"].append(build_tree(item))
        else:
            node["children"].append({
                "type": "file",
                "name": item.name,
                "path": str(item),
                "parsed": None  # will hold parsed content later
            })
    return node
#%% parse files based on extension

#%%
def parse_file(path: Path):
    try:
        if path.suffix == ".json":
            return json.loads(path.read_text(encoding="utf-8"))

        elif path.suffix in [".xml", ".rels", ".model", ".config"]:
            return pretty_xml(path.read_text(encoding="utf-8"))

        else:
            return None

    except Exception as e:
        return {"error": str(e)}

# ---------- Pretty Print XML ----------
def pretty_xml(xml_string):
    dom = minidom.parseString(xml_string)
    return dom.toprettyxml(indent="  ")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(base_dir, "Baby_Dragon_Multicolor_FF_P1P_X1C.3mf")
    output_path = os.path.join(base_dir, "extracted")
    with zipfile.ZipFile(input_file, 'r') as zin:
        zin.extractall(output_path)
    print("output_path:", output_path)
    
    tree = build_tree(Path(output_path))
    filepath = tree["children"][0]["children"][0]["path"]
    print("filepath:", filepath)
    parse_file(Path(filepath))