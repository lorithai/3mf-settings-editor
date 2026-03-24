#%%
import zipfile
import os
import shutil

base_dir = os.path.dirname(os.path.abspath(__file__))

#%%
input_file = os.path.join(base_dir, "Baby_Dragon_Multicolor_FF_P1P_X1C.3mf")
output_path = os.path.join(base_dir, "extracted")
with zipfile.ZipFile(input_file, 'r') as zin:
    zin.extractall(output_path)
    print("output_path:", output_path)


for root, dirs, files in os.walk(output_path, topdown=True):
    print("dirs:", dirs, "files:", files)
    for name in files:
        rel_path = os.path.relpath(os.path.join(root, name), output_path)
        #print(rel_path)
        #if any(rel_path.startswith(prefix) for prefix in REMOVE_PREFIXES):
        #    os.remove(os.path.join(root, name))

        # Repack
        #with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zout:
        #    for root, dirs, files in os.walk(output_path):
        #        for file in files:
        #            full_path = os.path.join(root, file)
        #            rel_path = os.path.relpath(full_path, tmpdir)
         #           zout.write(full_path, rel_path)

#%%