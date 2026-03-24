#%%
from mf_read_utils import build_tree, parse_file
import zipfile
import os
import sys
from pathlib import Path



from PySide6.QtWidgets import (
    QApplication, QWidget, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QTextEdit
)
from PySide6.QtCore import Qt


#%%

class FileViewer(QWidget):
    def __init__(self, root_path):
        super().__init__()

        self.setWindowTitle("File Tree Viewer")
        self.resize(900, 600)

        layout = QHBoxLayout(self)

        # Left: Tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabel("Files")

        # Right: Content
        self.viewer = QTextEdit()
        self.viewer.setReadOnly(True)

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
        path = Path(item.data(0, Qt.UserRole))
        name = path.name.lower()
        if path.is_file():
            if path.suffix in [".json", ".xml", ".rels", ".model", ".config"] or name.endswith(".rels"):
                content = parse_file(path)
                self.viewer.setText(content)
            else:
                self.viewer.setText("Not a supported settings file")

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