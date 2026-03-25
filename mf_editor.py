#%%
from mf_read_utils import build_tree, parse_file,object_to_string
import zipfile
import os
import sys
from pathlib import Path
from xml.etree.ElementTree import Element

from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QTextEdit
)
from PySide6.QtCore import Qt


#%%


def add_tree_items(parent, data):
    if isinstance(data, dict):
        for key, value in data.items():
            item = QTreeWidgetItem([str(key), ""])
            parent.addChild(item)
            add_tree_items(item, value)

    elif isinstance(data, list):
        for i, value in enumerate(data):
            item = QTreeWidgetItem([f"[{i}]", ""])
            parent.addChild(item)
            add_tree_items(item, value)

    elif isinstance(data, Element):
        # XML element
        item = QTreeWidgetItem([data.tag, ""])
        parent.addChild(item)

        # attributes
        for k, v in data.attrib.items():
            attr_item = QTreeWidgetItem([f"@{k}", v])
            item.addChild(attr_item)

        # children
        for child in data:
            add_tree_items(item, child)

        # text
        if data.text and data.text.strip():
            text_item = QTreeWidgetItem(["#text", data.text.strip()])
            item.addChild(text_item)

    else:
        # primitive value
        item = QTreeWidgetItem(["", str(data)])
        parent.addChild(item)



class FileViewer(QWidget):
    def __init__(self, root_path):
        super().__init__()

        self.setWindowTitle("File Tree Viewer")
        self.resize(900, 600)
        self.cache = {}  # path -> parsed content

        layout = QHBoxLayout(self)

        # Left: Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Files")

        # Right: Content
        self.viewer = QTreeWidget()
        self.viewer.setHeaderLabels(["Key", "Value"])

        layout.addWidget(self.tree, 1)
        layout.addWidget(self.viewer, 2)

        self.populate_tree(root_path)

        # Connect click
        self.tree.itemClicked.connect(self.on_item_clicked)

    # ---------- Build Tree ----------
    def populate_tree(self, path: Path, parent=None):
        if parent is None:
            parent = self.tree

        for item in sorted(path.iterdir(), key=lambda p: p.name.lower()):
            tree_item = QTreeWidgetItem(parent, [item.name])
            tree_item.setData(0, Qt.UserRole, str(item))

            if item.is_dir():
                self.populate_tree(item, tree_item)

    # ---------- Handle Click ----------

    def on_item_clicked(self, item):
        data = item.data(0, Qt.UserRole)
        
        if not data:
            return

        if Path(data).is_file():
            if data in self.cache:
                parsed = self.cache[data]
            else:
                parsed = parse_file(Path(data))
                self.cache[data] = parsed
            self.viewer.clear()

            root_item = QTreeWidgetItem(self.viewer, ["root", ""])
            
            add_tree_items(root_item, parsed)

            self.viewer.expandToDepth(2)



#%%
# ---------- Run ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    foldername = "filtered_Baby_Dragon_Multicolor_FF_P1P_X1C.3mf"
    #foldername = "Baby_Dragon_Multicolor_FF_P1P_X1C - Copy.zip"
    folderpath = os.path.join(base_dir, foldername)
    output_path = os.path.join(base_dir, "extracted")
    with zipfile.ZipFile(folderpath, 'r') as zin:
        zin.extractall(output_path)
        print("output_path:", output_path)
    #input_file = os.path.join(base_dir, filename)
    #root_folder = zipfile.Path(output_path)
    print(type(Path(output_path)))
    window = FileViewer(Path(output_path))
    window.show()

    sys.exit(app.exec())