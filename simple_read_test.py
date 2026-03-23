import zipfile
import os
import shutil
import tempfile

REMOVE_PREFIXES = [
    "Metadata/",
    "Thumbnails/",
    "Preview/",
    "_rels/",
]

KEEP_FILES = [
    "[Content_Types].xml",
]


input_file = "Baby_Dragon_Multicolor_FF_P1P_X1C.3mf"
with tempfile.TemporaryDirectory() as tmpdir:
    with zipfile.ZipFile(input_file, 'r') as zin:
        zin.extractall(tmpdir)

for root, dirs, files in os.walk(tmpdir, topdown=True):
    for name in files:
        rel_path = os.path.relpath(os.path.join(root, name), tmpdir)
        print(name)
        #if any(rel_path.startswith(prefix) for prefix in REMOVE_PREFIXES):
        #    os.remove(os.path.join(root, name))

        # Repack
        #with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zout:
        #    for root, dirs, files in os.walk(tmpdir):
        #        for file in files:
        #            full_path = os.path.join(root, file)
        #            rel_path = os.path.relpath(full_path, tmpdir)
         #           zout.write(full_path, rel_path)

