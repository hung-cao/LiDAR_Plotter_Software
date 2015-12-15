"""
Created on Nov 17, 2014
@author: chuxuankhoi
"""
try:
    from math import sin, cos, acos, atan, pi, degrees, radians, sqrt
    from wx import glcanvas, ID_ANY, DefaultSize, EVT_ERASE_BACKGROUND, EVT_SIZE, \
                    EVT_PAINT, EVT_LEFT_DOWN, EVT_LEFT_UP, EVT_MOTION, EVT_MOUSEWHEEL, \
                    PostEvent, PaintEvent
    from wx.glcanvas import GLContext
    import time
except ImportError:
    raise ImportError, 'Required dependency wx not present'

try:
    from OpenGL.GL import glViewport, glClear, GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glLoadIdentity, \
    glEnableClientState, glMatrixMode, GL_VERTEX_ARRAY, GL_PROJECTION, GL_MODELVIEW, GL_COLOR_ARRAY, \
    glDrawArrays, GL_POINTS, glDisableClientState, glLineWidth, glColor3f, glBegin, glVertex3f, glEnd, \
    glFlush, glGenBuffers, glBindBuffer, GL_ARRAY_BUFFER, glBufferData, glColorPointer, glVertexPointer, \
    GL_STATIC_DRAW, GL_FLOAT, GL_DEPTH_TEST, glEnable, glClearDepth, glDrawBuffer, GL_FRONT_AND_BACK, \
    GL_LINES, glGetDoublev, glGetIntegerv, GL_MODELVIEW_MATRIX, GL_PROJECTION_MATRIX, GL_VIEWPORT, \
    GLint, GLdouble, glReadPixels, GL_DEPTH_COMPONENT, glGetFloatv
    from OpenGL.GLU import gluPerspective, gluLookAt, gluUnProject
    from numpy import amax, amin, reshape, subtract, array, iterable, float32, vstack, unique
except ImportError:
    raise ImportError, 'Required dependency libs not present'
from filters import Cube2Point

defaultFOVY = 20
viewPosAngle = radians(30)
ZOOM_STEP = 0.05

class OpenGLCanvas(glcanvas.GLCanvas):
    _refreshAll = True
    _startPointIdx = 0
    _drawnPointsNum = 200000
    _isFront = True

    def __init__(self, parent, uid=ID_ANY, style=0, data=None, colors=None, size=DefaultSize):
        glcanvas.GLCanvas.__init__(self, parent, uid, style=style, size=size,
                                   attribList=[glcanvas.WX_GL_DOUBLEBUFFER, glcanvas.WX_GL_RGBA])
       
        self.init = False
        self.isSelecting = False
        self.displaySelected = False
        self.selectedPoints = []
        self.displayedSelPoints = []
        self.colorsNum = 0
        self.size = None
        self.data = None
        self.colors = None
        self.dataNum = 0
        self.angleHorizontal = 0
        self.angleVertical = 0
        self.angleFlat = 0
        self.scaleFactor = 1
        self.fovy = defaultFOVY
        self.transX = 0
        self.transY = 0
        self.is3D = False
        self.diffX = 0
        self.diffY = 0
        self.diffZ = 0
        self.startDragX = 0
        self.startDragY = 0
        self.oldTransX = 0
        self.oldTransY = 0
        self.eyeDistance = 100
        self.isDragging = False
        self.startDragging = False
        
        self.Bind(EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(EVT_SIZE, self.OnSize)
        self.Bind(EVT_PAINT, self.OnPaint)
        self.Bind(EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(EVT_MOTION, self.OnMouseMotion)
        self.Bind(EVT_MOUSEWHEEL, self.OnWheel)
        return

    def OnEraseBackground(self, event):
        pass

    def OnSize(self, event):
        size = self.size = self.GetClientSize()
        if self.init:
            glViewport(0, 0, size.width, size.height)
        event.Skip()

    def OnMouseDown(self, evt):
        self.SetFocus()
        self.startDragX = evt.GetX()
        self.startDragY = evt.GetY()
        self.oldTransX = self.transX
        self.oldTransY = self.transY
        self.startDragging = True

    def OnMouseUp(self, evt):
        curX = evt.GetX()
        curY = evt.GetY()
        self.startDragging = False
        if self.isDragging:
            self.transX = self.oldTransX + (curX - self.startDragX)
            self.transY = self.oldTransY - (curY - self.startDragY)
            self._refreshAll = True
            self.Refresh()
            self.startDragX = 0
            self.startDragY = 0
            self.isDragging = False
            self.Refresh()
            self.startDragX = 0
            self.startDragY = 0            
        elif self.isSelecting and not self.isDragging:
            reX, reY, reZ = self._Screen2Real(curX, curY)
            self.selectedPoints.append([reX, reY, reZ])
            dX, dY, dZ = self._Screen2Real(curX, curY, self.zMax)
            self.displayedSelPoints.append([dX, dY, dZ])
            self._refreshAll = True
            self.Refresh()        
        evt.Skip()

    def OnMouseMotion(self, evt):
        curX = evt.GetX()
        curY = evt.GetY()
        if self.statusBar != None:
            reX, reY, reZ = self._Screen2Real(curX, curY)
            self.statusBar.SetStatusText('X: ' + "{0:.2f}".format(reX) + 
                                         ', Y: ' + "{0:.2f}".format(reY) + 
                                         ', Z: ' + "{0:.2f}".format(reZ))
        if self.startDragging or self.isDragging:
            self.startDragging = False
            self.isDragging = True
            self.transX = self.oldTransX + (curX - self.startDragX)
            self.transY = self.oldTransY - (curY - self.startDragY)
            self._refreshAll = True
            self.Refresh()
        evt.Skip()

    def OnWheel(self, evt):
        rot = evt.GetWheelRotation()        
        delta = evt.GetWheelDelta()
        zoomDiff = rot / delta * ZOOM_STEP
        self.Zoom(zoomDiff)
        evt.Skip()

    def OnPaint(self, event):
#         startTime = time.time()
        if not self.init:
            self.context = GLContext(self)
            self.SetCurrent(self.context)
            glEnable(GL_DEPTH_TEST);
            self.init = True
            
        if self._refreshAll:  
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
#             prepareTime = time.time() - startTime
            if self.dataNum == 0:
                self.SwapBuffers()
                return
            
            eyePos = self.eyeDistance
            ex = 0.0
            ey = 0.0
            ez = 0.0
            dx = 0.0
            dy = 0.0
            dz = 0.0
            ux = 0.0
            uy = 0.0
            uz = 0.0
            xLen = max(abs(self.xMax), abs(self.xMin)) * 2
            yLen = max(abs(self.yMax), abs(self.yMin)) * 2
            zLen = max(abs(self.zMax), abs(self.zMin)) * 2
#             print 'transX, transY:', self.transX, self.transY
            if self.is3D:
                r2s = max(xLen, yLen, zLen) / self.size.width
                tX = self.transX * r2s
                tY = self.transY * r2s
                if not zLen == 0:
                    z = zLen / 2
                    if yLen / zLen > self.size.width / self.size.height:
                        z = yLen * self.size.height / self.size.width / 2
                    z *= 1.5
                    usedAngle = pi / 2 - viewPosAngle
                    cfovy1 = (eyePos - z * cos(usedAngle)) / sqrt(eyePos * eyePos + z * z - 2 * eyePos * z * cos(usedAngle))
                    cfovy2 = (eyePos - z * cos(pi - usedAngle)) / sqrt(eyePos * eyePos + z * z - 2 * eyePos * z * cos(pi - usedAngle))
                    fovy1 = degrees(acos(cfovy1))
                    fovy2 = degrees(acos(cfovy2))
                    self.fovy = 3 * max(fovy1, fovy2)
                angleX = viewPosAngle + radians(self.angleHorizontal)
                angleZ = viewPosAngle + radians(self.angleVertical)
                ex = eyePos * cos(angleZ) * cos(angleX)
                ey = eyePos * cos(angleZ) * sin(angleX)
                ez = eyePos * sin(angleZ)
                ux = 0.0
                uy = cos(pi / 2 - radians(self.angleFlat))
                uz = sin(pi / 2 - radians(self.angleFlat))
                flatAngle = radians(self.angleFlat)
                dx = -tX * cos(flatAngle) * sin(angleX) - tX * sin(flatAngle) * sin(angleZ) * sin(angleX)
                dx += tY * sin(flatAngle) * sin(angleX) - tY * cos(flatAngle) * sin(angleZ) * cos(angleX)
                dy = tX * cos(flatAngle) * cos(angleX) - tX * sin(flatAngle) * sin(angleZ) * cos(angleX)
                dy += -tY * sin(flatAngle) * cos(angleX) - tY * cos(flatAngle) * sin(angleZ) * sin(angleX)
                dz = tX * sin(flatAngle) * cos(angleZ)
                dz += tY * cos(flatAngle) * cos(angleZ)
            else:
                r2s = xLen / self.size.width
                dx = self.transX * r2s
                dy = self.transY * r2s
                dz = 0.0
                y = yLen / 2
                if xLen / yLen > self.size.width / self.size.height:
                    y = xLen * self.size.height / self.size.width / 2
                y += yLen / 10
                self.fovy = 2 * degrees(atan(y / eyePos))
                ez = eyePos
                ux = sin(radians(self.angleFlat))
                uy = cos(radians(self.angleFlat))
                uz = 0.0
            scale = 1
            if self.size != None:
                scale = float(self.size.width) / self.size.height               
#             userCalculationTime = time.time() - startTime - prepareTime
        
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            if self.is3D:
                gluPerspective(self.fovy * self.scaleFactor, scale, 0.1, self.eyeDistance * 2)
            else:
                gluPerspective(self.fovy * self.scaleFactor, scale,
                               self.eyeDistance - self.zMax - 10, self.eyeDistance - self.zMin + 10)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()
            gluLookAt(ex, ey, ez, -dx, -dy, -dz, ux, uy, uz)
            self._startPointIdx = 0
            
        if self.isDragging:
            # draw the frame instead of all data
            glLineWidth(1.0)
            glColor3f(0.0, 0.5, 0.0)
            glBegin(GL_LINES)
            glVertex3f(self.xMin, self.yMin, self.zMin)  # 1
            glVertex3f(self.xMax, self.yMin, self.zMin)  # 2
            
            glVertex3f(self.xMax, self.yMin, self.zMin)  # 2
            glVertex3f(self.xMax, self.yMax, self.zMin)  # 3
            
            glVertex3f(self.xMax, self.yMax, self.zMin)  # 3
            glVertex3f(self.xMin, self.yMax, self.zMin)  # 4
            
            glVertex3f(self.xMin, self.yMax, self.zMin)  # 4
            glVertex3f(self.xMin, self.yMin, self.zMin)  # 1
            
            glVertex3f(self.xMin, self.yMin, self.zMin)  # 1
            glVertex3f(self.xMin, self.yMin, self.zMax)  # 5
            
            glVertex3f(self.xMin, self.yMin, self.zMax)  # 5
            glVertex3f(self.xMax, self.yMin, self.zMax)  # 6
            
            glVertex3f(self.xMax, self.yMin, self.zMax)  # 6
            glVertex3f(self.xMax, self.yMax, self.zMax)  # 7
            
            glVertex3f(self.xMax, self.yMax, self.zMax)  # 7
            glVertex3f(self.xMin, self.yMax, self.zMax)  # 8
            
            glVertex3f(self.xMin, self.yMax, self.zMax)  # 8
            glVertex3f(self.xMin, self.yMin, self.zMax)  # 5
            
            glVertex3f(self.xMax, self.yMin, self.zMin)  # 2
            glVertex3f(self.xMax, self.yMin, self.zMax)  # 6
            
            glVertex3f(self.xMax, self.yMax, self.zMin)  # 3
            glVertex3f(self.xMax, self.yMax, self.zMax)  # 7
            
            glVertex3f(self.xMin, self.yMax, self.zMin)  # 4
            glVertex3f(self.xMin, self.yMax, self.zMax)  # 8
            
            glEnd()
            glFlush()
            self.SwapBuffers()
            return
            
        glEnableClientState(GL_VERTEX_ARRAY)
        if self.colorsNum >= self.dataNum:
            glEnableClientState(GL_COLOR_ARRAY)
            
        glDrawBuffer(GL_FRONT_AND_BACK)
                
        if self._startPointIdx + self._drawnPointsNum >= self.dataNum:
            glDrawArrays(GL_POINTS, self._startPointIdx, self.dataNum - self._startPointIdx)
            if self.displaySelected:
                selNum = len(self.displayedSelPoints)
                if selNum >= 2:
                    glLineWidth(2.0)
                    glColor3f(0.0, 1.0, 0.0)
                    glBegin(GL_LINES)
                    for i in xrange(1, selNum):
                        glVertex3f(self.displayedSelPoints[i - 1][0],
                                   self.displayedSelPoints[i - 1][1],
                                   self.displayedSelPoints[i - 1][2])
                        glVertex3f(self.displayedSelPoints[i][0],
                                   self.displayedSelPoints[i][1],
                                   self.displayedSelPoints[i][2])
                    glVertex3f(self.displayedSelPoints[selNum - 1][0],
                               self.displayedSelPoints[selNum - 1][1],
                               self.displayedSelPoints[selNum - 1][2])
                    glVertex3f(self.displayedSelPoints[0][0],
                               self.displayedSelPoints[0][1],
                               self.displayedSelPoints[0][2])
                    glEnd()
            self._refreshAll = True
        else:
            glDrawArrays(GL_POINTS, self._startPointIdx, self._drawnPointsNum)
            self._refreshAll = False
            self._isFront = not self._isFront
            self._startPointIdx += self._drawnPointsNum if self._isFront else 0
            
        glDisableClientState(GL_VERTEX_ARRAY)
        if self.colorsNum >= self.dataNum:
            glDisableClientState(GL_COLOR_ARRAY)
        glFlush()
        self.SwapBuffers()
#         drawingTime = time.time() - startTime - prepareTime - userCalculationTime
#         print "preparation time:", str(prepareTime), "user calculation time:",\
#             str(userCalculationTime), "drawing time:", str(drawingTime)
        if not self._refreshAll:
            PostEvent(self, PaintEvent())
        event.Skip()

    def SetStatusBar(self, statusBar):
        self.statusBar = statusBar

    def RemoveStatusBar(self):
        self.statusBar = None
        return
    
    # data and colors are stored in numpy's float32 array
    def SetDisplayingItems(self, data, dataLen, colors):
        self.data = data
        self.colors = colors
        
        self.xcount = len(unique(data[:, 0]))
        self.ycount = len(unique(data[:, 1]))
        
        workingData = self.data
        workingColors = self.colors
        self.dataNum = dataLen
        self.colorsNum = self.dataNum
        
        maxVals = amax(workingData, axis=0)
        self.xMax = maxVals[0]
        self.yMax = maxVals[1]
        self.zMax = maxVals[2]
        minVals = amin(workingData, axis=0)
        self.xMin = minVals[0]
        self.yMin = minVals[1]
        self.zMin = minVals[2]
#         print "Max before offset:", self.xMax, self.yMax, self.zMax
#         print "Min before offset:", self.xMin, self.yMin, self.zMin
        self.diffX = (self.xMax + self.xMin) / 2
        self.diffY = (self.yMax + self.yMin) / 2
        self.diffZ = (self.zMax + self.zMin) / 2
#         print "Offset:", self.diffX, self.diffY, self.diffZ
        workingData = subtract(workingData, array([self.diffX, self.diffY, self.diffZ], float32))
        # recollect limitations
        maxVals = amax(workingData, axis=0)
        self.xMax = maxVals[0]
        self.yMax = maxVals[1]
        self.zMax = maxVals[2]
        minVals = amin(workingData, axis=0)
        self.xMin = minVals[0]
        self.yMin = minVals[1]
        self.zMin = minVals[2]
#         print "Max:", self.xMax, self.yMax, self.zMax
#         print "Min:", self.xMin, self.yMin, self.zMin
        self.eyeDistance = 100 * max(abs(self.xMax), abs(self.xMin),
                                     abs(self.yMax), abs(self.yMin),
                                     abs(self.zMax), abs(self.zMin))
#         print "eye distance:", self.eyeDistance
        self.vertices_vbo = glGenBuffers(1)
        glEnableClientState(GL_VERTEX_ARRAY)
        glBindBuffer(GL_ARRAY_BUFFER, self.vertices_vbo)
        glBufferData(GL_ARRAY_BUFFER, workingData.nbytes, workingData, GL_STATIC_DRAW)
        glVertexPointer(3, GL_FLOAT, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
                
        self.colors_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo)
        glBufferData(GL_ARRAY_BUFFER, workingColors.nbytes, workingColors, GL_STATIC_DRAW)
        glColorPointer(3, GL_FLOAT, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        print "Points and color is ready"

    # Used in case the old data is reused, thus, the input length should be equal or greater than the old data length
    def SetColors(self, colors):
        if not iterable(colors):
            return
        if len(colors) < self.dataNum:
            return
        self.colors = colors
        workingColors = self.colors
#         workingData, self.dataNum, workingColors = self.GetWorkingSet(self.data, self.dataNum, self.colors)
        self.colorsNum = len(workingColors)
        
        self.colors_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.colors_vbo)
        glBufferData(GL_ARRAY_BUFFER, workingColors.nbytes, workingColors, GL_STATIC_DRAW)
        glColorPointer(3, GL_FLOAT, 0, None)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        print "Color is ready"
    
    # On reserved, used to simplify the drawing data
    def GetWorkingSet(self, data, dataLength, colors):
        if((dataLength == 0) or (colors is None) or (len(colors) < dataLength)):
            return data, dataLength, colors
        
        # Reduce data number
        return Cube2Point(data, dataLength, colors, max(self.size.width, self.size.height))        
#         return workingData, workingDataNum, workingColors

    def ResetView(self):
        self.angleHorizontal = 0
        self.angleVertical = 0
        self.angleFlat = 0
        self.scaleFactor = 1
        self.transX = 0
        self.transY = 0
        self._refreshAll = True
        self.Refresh()

    def RotateHorizontal(self, angle=10.0):
        self.angleHorizontal = angle
        self._refreshAll = True
        self.Refresh()

    def RotateVeritcal(self, angle=10.0):
        self.angleVertical = angle
        self._refreshAll = True
        self.Refresh()

    def RotateFlat(self, angle=10.0):
        self.angleFlat = angle
        self._refreshAll = True
        self.Refresh()

    def Zoom(self, factor=1):
        while factor + self.scaleFactor < 0:
            return
        self.scaleFactor += factor
        self._refreshAll = True
        self.Refresh()

    def Move(self, dx=0.0, dy=0.0):
        self.transX += dx
        self.transY += dy
        self._refreshAll = True
        self.Refresh()

    def Set3D(self, is3D=True):
        self.is3D = is3D
        self.ResetView()
        self._refreshAll = True
        self.Refresh()
        
    def SetSelecting(self, isSelecting = True):
        if not self.isSelecting:
            self.selectedPoints = []
            self.displayedSelPoints = []
        self.isSelecting = isSelecting
        if self.isSelecting:
            self.displaySelected = True
        
    def ClearSelected(self):
        self.selectedPoints = []
        self.displayedSelPoints = []
        self._refreshAll = True
        self.Refresh()
    
    def GetSelectedPoints(self):
        if len(self.selectedPoints) <= 2:
            return []
        ret = []
        for x in self.selectedPoints:
            ret.append([x[0] + self.diffX, x[1] + self.diffY])
        return ret
        
    def _Screen2Real(self, x, y, expZ=0.0):
        '''
        Return the x and y in real coordination if the input is the x and y in screen coordination
        http://nehe.gamedev.net/article/using_gluunproject/16013/
        Inputs:
            - x, y: coordinates get from mouse in screen coordination
            - expZ: expected Z of the real coordinates
        Outputs: coordinates in the real world
        '''
        if not self.init:
            return 0, 0, 0
        
        projection = glGetDoublev(GL_PROJECTION_MATRIX)
        modelview = glGetDoublev(GL_MODELVIEW_MATRIX)
        viewport = glGetIntegerv(GL_VIEWPORT)
        
        winX = float(x)
        winY = float(viewport[3]) - float(y)
#         winZ = glReadPixels(x, int(winY), 1, 1, GL_DEPTH_COMPONENT, GL_FLOAT)
        
        try:
            posXF, posYF, posZF = gluUnProject(winX, winY, 1, modelview, projection, viewport)
            posXN, posYN, posZN = gluUnProject(winX, winY, -1, modelview, projection, viewport)
            posZ = expZ
            posX = (posZ - posZN) / (posZF - posZN) * (posXF - posXN) + posXN
            posY = (posZ - posZN) / (posZF - posZN) * (posYF - posYN) + posYN
#             posX, posY, posZ = gluUnProject(winX, winY, winZ, modelview, projection, viewport)
        except:
            return 0, 0, 0
        return posX, posY, posZ
