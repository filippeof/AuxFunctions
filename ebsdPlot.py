from PIL import Image
import numpy as np
import pandas as pd
import sys
from os.path import splitext
from itertools import takewhile



def readByToken(hl,token):
    for line in hl:
        if token in line:
            line = line.replace(token,'')
            line.strip()
            return line

fname = sys.argv[1] # Read file name from first bash input
# fname= 'path/to/file.ang'
file_name, extension = splitext(fname)

if extension=='.ang': # EDAX file
    # ColumnNames = {'Euler 1' 'Euler 2' 'Euler 3' 'X' 'Y' 'IQ' 'CI' 'Fit' 'PRIAS_BS' 'PRIAS_CS' 'PRIAS_TS'  'unknown4'  'unknown5' 'unknown6' 'unknown7'};
    cols2read = [3, 4, 5]  # x,y,IQ
    CommentStyle="#"

    with open(fname, 'r') as fobj:
        headiter = takewhile(lambda s: s.startswith(CommentStyle), fobj)
        hl = list(headiter)
        gridType = readByToken(hl, '# GRID: ')
        nRows = int(readByToken(hl, '# NROWS:'))
        nCols = int(readByToken(hl, '# NCOLS_ODD:'))
        stepSizeX = float(readByToken(hl, '# XSTEP:'))
        stepSizeY = float(readByToken(hl, '# YSTEP:'))

    file_data = pd.read_csv(fname, sep=' ',comment=CommentStyle, usecols=cols2read, skipinitialspace=True, header=None)

    x = np.array(file_data[cols2read[0]], dtype=float)
    y = np.array(file_data[cols2read[1]], dtype=float)
    prop = np.array(file_data[cols2read[2]], dtype=float)

    prop = 255*prop/max(prop) #Normalize grayscale

    max_x = max(x)
    min_x = min(x)
    max_y = max(y)
    min_y = min(y)
    # stepSizeX=x[2]-x[1]
    # stepSizeY=stepSizeX*np.sin(np.pi/3)
    # nRows=np.array((((max_x-min_x)/stepSizeX)+1), dtype=int)
    # nCols=np.array((((max_y-min_y)/stepSizeY)+1), dtype=int)

    print stepSizeX,stepSizeY,nRows,nCols

    x_id = np.array(x/stepSizeY, dtype=int)

    y_id = np.array(y/stepSizeX, dtype=int)

    img = np.zeros((1, nCols*nRows))

    # img = np.zeros((nCols,nRows))
    # for i in range(len(x_id)):
    #     img[y_id[i], x_id[i]]=prop[i]
    # img=img[~np.all(img == 0, axis=1)]

    idsR = ((x_id+1) + y_id*nCols)-1

    img[0][idsR] = prop
    img = img.reshape(nRows,nCols)

I= Image.fromarray(img)
I.show()
# I.convert("L")
# I.save('/Users/fereira/Documents/MATLAB/test.png','PNG')
