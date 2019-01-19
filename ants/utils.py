import sys  
import os
import json
import locale

def readKey(filePath):
    print('read file {}'.format(filePath))
    if not os.path.isfile(filePath):
        print("File path {} does not exist. Exiting...".format(filePath))
        sys.exit()
    
    try:
        with open(filePath) as fp:
            result = json.load(fp)
    except Exception as exp:
        print("Can't load json : {}".format(exp))
        print("Program exit")
        sys.exit()

    return result

def saveBinFile(fileName, data):
    f = open(fileName,'wb')
    f.write(data)
    f.close()
    
def loadBinFile(fileName): 
    f = open(fileName,'rb')
    data = f.read()
    f.close()
    return data
    
def krwFormat(number) :
    s = '%d' % number
    groups = []
    while s and s[-1].isdigit():
        groups.append(s[-3:])
        s = s[:-3]
    return s + ','.join(reversed(groups))