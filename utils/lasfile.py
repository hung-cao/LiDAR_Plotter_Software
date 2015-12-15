'''
Created on 12 Jan 2015

@author: khoicx
'''

from laspy.file import File
import numpy
import datetime

class LASInfo:
    filename = ""
    version = ""
    sourceID = ""
    identifier = ""
    software = ""
    creationTime = ""
    pointsNum = 0
    xMin = 0
    xMax = 0
    yMin = 0
    yMax = 0
    zMin = 0
    zMax = 0
    compression = False
    
    def toString(self):
        ret = "filename: " + self.filename + "\n"
        ret = ret + "version: " + self.version + "\n"
        ret = ret + "sourceID: " + str(self.sourceID) + "\n"
        ret = ret + "identifier: " + self.identifier + "\n"
        ret = ret + "software: " + self.software + "\n"
        ret = ret + "creationTime: " + self.creationTime + "\n"
        ret = ret + "pointsNum: " + str(self.pointsNum) + "\n"
        ret = ret + "x range: " + str(self.xMin) + " to " + str(self.xMax) + "\n"
        ret = ret + "y range: " + str(self.yMin) + " to " + str(self.yMax) + "\n"
        ret = ret + "z range: " + str(self.zMin) + " to " + str(self.zMax) + "\n"
        ret = ret + "compression: " + str(self.compression)
        return ret

class LASFile(object):
    def __init__(self, fileName):
        self.__file = File(fileName, mode='r')
    
    def GetPoints(self):
        compressedX = self.__file.X
        scaleX = self.__file.header.scale[0]
        offsetX = self.__file.header.offset[0]
        X = compressedX * scaleX + offsetX
        compressedY = self.__file.Y
        scaleY = self.__file.header.scale[1]
        offsetY = self.__file.header.offset[1]
        Y = compressedY * scaleY + offsetY
        compressedZ = self.__file.Z
        scaleZ = self.__file.header.scale[2]
        offsetZ = self.__file.header.offset[2]
        Z = compressedZ * scaleZ + offsetZ
        points = numpy.vstack((X, Y, Z)).T
        return points
    
    def GetIntensity(self):
        try:
            return self.__file.Intensity
        except:
            return None
    
    def GetColor(self):
        try:
            blue = self.__file.blue
            green = self.__file.green
            red = self.__file.red
            colors = numpy.vstack((red, green, blue)).T
            colors = numpy.divide(colors, 255.0) # conver from (0:255, 0:255, 0:255) to (0.0:1.0, 0.0:1.0, 0.0:1.0)
            return colors
        except:
            return None
    
    def GetInfor(self):
        info = LASInfo()
        header = self.__file.header
        info.filename = self.__file.filename
        info.version = header.version
        info.sourceID = header.file_source_id
        info.identifier = header.system_id
        info.software = header.software_id
        if not header.date is None:
            delta = header.date - datetime.datetime(header.date.year, 1, 1, 0, 0)
            info.creationTime = str(delta.days) + "/" + str(header.date.year)
        else:
            info.creationTime = 'No information'
        info.pointsNum = sum(header.point_return_count)
        info.xMin = header.min[0]
        info.yMin = header.min[1]
        info.zMin = header.min[2]
        info.xMax = header.max[0]
        info.yMax = header.max[1]
        info.zMax = header.max[2]
        info.compression = False
        return info
    
    def GetReturns(self):
        flags = self.__file.flag_byte
        return numpy.divide(flags & int('11100000', 2), 32)
    
    def GetPointReturnCount(self):
        return self.__file.header.point_return_count
    
if __name__ == '__main__':
    fileName = "D:\\Study in UCD\\COMP47330 Practical Android Programming\\Projects\\Read_las\\data1.las"
    lFile = LASFile(fileName)
#     points = lFile.GetPoints()
#     print "points:\n", points
#     intensities = lFile.GetIntensity()
#     print "intensities:\n", intensities
#     colors = lFile.GetColor()
#     print "colors:\n", colors
    info = lFile.GetInfor()
    print "information from file:\n", info.toString()
    ret = lFile.GetReturns()
    print numpy.amax(ret)