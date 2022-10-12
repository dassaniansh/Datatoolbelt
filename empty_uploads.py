import os
import glob

files = glob.glob('instances/uploads')
for f in files:
    os.remove(f)