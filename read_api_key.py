import sys  
import os

def readKey(filePath):
    print('read file {}'.format(filePath))
    if not os.path.isfile(filePath):
        print("File path {} does not exist. Exiting...".format(filePath))
        sys.exit()
    
    with open(filePath) as fp:
        keys = fp.readlines()
       
    keys[0] = keys[0].strip()
    keys[1] = keys[1].strip()
    
    return keys
