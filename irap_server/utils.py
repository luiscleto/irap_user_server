import os


def copy_grid_file(grid_file, new_file_path):
    with open(new_file_path, 'wb') as f:
        while True:
            buf = grid_file.read(16 * 1024)
            if not buf:
                break
            f.write(buf)


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for f in files:
            ziph.write(os.path.join(root, f))
