'''
Created on 3 Feb 2015

@author: khoicx
'''

import numpy

class Polygon:
    '''
    Represent a 2D polygon, including the vertices and the method that user want to work with a polygon
    '''
    vertices = []
    
    def __init__(self, vertices):
        '''
        Constructor
        Input is a sequence of point representations (sequence including x and y)
        '''
        self.vertices = numpy.array(vertices, numpy.float32)
        
    def AddVertex(self, vertex):
        if vertex in self.vertices:
            raise ValueError("The vertex existed")
        self.vertices = numpy.append(self.vertices, vertex, 0)
        
    def RemoveVertex(self, vertex):
        self.vertices = numpy.delete(self.vertices, numpy.argwhere(numpy.all(self.vertices == vertex, 1)), 0)
        
    def InsertVertex(self, vertex, index):
        self.vertices = numpy.insert(self.vertices, index, vertex, 0)
        
    def PointsInPolygon(self, points):
        '''
        Try to vectorize the test when the number of points is huge
        '''
        if isinstance(points, numpy.ndarray): # treat as numpy array
            # find x-max, y-max, x-min, y-min of vertices
            mx = numpy.amax(self.vertices, 0)
            mn = numpy.amin(self.vertices, 0)
            # eliminate points that are surely outside of the polygon 
            # (the coordination is outside of the polygon's max and min coordination)
            elim = numpy.logical_and(numpy.logical_and(points[:, 1] >= mn[1], points[:, 1] <= mx[1]),
                                     numpy.logical_and(points[:, 0] >= mn[0], points[:, 0] <= mx[0]))
            # iterate over the possible points
            it = numpy.nditer(elim,flags=['multi_index'], op_flags=['readwrite'])                               
            while not it.finished:
                if elim[it.multi_index]:
                    elim[it.multi_index] = points[it.multi_index] in self
                it.iternext()
            return elim
        else:
            return [x in self for x in points]
        
    def __getitem__(self, index):
        '''
        Convenient way to access the vertex of the polygon
        '''
        return self.vertices[index]
    
    def __contains__(self, point):
        '''
        Check a point is in/on the polygon or not
        '''
        vertices = self.vertices.tolist()        
        polyCorners = len(self.vertices)
        j = polyCorners - 1
        oddNodes = False
        x = point[0]
        y = point[1]
        
        for i in xrange(polyCorners):
            v1 = vertices[i]
            v2 = vertices[j]
            if ((v1[1] <= y and v2[1] >= y or v2[1] <= y and v1[1] >= y) and 
                (v1[0] <= x or v2[0] <= x)):
                if v2[1] == v1[1]:
                    oddModes ^= (v1[0] <= x)
                else:
                    oddNodes ^= ((v1[0] + (y- v1[1]) / (v2[1] - v1[1]) * (v2[0] - v1[0])) <= x)
            j = i
 
        return oddNodes
    
    def __str__(self):
        return str(self.vertices.tolist())