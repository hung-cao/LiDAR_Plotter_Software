'''
Created on 16 Dec 2014

@author: khoicx
'''
import numpy
import math
import collections

def Cube2Point(data, dataLen, colors, maxSize):
    tmpData = []
    retLen = 0
    retColors = None
    
    # Sort data and colors along x, y, z
    iData = numpy.zeros((dataLen, 6), numpy.float32)
    for i in xrange(3):
        iData[:,i] = data[:, i]
        iData[:, i + 3] = colors[:, i]
    iData.view(str(iData.dtype) + ',' + str(iData.dtype) + ',' +str(iData.dtype)).sort(order=['f0', 'f1', 'f2'], axis=0)
#     print iData
    
    # Calculate cube's dimensions
    maxVals = numpy.amax(iData, axis=0)
    xMax = maxVals[0]
    yMax = maxVals[1]
    zMax = maxVals[2]
    minVals = numpy.amin(iData, axis=0)
    xMin = minVals[0]
    yMin = minVals[1]
    zMin = minVals[2]
    xRange = xMax - xMin
    yRange = yMax - yMin
    zRange = zMax - zMin
    maxRange = 0
    if(xRange == 0 and yRange == 0 and zRange == 0):
        return [xMax, yMax, zMax], 1, [[iData[3,0], iData[4, 0], iData[4, 0]]]
    elif(xRange == 0 and yRange == 0):
        maxRange = zRange
    elif(yRange == 0 and zRange == 0):
        maxRange = xRange
    elif(xRange == 0 and zRange == 0):
        maxRange = yRange
    elif(xRange == 0):
        maxRange = max(yRange, zRange)
    elif(yRange == 0):
        maxRange = max(xRange, zRange)
    elif(zRange == 0):
        maxRange = max(yRange, xRange)
    else:
        maxRange = max(xRange, yRange, zRange) 
    cubeLength = maxRange / maxSize
    cubeNumX = int(math.ceil(xRange / cubeLength)) if xRange > 0 else 1
    cubeNumY = int(math.ceil(yRange / cubeLength)) if yRange > 0 else 1
    cubeNumZ = int(math.ceil(zRange / cubeLength)) if zRange > 0 else 1
    print "Cube dim: ", cubeLength
    print "Cubes number: x:", cubeNumX, "y:", cubeNumY, "z:", cubeNumZ
    
    # In each cube in drawing space, try to reduce the point number
    for i in xrange(1, cubeNumX + 1):
        for j in xrange(1, cubeNumY + 1):
            for k in xrange(1, cubeNumZ + 1):
                print i, j, k
                # get all points in the current cube                
                cubeMinX = (i - 1) * cubeLength + xMin
                cubeMaxX = i * cubeLength + xMin
                lx = numpy.searchsorted(iData[:, 0], cubeMinX, 'right')
                ux = numpy.searchsorted(iData[:, 0], cubeMaxX, 'left')
#                 print "lower X, upper X:", lx, ux
                cubeMinY = (j - 1) * cubeLength + yMin
                cubeMaxY = j * cubeLength + yMin
                ly = numpy.searchsorted(iData[lx:ux + 1, 1], cubeMinY, 'right')
                uy = numpy.searchsorted(iData[lx:ux + 1, 1], cubeMaxY, 'left')
#                 print "lower Y, upper Y:", ly, uy
                cubeMinZ = (k - 1) * cubeLength + zMin
                cubeMaxZ = k * cubeLength + zMin                
                lz = numpy.searchsorted(iData[(lx + ly):(lx + uy + 1), 2], cubeMinZ, 'right')
                uz = numpy.searchsorted(iData[(lx + ly):(lx + uy + 1), 2], cubeMaxZ, 'left')
#                 print "lower Z, upper Z:", lz, uz
                lower = lx + ly + lz
                upper = lx + uz + 1
#                 print "lower, upper", lower, upper
                pts = iData[lower:upper]
#                 print "pts:\n", pts
                usedCount = len(pts)
                # level 1: if all points have the same color, they are one
                if usedCount > 1:
                    if len(collections.Counter(tuple([tuple(x) for x in pts[0:usedCount, 3:6]]))):
                        newPts = pts[0].tolist()
                        newPts[0] = (cubeMinX + cubeMaxX) / 2
                        newPts[1] = (cubeMinY + cubeMaxY) / 2
                        newPts[2] = (cubeMinZ + cubeMaxZ) / 2
                        tmpData.append(newPts)
                    else:
                        tmpData.append(pts[0:usedCount].tolist())
                elif usedCount == 1:
                    tmpData.append(pts[0:usedCount].tolist()[0])
    print "found:", tmpData
    retData = numpy.array(tmpData, numpy.float32)
    ncols = retData.shape[1]
    dtype = retData.dtype.descr * ncols
    struct = retData.view(dtype)
    
    uniq = numpy.unique(struct)
    uniq = uniq.view(retData.dtype).reshape(-1, ncols)
    print "return:\n", uniq
    return uniq[:, 0:3], len(uniq), uniq[:, 3:6]

import time

# Create fake data to test
def GenData():
    dataLen = 100000
    data = [[i - dataLen / 2, i - dataLen / 2, i - dataLen / 2] for i in xrange(dataLen)]
    colors = [[0.5, 0.75, 1.0] for i in xrange(dataLen)]
    return numpy.array(data, numpy.float32), dataLen, numpy.array(colors, numpy.float32)

if __name__ == '__main__':
    # create data
    data, dataLen, colors = GenData()
    maxSize = 200
    print "length before simplifying:", dataLen
#     print "data before simplifying:\n", data
#     print "colors before simplifying:\n", colors
    print "max size:", maxSize
    # run function
    startTime = time.time()
    newData, newLen, newColors = Cube2Point(data, dataLen, colors, maxSize)
    print "Time for simplifying:", (time.time() - startTime)
    print "length after simplifying:", newLen
#     print "data after simplifying:\n", newData
#     print "colors after simplifying:\n", newColors