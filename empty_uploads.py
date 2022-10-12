import os
import glob
import time

files = glob.glob('instance/uploads/*')
for f in files:
    x=os.stat(f)
    Result=(time.time()-x.st_mtime)
    print(f'File\'s age is {Result}')
    if Result > 86400:
        #os.remove(f)
        print(f'Deleting {f}...')