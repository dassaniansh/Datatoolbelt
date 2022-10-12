import os
import glob

files = glob.glob('instance/uploads/*')
for f in files:
    print(f'deleting {f}...')
    os.remove(f)