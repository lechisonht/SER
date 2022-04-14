import os
import shutil

def create_path(path, TOKEN=None):
    if TOKEN:
        path = os.path.join(path, TOKEN)
    if not os.path.exists(path):
        os.makedirs(path)
    return path

def clear_file(path, TOKEN=None):
    if TOKEN:
        path = os.path.join(path, TOKEN)
    # create_path(path)
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))

def clear_path(path, TOKEN=None):
    if TOKEN:
        path = os.path.join(path, TOKEN)
    try:
        shutil.rmtree(path)
    except:
        None