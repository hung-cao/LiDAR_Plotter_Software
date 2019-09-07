'''
Created on Oct 14, 2014

@author: Van-Hung Cao & chuxuankhoi
'''
from wx._gdi import NullBitmap

try:
    # import widgets
    from wx import App, Frame, MenuBar, Menu, MenuItem, Image, SplitterWindow, \
        Panel, StaticText, TextCtrl, BoxSizer, BusyInfo, GetApp, AboutDialogInfo, \
        AboutBox, FileDialog
        
    import math
    import time
    import os
    import json
    
    # import constants
    from wx import DEFAULT_FRAME_STYLE, EVT_MENU, TB_HORIZONTAL, NO_BORDER, TB_FLAT, \
    TB_TEXT, BITMAP_TYPE_PNG, EVT_TOOL, RAISED_BORDER, EXPAND, MAXIMIZE, \
    VERTICAL, HORIZONTAL, ITEM_RADIO, TOP, LEFT, RIGHT, ALIGN_CENTER_VERTICAL, \
    ALIGN_CENTRE_VERTICAL, ALL, ID_OK, OPEN
        
    from numpy import array, float32, reshape, amin, amax, zeros, empty, argwhere, \
                        multiply, divide, add, subtract, iterable, ones, vectorize, \
                        arange, ones_like, array_str, unique    
    
    from opengl.openglcanvas import OpenGLCanvas
    from dialogs.colorrangedlg import ColorRangeDlg
    from dialogs.colortabledlg import ColorTableDlg
    from utils.lasfile import LASFile, LASInfo
    from dialogs.returnselectiondlg import ReturnSelectionDlg
    from utils.shapes import Polygon
except ImportError:
    raise ImportError, 'Required dependencies not present'

# MENU_FILE = 100
MENU_FILE_OPEN = 101
MENU_FILE_QUIT = 105
# MENU_VIEW = 110
MENU_VIEW_MODE = 111
MENU_VIEW_MODE_2D = 1111
MENU_VIEW_MODE_3D = 1112
MENU_VIEW_ZOOM = 112
MENU_VIEW_ZOOMIN = 1121
MENU_VIEW_ZOOMOUT = 1122
MENU_VIEW_ROTATE = 113
MENU_VIEW_ROTATE_UP = 1131
MENU_VIEW_ROTATE_DOWN = 1132
MENU_VIEW_ROTATE_LEFT = 1133
MENU_VIEW_ROTATE_RIGHT = 1134
MENU_VIEW_ROTATE_CLK = 1135
MENU_VIEW_ROTATE_ANTICLK = 1136
MENU_VIEW_MOVE = 114
MENU_VIEW_MOVE_UP = 1141
MENU_VIEW_MOVE_DOWN = 1142
MENU_VIEW_MOVE_LEFT = 1143
MENU_VIEW_MOVE_RIGHT = 1144
MENU_VIEW_RESET = 115
MENU_VIEW_INFO = 116
MENU_VIEW_SELECT = 118
MENU_VIEW_CLEAR_SELECTED = 119
# MENU_SETTING = 120
MENU_SETTING_COLORR = 121
MENU_SETTING_COLORR_INT = 1211
MENU_SETTING_COLORR_Z = 1212
MENU_SETTING_COLORR_LAB = 1213
MENU_SETTING_COLORM = 122
MENU_SETTING_COLORM_RAW = 1221
MENU_SETTING_COLORM_INT = 1222
MENU_SETTING_COLORM_Z = 1223
MENU_SETTING_COLORM_LAB = 1224
MENU_SETTING_COLORR_RET = 1225
MENU_SETTING_COLORM_RET = 1226
MENU_SETTING_PTN = 123
MENU_SETTING_PNT_ALL = 1231
MENU_SETTING_PNT_RET = 1232
MENU_SETTING_PNT_POL = 1233
# MENU_HELP = 130
MENU_HELP_ABOUT = 131
# MENU_TOOLS = 140
MENU_TOOLS_LAS2TXT = 141

TOOLBAR_OPEN = 201
TOOLBAR_EXIT = 202
TOOLBAR_ROTATE_CLOCKWISE = 203
TOOLBAR_ROTATE_COUNTER = 204
TOOLBAR_ZOOMIN = 205
TOOLBAR_ZOOMOUT = 206
TOOLBAR_MOVEUP = 207
TOOLBAR_MOVEDOWN = 208
TOOLBAR_MOVELEFT = 209
TOOLBAR_MOVERIGHT = 210
TOOLBAR_RESETVIEW = 211
TOOLBAR_3D = 212
TOOLBAR_ROTATE_UP = 213
TOOLBAR_ROTATE_DOWN = 214
TOOLBAR_ROTATE_LEFT = 215
TOOLBAR_ROTATE_RIGHT = 216
TOOLBAR_SHOWINF = 217
TOOLBAR_PTN_ALL = 218
TOOLBAR_SELECT = 219
TOOLBAR_PTN_RET = 220
TOOLBAR_PTN_POL = 221
TOOLBAR_CLEAR_SELECTED = 222

SPLITTER_WIN = 300
SPLITTER_WIN_INPUT = 301
SPLITTER_WIN_DRAW = 302

INPUT_PANEL_WIDTH = 300
INPUT_PANEL_LBLW = 60

ZOOMIN_STEP = 0.01
ZOOMOUT_STEP = 0.05

class MainWindow(Frame):
    def __init__(self, parent=None, uid=-1, title="LiDAR Plotter"):
        Frame.__init__(
                self, parent, uid, title, size=(1000, 800),
                style=DEFAULT_FRAME_STYLE | MAXIMIZE
        )
        # Additional source code here
        self.createMenu()
        self.createToolBar()
        self.CreateStatusBar()
        self.createWorkingSpace()
        self.currentAngleHorizontal = 0
        self.currentAngleVertical = 0
        self.currentAngleFlat = 0
        self.dZoomFactor = 1
        self.dX = 0
        self.dY = 0
        self.currentDZ = 0
        self.is3D = False
        self.Enable3DFeatures(self.is3D)
        self.colorMode = "rawColor"  # 4 modes: rawColor, intensity, z, label, return
        self.maxIColor = [0.0, 1.0, 0.0]
        self.minIColor = [1.0, 0.0, 0.0]
        self.minZColor = [0.0, 1.0, 0.0]
        self.maxZColor = [1.0, 0.0, 0.0]
        self.rawColors = None
        self.usedColors = None
        self.intensities = None
        self.rawData = None
        self.labels = None
        self.info = None
        self.lab2colDict = {}
        self.returns = None
        self.workingReturns = None
        self.ret2colDict = {}
        self.pointMode = 'all'
        self.dataUsedIdx = None
        self.showInfo = False
        self.initializeData = True
        self.isSelecting = False
        self.selectedPoints = []
        self.LoadSavedSetting()
        self.Show(True)
        
    def __del__(self):
        self.SaveCurrentSetting()
        
    def LoadSavedSetting(self):
        try:
            with open('setting.lp', 'r') as f:
                dumpData = json.load(f)
                self.maxIColor = dumpData[0]
                self.minIColor = dumpData[1]
                self.minZColor = dumpData[2]
                self.maxZColor = dumpData[3]
                self.lab2colDict = dumpData[4]
                self.ret2colDict = dict(dumpData[5])
        except:
            pass
    
    def SaveCurrentSetting(self):
        dumpData = [self.maxIColor, self.minIColor, self.maxZColor, self.minZColor, self.lab2colDict, self.ret2colDict.items()]
        with open('setting.lp', 'w') as f:
            json.dump(dumpData, f)
        
    def createMenu(self):
        self.menubar = MenuBar()
        mfile = Menu()
        mfile.Append(MENU_FILE_OPEN, '&Open\tCtr+O', 'Open a new document')
        mfile.AppendSeparator()
        mquit = MenuItem(mfile, MENU_FILE_QUIT, '&Quit\tCtrl+Q', 'Quit the Application')
        mfile.AppendItem(mquit)
        
        view = Menu()
        mode = Menu()
        self.mode2D = mode.Append(MENU_VIEW_MODE_2D, '2D Mode', kind=ITEM_RADIO)
        self.mode3D = mode.Append(MENU_VIEW_MODE_3D, '3D Mode', kind=ITEM_RADIO)
        view.AppendMenu(MENU_VIEW_MODE, '&View Mode', mode)
        zoom = Menu()
        zoom.Append(MENU_VIEW_ZOOMIN, 'Zoom &In\tCtr++')
        zoom.Append(MENU_VIEW_ZOOMOUT, 'Zoom &Out\tCtr+-')
        view.AppendMenu(MENU_VIEW_ZOOM, '&Zoom', zoom)
        rotate = Menu()
        rotate.Append(MENU_VIEW_ROTATE_CLK, 'Rotate &Clockwise')
        rotate.Append(MENU_VIEW_ROTATE_ANTICLK, 'Rotate &Anti-clockwise')
        rotate.Append(MENU_VIEW_ROTATE_LEFT, 'Rotate &Left')
        rotate.Append(MENU_VIEW_ROTATE_RIGHT, 'Rotate &Right')
        rotate.Append(MENU_VIEW_ROTATE_UP, 'Rotate &Up')
        rotate.Append(MENU_VIEW_ROTATE_DOWN, 'Rotate &Down')
        view.AppendMenu(MENU_VIEW_ROTATE, '&Rotate', rotate)
        move = Menu()
        move.Append(MENU_VIEW_MOVE_UP, 'Move &Up')
        move.Append(MENU_VIEW_MOVE_DOWN, 'Move &Down')
        move.Append(MENU_VIEW_MOVE_LEFT, 'Move &Left')
        move.Append(MENU_VIEW_MOVE_RIGHT, 'Move &Right')
        view.AppendMenu(MENU_VIEW_MOVE, '&Move', move)
        view.AppendSeparator()
        view.Append(MENU_VIEW_SELECT, 'Select Points', 'Select point(s)')
        view.Append(MENU_VIEW_CLEAR_SELECTED, 'Erase', 'Clear selected point(s)')
        view.AppendSeparator()
        view.Append(MENU_VIEW_RESET, '&Reset', 'Reset to default view')
        view.Append(MENU_VIEW_INFO, '&On/off Input Information', '')        
        setting = Menu()
        rangeMenu = Menu()
        rangeMenu.Append(MENU_SETTING_COLORR_INT, '&Intensity Color Range')
        rangeMenu.Append(MENU_SETTING_COLORR_Z, '&Height Color Range')
        rangeMenu.Append(MENU_SETTING_COLORR_LAB, '&Labels Color Range')
        rangeMenu.AppendSeparator()
        rangeMenu.Append(MENU_SETTING_COLORR_RET, '&Returning Color')
        setting.AppendMenu(MENU_SETTING_COLORR, '&Ranges Setting', rangeMenu)
        colorMode = Menu()
        self.rawModeMenu = colorMode.Append(MENU_SETTING_COLORM_RAW, 'Use &Raw Color', kind=ITEM_RADIO)
        self.intModeMenu = colorMode.Append(MENU_SETTING_COLORM_INT, 'Use &Intensity', kind=ITEM_RADIO)
        self.zModeMenu = colorMode.Append(MENU_SETTING_COLORM_Z, 'Use &Height', kind=ITEM_RADIO)
        self.labModeMenu = colorMode.Append(MENU_SETTING_COLORM_LAB, 'Use &Label', kind=ITEM_RADIO)
        self.retModeMenu = colorMode.Append(MENU_SETTING_COLORM_RET, 'Use &Return', kind=ITEM_RADIO)
        setting.AppendMenu(MENU_SETTING_COLORM, 'Color &Modes', colorMode)
        pointMode = Menu()
        self.ptnModeAll = pointMode.Append(MENU_SETTING_PNT_ALL, "Use &All Points")
        self.ptnModeRet = pointMode.Append(MENU_SETTING_PNT_RET, "Use &Returned Points")
        self.ptnModePol = pointMode.Append(MENU_SETTING_PNT_POL, "Use Points in &Polygon")
        setting.AppendMenu(MENU_SETTING_PTN, '&Points Used', pointMode)
        
        tools = Menu()
        self.las2txtMenu = tools.Append(MENU_TOOLS_LAS2TXT, 'LAS to TXT')
        
        mhelp = Menu()
        mhelp.Append(MENU_HELP_ABOUT, '&About', 'Application\'s information')
        
        self.menubar.Append(mfile, '&File')
        self.menubar.Append(view, '&View')
        self.menubar.Append(setting, '&Setting')
        self.menubar.Append(tools, '&Tools')
        self.menubar.Append(mhelp, '&Help')
        self.SetMenuBar(self.menubar)
        
        # Add handlers for menu items
        self.Bind(EVT_MENU, self.onOpen, id=MENU_FILE_OPEN)
        self.Bind(EVT_MENU, self.onQuit, id=MENU_FILE_QUIT)
        self.Bind(EVT_MENU, self.onSet2DMode, id=MENU_VIEW_MODE_2D)
        self.Bind(EVT_MENU, self.onSet3DMode, id=MENU_VIEW_MODE_3D)
        self.Bind(EVT_MENU, self.onMoveDown2D, id=MENU_VIEW_MOVE_DOWN)
        self.Bind(EVT_MENU, self.onMoveLeft2D, id=MENU_VIEW_MOVE_LEFT)
        self.Bind(EVT_MENU, self.onMoveRight2D, id=MENU_VIEW_MOVE_RIGHT)
        self.Bind(EVT_MENU, self.onMoveUp2D, id=MENU_VIEW_MOVE_UP)
        self.Bind(EVT_MENU, self.onResetView, id=MENU_VIEW_RESET)
        self.Bind(EVT_MENU, self.onShowInfo, id=MENU_VIEW_INFO)
        self.Bind(EVT_MENU, self.onRotateCounter, id=MENU_VIEW_ROTATE_ANTICLK)
        self.Bind(EVT_MENU, self.onRotateClockwise, id=MENU_VIEW_ROTATE_CLK)
        self.Bind(EVT_MENU, self.onRotateDown, id=MENU_VIEW_ROTATE_DOWN)
        self.Bind(EVT_MENU, self.onRotateLeft, id=MENU_VIEW_ROTATE_LEFT)
        self.Bind(EVT_MENU, self.onRotateRight, id=MENU_VIEW_ROTATE_RIGHT)
        self.Bind(EVT_MENU, self.onRotateUp, id=MENU_VIEW_ROTATE_UP)
        self.Bind(EVT_MENU, self.onZoomIn, id=MENU_VIEW_ZOOMIN)
        self.Bind(EVT_MENU, self.onZoomOut, id=MENU_VIEW_ZOOMOUT)
        self.Bind(EVT_MENU, self.onSelect, id=MENU_VIEW_SELECT)
        self.Bind(EVT_MENU, self.onErase, id=MENU_VIEW_CLEAR_SELECTED)
        self.Bind(EVT_MENU, self.onSetColorModeIntensity, id=MENU_SETTING_COLORM_INT)
        self.Bind(EVT_MENU, self.onSetColorModeRaw, id=MENU_SETTING_COLORM_RAW)
        self.Bind(EVT_MENU, self.onSetColorModeZ, id=MENU_SETTING_COLORM_Z)
        self.Bind(EVT_MENU, self.onSetColorModeLab, id=MENU_SETTING_COLORM_LAB)
        self.Bind(EVT_MENU, self.onSetColorRangeIntensity, id=MENU_SETTING_COLORR_INT)
        self.Bind(EVT_MENU, self.onSetColorRangeZ, id=MENU_SETTING_COLORR_Z)
        self.Bind(EVT_MENU, self.onSetColorRangeLab, id=MENU_SETTING_COLORR_LAB)
        self.Bind(EVT_MENU, self.onAbout, id=MENU_HELP_ABOUT)
        self.Bind(EVT_MENU, self.onLas2Txt, id=MENU_TOOLS_LAS2TXT)
        self.Bind(EVT_MENU, self.onSetColorRangeRet, id=MENU_SETTING_COLORR_RET)
        self.Bind(EVT_MENU, self.onSetColorModeRet, id=MENU_SETTING_COLORM_RET)
        self.Bind(EVT_MENU, self.onSetPtnAll, id=MENU_SETTING_PNT_ALL)
        self.Bind(EVT_MENU, self.onSetPtnRet, id=MENU_SETTING_PNT_RET)
        self.Bind(EVT_MENU, self.onSetPtnPol, id=MENU_SETTING_PNT_POL)
        
    def createToolBar(self):
        self.toolbar = self.CreateToolBar(TB_HORIZONTAL | NO_BORDER | TB_FLAT | TB_TEXT)
        self.toolbar.AddSimpleTool(TOOLBAR_OPEN,
                              Image('icons/open.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Open', '')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(TOOLBAR_3D,
                              Image('icons/3d.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Turn on/off 3D mode', '')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(TOOLBAR_ROTATE_CLOCKWISE,
                              Image('icons/rotate_clockwise.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Rotate clockwise 10 degrees', '')
        self.toolbar.AddSimpleTool(TOOLBAR_ROTATE_COUNTER,
                              Image('icons/rotate_anticlockwise.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Rotate counter-clockwise 10 degrees', '')
        self.toolbar.AddSimpleTool(TOOLBAR_ROTATE_UP,
                              Image('icons/rotate_up.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Rotate around X axis up 10 degrees', '')
        self.toolbar.AddSimpleTool(TOOLBAR_ROTATE_DOWN,
                              Image('icons/rotate_down.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Rotate around X axis down 10 degrees', '')
        self.toolbar.AddSimpleTool(TOOLBAR_ROTATE_LEFT,
                              Image('icons/rotate_left.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Rotate around Y axis left 10 degrees', '')
        self.toolbar.AddSimpleTool(TOOLBAR_ROTATE_RIGHT,
                              Image('icons/rotate_right.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Rotate around Y right 10 degrees', '')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(TOOLBAR_ZOOMIN,
                              Image('icons/zoom_in.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Zoom in 0.25 times', '')
        self.toolbar.AddSimpleTool(TOOLBAR_ZOOMOUT,
                              Image('icons/zoom_out.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Zoom out 0.25 times', '')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(TOOLBAR_MOVEUP,
                              Image('icons/move_up.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Move up 10 pixels', '')
        self.toolbar.AddSimpleTool(TOOLBAR_MOVEDOWN,
                              Image('icons/move_down.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Move down 10 pixels', '')
        self.toolbar.AddSimpleTool(TOOLBAR_MOVELEFT,
                              Image('icons/move_left.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Move left 10 pixels', '')
        self.toolbar.AddSimpleTool(TOOLBAR_MOVERIGHT,
                              Image('icons/move_right.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Move right 10 pixels', '')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(TOOLBAR_RESETVIEW,
                              Image('icons/reset.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Reset view', '')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(TOOLBAR_PTN_ALL,
                              Image('icons/all_pts.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              "Use all points to draw", "")
        self.toolbar.AddSimpleTool(TOOLBAR_PTN_RET,
                              Image('icons/returns_pts.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              "Use points with specific returns to draw", "")
        self.toolbar.AddSimpleTool(TOOLBAR_PTN_POL,
                              Image('icons/polygon_pts.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              "Use points in selected polygon to draw", "")
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(TOOLBAR_SELECT,
                              Image('icons/select.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Select points', '')
        self.toolbar.AddSimpleTool(TOOLBAR_CLEAR_SELECTED,
                              Image('icons/erase.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Clear selected points', '')
        self.toolbar.AddSeparator()
        self.toolbar.AddSimpleTool(TOOLBAR_SHOWINF,
                              Image('icons/info_on.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Info', 'On/off data information')
        self.toolbar.AddSimpleTool(TOOLBAR_EXIT,
                              Image('icons/stock_exit.png', BITMAP_TYPE_PNG).ConvertToBitmap(),
                              'Exit', '')
        self.toolbar.Realize()
          
        self.Bind(EVT_TOOL, self.onOpen, id=TOOLBAR_OPEN)
        self.Bind(EVT_TOOL, self.on3D, id=TOOLBAR_3D)
        self.Bind(EVT_TOOL, self.onRotateClockwise, id=TOOLBAR_ROTATE_CLOCKWISE)
        self.Bind(EVT_TOOL, self.onRotateCounter, id=TOOLBAR_ROTATE_COUNTER)
        self.Bind(EVT_TOOL, self.onRotateUp, id=TOOLBAR_ROTATE_UP)
        self.Bind(EVT_TOOL, self.onRotateDown, id=TOOLBAR_ROTATE_DOWN)
        self.Bind(EVT_TOOL, self.onRotateLeft, id=TOOLBAR_ROTATE_LEFT)
        self.Bind(EVT_TOOL, self.onRotateRight, id=TOOLBAR_ROTATE_RIGHT)
        self.Bind(EVT_TOOL, self.onZoomIn, id=TOOLBAR_ZOOMIN)
        self.Bind(EVT_TOOL, self.onZoomOut, id=TOOLBAR_ZOOMOUT)
        self.Bind(EVT_TOOL, self.onMoveUp2D, id=TOOLBAR_MOVEUP)
        self.Bind(EVT_TOOL, self.onMoveDown2D, id=TOOLBAR_MOVEDOWN)
        self.Bind(EVT_TOOL, self.onMoveLeft2D, id=TOOLBAR_MOVELEFT)
        self.Bind(EVT_TOOL, self.onMoveRight2D, id=TOOLBAR_MOVERIGHT)
        self.Bind(EVT_TOOL, self.onResetView, id=TOOLBAR_RESETVIEW)
        self.Bind(EVT_TOOL, self.onSetPtnPol, id=TOOLBAR_PTN_POL)
        self.Bind(EVT_TOOL, self.onSetPtnAll, id=TOOLBAR_PTN_ALL)
        self.Bind(EVT_TOOL, self.onSetPtnRet, id=TOOLBAR_PTN_RET)
        self.Bind(EVT_TOOL, self.onSelect, id=TOOLBAR_SELECT)
        self.Bind(EVT_TOOL, self.onErase, id=TOOLBAR_CLEAR_SELECTED)
        self.Bind(EVT_TOOL, self.onShowInfo, id=TOOLBAR_SHOWINF)
        self.Bind(EVT_TOOL, self.onQuit, id=TOOLBAR_EXIT)
        
    def createWorkingSpace(self):
        vbox = BoxSizer(HORIZONTAL)
        self.drawPanel = OpenGLCanvas(self, SPLITTER_WIN_DRAW, style=RAISED_BORDER)
        self.drawPanel.SetStatusBar(self.StatusBar)
        self.inputPanel = Panel(self, style=RAISED_BORDER, size=(300, 400))
        self.createInputPanelControls()
        vbox.Add(self.inputPanel, 0, flag=LEFT | EXPAND)
        vbox.Add(self.drawPanel, 1, flag=RIGHT | EXPAND | ALL)
        self.inputPanel.Show(False)
        self.SetSizer(vbox)
        
    def createInputPanelControls(self):
        vbox = BoxSizer(VERTICAL)
        
        labels = ['Input source', 'LAS version', 'Source ID', 'System ID', 'Software ID',
                  'Creation day/year', 'Points number', 'X Range', 'Y Range', 'Z Range',
                  'Used points']
        self.infoTxt = []
        
        for i in xrange(len(labels)):
            hbox = BoxSizer(HORIZONTAL)
            st = StaticText(self.inputPanel, label=labels[i], style=ALIGN_CENTER_VERTICAL)
            hbox.Add(st, flag=RIGHT | ALIGN_CENTRE_VERTICAL, border=8)
            self.infoTxt.append(TextCtrl(self.inputPanel, value="None"))
            self.infoTxt[i].SetEditable(False)
            hbox.Add(self.infoTxt[i], proportion=1)
            vbox.Add(hbox, flag=EXPAND | LEFT | RIGHT | TOP, border=8)
        
        self.inputPanel.SetSizer(vbox)
        
    def onOpen(self, event):    
        # Get file path
        wildcard = "LAS file (*.las)|*.las|" "All files (*.*)|*.*"
        dialog = FileDialog(None, "Choose LAS file", os.getcwd(), "", wildcard, OPEN)
        if dialog.ShowModal() == ID_OK:
            fileName = dialog.GetPath()
            dialog.Destroy()
        else:
            dialog.Destroy()
            return        
        
        startTime = time.time()
        # Get data from file
        busyDlg = BusyInfo("Importing data...")
        self.rawData, self.intensities, self.rawColors, self.info, self.returns, self.ptnRetCount = self.GetRawData(fileName)
        del busyDlg
        if self.rawData is None:
            return  # no data get
        # Make sure that the used points are get based on the current state of the application
        startTime = time.time()
        self.initializeData = True
        self.toolbar.ToggleTool(TOOLBAR_PTN_ALL, True)
        self.pointMode = 'all'
        self.colorMode = 'rawColor'
        self.CalculateDisplayData()
        if self.dataUsedIdx is None or len(self.dataUsedIdx) == 0:
            return
        busyDlg = BusyInfo("Pushing data to OpenGL...")
        data = self.rawData[self.dataUsedIdx]
        colors = self.usedColors[self.dataUsedIdx]
        self.drawPanel.ResetView()
        self.drawPanel.SetDisplayingItems(data, len(data), colors)
        self.drawPanel.Set3D(self.is3D)
        del data
        del colors
        self.drawPanel.Refresh()
        del busyDlg
        print "Time to prepare data: ", (time.time() - startTime)
        
        # Update information
        if not self.info is None:
            self.infoTxt[0].SetValue(self.info.filename)
            self.infoTxt[1].SetValue(self.info.version)
            self.infoTxt[2].SetValue(str(self.info.sourceID))
            self.infoTxt[3].SetValue(self.info.identifier)
            self.infoTxt[4].SetValue(str(self.info.software))
            self.infoTxt[5].SetValue(self.info.creationTime)
            self.infoTxt[6].SetValue(str(self.info.pointsNum))
            self.infoTxt[7].SetValue(str(self.info.xMin) + " to " + str(self.info.xMax))
            self.infoTxt[8].SetValue(str(self.info.yMin) + " to " + str(self.info.yMax))
            self.infoTxt[9].SetValue(str(self.info.zMin) + " to " + str(self.info.zMax))
            self.infoTxt[10].SetValue('All')
            x1 = self.info.xMin + (self.info.xMax - self.info.xMin) / 3
            x2 = self.info.xMin + (self.info.xMax - self.info.xMin) * 2 / 3
            y1 = self.info.yMin + (self.info.yMax - self.info.yMin) / 3
            y2 = self.info.yMin + (self.info.yMax - self.info.yMin) * 2 / 3
            self.selectedPoints = [[x1, y1], [x1, y2], [x2, y2], [x2, y1]]
            
    # additionals must be array of number
    def GetAdditionalBasedColors(self, additionals, maxColor, minColor):
        if additionals is None or len(additionals) == 0:
            return
        uinput = reshape(array(additionals, float32), (-1, 1))
        xMax = amax(uinput)
        xMin = amin(uinput)
        xRange = xMax - xMin
        rRange = maxColor[0] - minColor[0]
        gRange = maxColor[1] - minColor[1]
        bRange = maxColor[2] - minColor[2]
        rMin = minColor[0]
        gMin = minColor[1]
        bMin = minColor[2]
        
        try:            
            uinput = subtract(uinput, xMin)
            if xRange != 0:
                GetApp().Yield()  # should keep this line to update the BusyInfo dialog
                colorArr = multiply(uinput, array([rRange, gRange, bRange], float32))
                GetApp().Yield()  # should keep this line to update the BusyInfo dialog
                colorArr = divide(colorArr, xRange)
                GetApp().Yield()  # should keep this line to update the BusyInfo dialog
                colorArr = add(colorArr, array([rMin, gMin, bMin], float32))
            else:
                colorArr = ones((len(additionals), 3), dtype=float32)
                colorArr = multiply(colorArr, array([rMin, gMin, bMin], float32))
        finally:
            pass
        return colorArr
    
    def GetRawData(self, fileName):        
        '''
        Fill data to arrays
        if number of points is n, points' length = 3 * n, intensities' length = n
        and colors' length = 3 * n
        '''
#         points, intensities, colors = self.GenerateFakeData()
#         return points, intensities, colors, None, None, None
        lFile = LASFile(fileName)
        points = lFile.GetPoints()
#         print "points:\n", points
        intensities = lFile.GetIntensity()
#         print "intensities:\n", intensities
        colors = lFile.GetColor()
#         print "colors:\n", colors
        info = lFile.GetInfor()
        returns = lFile.GetReturns()
        ptn_ret_count = lFile.GetPointReturnCount()        
        return points, intensities, colors, info, returns, ptn_ret_count
        
        
    def onQuit(self, event):
        self.Close(True)  # Close the frame.
        
    # Zooming is based on the angle of view in Y axis (fovy)
    def onZoomIn(self, event):
        self.dZoomFactor = -ZOOMIN_STEP
        self.drawPanel.Zoom(self.dZoomFactor)
        event.Skip()
    
    # Zooming is based on the angle of view in Y axis (fovy)
    def onZoomOut(self, event):
        self.dZoomFactor = ZOOMOUT_STEP
        self.drawPanel.Zoom(self.dZoomFactor)
        event.Skip()
     
    # Moving is based on pixels   
    def onMoveLeft2D(self, event):
        self.drawPanel.Move(-10.0, 0.0)
        event.Skip()
    
    # Moving is based on pixels
    def onMoveRight2D(self, event):
        self.drawPanel.Move(10.0, 0.0)
        event.Skip()
    
    # Moving is based on pixels
    def onMoveUp2D(self, event):
        self.drawPanel.Move(0.0, 10.0)
        event.Skip()
        
    # Moving is based on pixels
    def onMoveDown2D(self, event):
        self.drawPanel.Move(0.0, -10.0)
        event.Skip()
        
    def onResetView(self, event):
        self.currentAngleHorizontal = 0
        self.currentAngleVertical = 0
        self.currentAngleFlat = 0
        self.dZoomFactor = 1
        self.dX = 0
        self.dY = 0
        self.drawPanel.ResetView()
        event.Skip()
        
    def on3D(self, event):
        self.is3D = (not self.is3D)
        if self.is3D:
            self.mode3D.Check()
            self.toolbar.SetToolNormalBitmap(id=TOOLBAR_3D,
                                             bitmap=Image('icons/2D.png', BITMAP_TYPE_PNG).ConvertToBitmap()) 
        else:
            self.mode2D.Check()
            self.toolbar.SetToolNormalBitmap(id=TOOLBAR_3D,
                                             bitmap=Image('icons/3d.png', BITMAP_TYPE_PNG).ConvertToBitmap())
        self.Enable3DFeatures(self.is3D)
        self.drawPanel.Set3D(self.is3D)
        event.Skip()
    
    # Rotating angle is in degree unit    
    def onRotateClockwise(self, event):
        self.currentAngleFlat -= 10
        self.drawPanel.RotateFlat(self.currentAngleFlat)
        event.Skip()
    
    # Rotating angle is in degree unit    
    def onRotateCounter(self, event):
        self.currentAngleFlat += 10
        self.drawPanel.RotateFlat(self.currentAngleFlat)
        event.Skip()
        
    def onRotateUp(self, event):
        if(self.is3D):
            self.currentAngleVertical -= 10
            self.drawPanel.RotateVeritcal(self.currentAngleVertical)
            event.Skip()
    
    def onRotateDown(self, event):
        if(self.is3D):
            self.currentAngleVertical += 10
            self.drawPanel.RotateVeritcal(self.currentAngleVertical)
            event.Skip()
    
    def onRotateLeft(self, event):
        if(self.is3D):
            self.currentAngleHorizontal += 10            
            self.drawPanel.RotateHorizontal(self.currentAngleHorizontal)
            event.Skip()
    
    def onRotateRight(self, event):
        if(self.is3D):
            self.currentAngleHorizontal -= 10
            self.drawPanel.RotateHorizontal(self.currentAngleHorizontal)
            event.Skip()
            
    def onSetColorModeIntensity(self, event):
        if self.colorMode == "intensity":
            return
        if self.intensities is None:
            if self.colorMode == "rawColor":
                self.rawModeMenu.Check()
                return
            elif self.colorMode == "z":
                self.zModeMenu.Check()
                return
            elif self.colorMode == "return":
                self.retModeMenu.Check()
                return
            else:
                self.labModeMenu.Check()
                return
        self.colorMode = "intensity"
        self.UpdateColor()
        event.Skip()
    
    def onSetColorModeRaw(self, event):
        if self.colorMode == "rawColor":
            return
        if self.rawColors is None:
            if self.colorMode == "intensity":
                self.intModeMenu.Check()
                return
            elif self.colorMode == "z":
                self.zModeMenu.Check()
                return
            elif self.colorMode == "return":
                self.retModeMenu.Check()
                return
            else:
                self.labModeMenu.Check()
                return
        self.colorMode = "rawColor"
        self.UpdateColor()
        event.Skip()
    
    def onSetColorModeZ(self, event):
        if self.colorMode == "z":
            return
        self.colorMode = "z"
        self.modeChanged = True
        self.UpdateColor()
        event.Skip()
    
    def onSetColorModeLab(self, event):
        if self.colorMode == "label":
            return
        if self.labels is None:
            if self.colorMode == "rawColor":
                self.rawModeMenu.Check()
                return
            elif self.colorMode == "z":
                self.zModeMenu.Check()
                return
            elif self.colorMode == "return":
                self.retModeMenu.Check()
                return
            else:
                self.intModeMenu.Check()
                return
        self.colorMode = "label"
        self.UpdateColor()
        event.Skip()
        
    def onSetColorModeRet(self, event):
        if self.colorMode == "return":
            return
        if self.returns is None:
            if self.colorMode == "rawColor":
                self.rawModeMenu.Check()
                return
            elif self.colorMode == "z":
                self.zModeMenu.Check()
                return
            elif self.colorMode == "label":
                self.labModeMenu.Check()
                return
            else:
                self.intModeMenu.Check()
                return
        self.colorMode = "return"
        self.UpdateColor()
        event.Skip()
    
    def onSetColorRangeIntensity(self, event):
        dlg = ColorRangeDlg(self.maxIColor, self.minIColor) 
        if dlg.ShowModal() == ID_OK:
            self.maxIColor = dlg.GetUpperColor()
            self.minIColor = dlg.GetLowerColor()
            if self.colorMode == "intensity":
                self.UpdateColor()
        dlg.Destroy()
        event.Skip()
    
    def onSetColorRangeZ(self, event):
        dlg = ColorRangeDlg(self.maxZColor, self.minZColor) 
        if dlg.ShowModal() == ID_OK:
            self.maxZColor = dlg.GetUpperColor()
            self.minZColor = dlg.GetLowerColor()
            if self.colorMode == "z":
                self.UpdateColor()
        dlg.Destroy()
        event.Skip()
        
    def onSetColorRangeLab(self, event):
        dlg = ColorTableDlg("Label", self.lab2colDict) 
        if dlg.ShowModal() == ID_OK:
            self.lab2colDict = dlg.GetNewDict()
            if self.colorMode == "label":
                self.UpdateColor()
        dlg.Destroy()
        event.Skip()
        
    def onSetColorRangeRet(self, evt):
        dlg = ColorTableDlg("Return Value", self.ret2colDict) 
        if dlg.ShowModal() == ID_OK:
            self.ret2colDict = dlg.GetNewDict(ktype='int')
            if self.colorMode == "return":
                self.UpdateColor()
        dlg.Destroy()
        evt.Skip()
    
    def UpdateColor(self):
        wait = BusyInfo("Updating colors...")
        startTime = time.time()
        if(self.colorMode == "rawColor"):
            self.usedColors = self.rawColors.astype(float32)
        elif(self.colorMode == "intensity"):
            self.usedColors = self.GetAdditionalBasedColors(self.intensities, self.maxIColor, self.minIColor)
        elif(self.colorMode == "z"):
            data = array(self.rawData, float32)
            reshape(data, [3, -1])
            self.usedColors = self.GetAdditionalBasedColors(data[:, 2], self.maxZColor, self.minZColor)
        elif(self.colorMode == "label"):
            self.usedColors = self.GetColorsFromDict(self.labels, self.lab2colDict)
        elif(self.colorMode == "return"):
            self.usedColors = self.GetColorsFromDict(self.returns, self.ret2colDict)
        else:
            self.usedColors = self.rawColors.astype(float32)
        print 'time to calculate new color:', (time.time() - startTime)
        self.drawPanel.SetColors(self.usedColors[self.dataUsedIdx])
        print "Time for updating new color: ", (time.time() - startTime)
        del wait
        self.drawPanel.Refresh()        
        
    def GetColorsFromDict(self, labels, dict):
        if labels is None or not iterable(labels):
            return None
        ret = empty((len(labels), 3), float32)
        # get all label names in labels
        usedLabels = unique(labels)
        # get all color appropriate to the label  
        for i in xrange(len(usedLabels)):
            # get indices of label in labels
            indices = argwhere(labels == usedLabels[i])
            # find the color of the labels
            if usedLabels[i] in dict:
                color = dict[usedLabels[i]]
            else:
                color = [1.0, 1.0, 1.0]
            # For each label, assign the color following the found indices
            ret[indices] = color
        return ret
    
    def onAbout(self, event):
        info = AboutDialogInfo()

        description = ""
        licence = ""
#         info.SetIcon(Icon('hunter.png', wx.BITMAP_TYPE_PNG))
        info.SetName('LiDAR Plotter')
        info.SetVersion('0.1')
        info.SetDescription(description)
        info.SetCopyright('(C) 2014 Cao Van Hung - Chu Xuan Khoi')
#         info.SetWebSite('http://www.zetcode.com')
        info.SetLicence(licence)
        info.AddDeveloper('Cao Van Hung')
        info.AddDocWriter('Cao Van Hung')
        info.AddArtist('Chu Xuan Khoi')
#         info.AddTranslator('Jan Bodnar')

        AboutBox(info)

    def onShowInfo(self, event):
        self.showInfo = not self.showInfo
        self.inputPanel.Show(self.showInfo)
        self.Layout()
    
    def onSet2DMode(self, event):
        self.is3D = False
        self.drawPanel.Set3D(self.is3D)
        self.toolbar.SetToolNormalBitmap(id=TOOLBAR_3D,
                                         bitmap=Image('icons/3d.png', BITMAP_TYPE_PNG).ConvertToBitmap())
        self.Enable3DFeatures(self.is3D)
        event.Skip()
    
    def onSet3DMode(self, event):
        self.is3D = True
        self.drawPanel.Set3D(self.is3D)
        self.toolbar.SetToolNormalBitmap(id=TOOLBAR_3D,
                                         bitmap=Image('icons/2D.png', BITMAP_TYPE_PNG).ConvertToBitmap())
        self.Enable3DFeatures(self.is3D)
        event.Skip()

    def Enable3DFeatures(self, enable=True):
        # enable/disable toolbar buttons
        self.toolbar.EnableTool(TOOLBAR_ROTATE_DOWN, enable)
        self.toolbar.EnableTool(TOOLBAR_ROTATE_LEFT, enable)
        self.toolbar.EnableTool(TOOLBAR_ROTATE_RIGHT, enable)
        self.toolbar.EnableTool(TOOLBAR_ROTATE_UP, enable)
        self.toolbar.EnableTool(TOOLBAR_SELECT, not enable)
        self.toolbar.EnableTool(TOOLBAR_CLEAR_SELECTED, not enable)
        # enable/disable menu items
        self.menubar.Enable(MENU_VIEW_ROTATE_DOWN, enable)
        self.menubar.Enable(MENU_VIEW_ROTATE_LEFT, enable)
        self.menubar.Enable(MENU_VIEW_ROTATE_RIGHT, enable)
        self.menubar.Enable(MENU_VIEW_ROTATE_UP, enable)
        self.menubar.Enable(MENU_VIEW_SELECT, not enable)
        self.menubar.Enable(MENU_VIEW_CLEAR_SELECTED, not enable)
    
    def onLas2Txt(self, evt):
        '''
        Need more discussion to agree about the file's contents
        '''
        pass    
    
    def onSetPtnAll(self, evt):
        if self.rawData is None:
            return  # no data get 
        self.CalculateDisplayData()
        if self.dataUsedIdx is None or len(self.dataUsedIdx) == 0:
            return        
        data = self.rawData[self.dataUsedIdx]
        colors = self.usedColors[self.dataUsedIdx]
        if data is None or len(data) == 0:
            print 'No data get for the returns'
            return
        print 'new data length:', len(data)
        busyDlg = BusyInfo("Pushing data to OpenGL...")
        self.drawPanel.SetDisplayingItems(data, len(data), colors)
        self.drawPanel.Set3D(self.is3D)
        del data
        del colors
        self.drawPanel.Refresh()
        del busyDlg
        
        self.infoTxt[10].SetValue('All')
    
    def onSetPtnRet(self, evt):
        if self.returns is None or len(self.returns) == 0:
            return
        
        # Open dialog to collect return(s) user want to display
        retDlg = ReturnSelectionDlg(self.ptnRetCount)
        if retDlg.ShowModal() != ID_OK:
            return
        self.workingReturns = retDlg.GetUsedReturns()
        if self.workingReturns is None or len(self.workingReturns) == 0:
            MessageDialog(None, 'No return is selected',
                               'Error', OK | ICON_ERROR).ShowModal()
            return
        print 'working ret:', self.workingReturns
        
        self.CalculateDisplayData()
        if self.dataUsedIdx is None or len(self.dataUsedIdx) == 0:
            return
        
        data = self.rawData[self.dataUsedIdx]
        colors = self.usedColors[self.dataUsedIdx]
        print 'new data length:', len(data)
        busyDlg = BusyInfo("Pushing data to OpenGL...")
        self.drawPanel.SetDisplayingItems(data, len(data), colors)
        self.drawPanel.Set3D(self.is3D)
        del data
        del colors
        self.drawPanel.Refresh()
        del busyDlg
        
        self.infoTxt[10].SetValue(str(self.workingReturns))
    
    def CalculateDisplayData(self):
        '''
        Calculate used color and index of used points based on the current mode and raw data
        '''
        busyDlg = BusyInfo("Calculating data...")
        if self.rawData is None:
            return
        # if features are not adequate, replace the default color by the other
        if self.initializeData:
            if self.colorMode == "rawColor" and self.rawColors is None:
                print "No raw color, replace by other mode"
                if self.intensities is None:
                    self.colorMode = "z"
                    self.zModeMenu.Check()
                    print "Z color is used"
                else:
                    self.colorMode = "intensity"
                    self.intModeMenu.Check()
                    print "Intensity color is used"
            if self.colorMode == "intensity" and self.intensities is None:
                if self.rawColors is None:
                    self.colorMode = "z"
                    self.zModeMenu.Check()
                    print "Z color is used"
                else:
                    self.colorMode = "rawColors"
                    self.rawModeMenu.Check()
                    print "Raw color is used"
            if self.colorMode == "label" and self.labels is None:
                if self.rawColors is None:
                    self.colorMode = "z"
                    self.zModeMenu.Check()
                    print "Z color is used"
                else:
                    self.colorMode = "rawColors"
                    self.rawModeMenu.Check()
                    print "Raw color is used"
            if self.colorMode == "return" and self.returns is None:
                if self.rawColors is None:
                    self.colorMode = "z"
                    self.zModeMenu.Check()
                    print "Z color is used"
                else:
                    self.colorMode = "rawColors"
                    self.rawModeMenu.Check()
                    print "Raw color is used"
            # Get appropriate data
            self.rawData = self.rawData.astype(float32)               
            # process color of each point based on the additional information        
            if(self.colorMode == "rawColor"):
                self.usedColors = self.rawColors.astype(float32)
            elif(self.colorMode == "intensity"):
                self.usedColors = self.GetAdditionalBasedColors(self.intensities, self.maxIColor, self.minIColor)
            elif(self.colorMode == "z"):
                reshape(data, [3, -1])
                self.usedColors = self.GetAdditionalBasedColors(data[:, 2], self.maxZColor, self.minZColor)
            elif self.colorMode == "label":
                self.usedColors = self.GetColorsFromDict(self.labels, self.lab2colDict)
            elif self.colorMode == "return":
                self.usedColors = self.GetColorsFromDict(self.returns, self.ret2colDict)
            else:
                self.usedColors = self.rawColors.astype(float32)
            self.initializeData = False
            
        self.dataUsedIdx = arange(len(self.rawData))
        
        if self.pointMode == 'return' and not self.returns is None:
            mask = ones_like(self.returns, bool)
            for r in self.workingReturns:
                mask &= (self.returns != r)
            self.dataUsedIdx = self.dataUsedIdx[-mask]
        del busyDlg
        
    def onSetPtnPol(self, event):
        if self.isSelecting:
            self.selectedPoints = []
            self.onSelect(None)
        if self.selectedPoints is None or len(self.selectedPoints) == 0:
            return
        
        # Get all points in the selected polygon
        busyDlg = BusyInfo("Getting inner points...")
        start = time.time()
        pol = Polygon(self.selectedPoints)
#         print "polygon:", pol
        self.dataUsedIdx = argwhere(pol.PointsInPolygon(self.rawData)).flatten()
#         self.dataUsedIdx = argwhere([p in pol for p in self.rawData]).flatten()
        print 'time to get inner points:', time.time() - start
        del busyDlg
        
        # Push the points to OpenGL and display
        if self.dataUsedIdx is None or len(self.dataUsedIdx) == 0:
            MessageDialog(None, 'No point in the selected area',
                               'Error', OK | ICON_ERROR).ShowModal()
            return
        data = self.rawData[self.dataUsedIdx]
        colors = self.usedColors[self.dataUsedIdx]
        busyDlg = BusyInfo("Pushing data to OpenGL...")
        print 'new data length:', len(self.dataUsedIdx)
        self.drawPanel.ClearSelected()
        self.drawPanel.SetDisplayingItems(data, len(self.dataUsedIdx), colors)
        self.drawPanel.Set3D(self.is3D)
        del data
        del colors
        self.drawPanel.Refresh()
        del busyDlg
                
        ptsStr = "["
        for p in self.selectedPoints:
            ptsStr += "("
            ptsStr += "{0:.2f}".format(p[0])
            ptsStr += ", "
            ptsStr += "{0:.2f}".format(p[1])
            ptsStr += ")"
        ptsStr += "]"
        
        self.infoTxt[10].SetValue(ptsStr)
    
    def onSelect(self, event):
        self.isSelecting = (not self.isSelecting)
        self.drawPanel.SetSelecting(self.isSelecting)
        if self.isSelecting:
            self.menubar.SetLabel(MENU_VIEW_SELECT, "Stop Selecting")
            self.toolbar.SetToolNormalBitmap(id=TOOLBAR_SELECT,
                                             bitmap=Image('icons/unselect.png', BITMAP_TYPE_PNG).ConvertToBitmap()) 
        else:
            self.selectedPoints = self.drawPanel.GetSelectedPoints()
            self.menubar.SetLabel(MENU_VIEW_SELECT, "Select Points")
            self.toolbar.SetToolNormalBitmap(id=TOOLBAR_SELECT,
                                             bitmap=Image('icons/select.png', BITMAP_TYPE_PNG).ConvertToBitmap())
    
    def onErase(self, evt):
        self.drawPanel.ClearSelected()

    def GenerateFakeData(self):
        points = []
        intensities = []
        colors = []
        lineNum = 50
        ppl = 50  # points per line
        totalData = lineNum * ppl
        radius = 1.0
        alpha = 0.0
        beta = 0.0
        alphaStep = 2.0 * math.pi / ppl
        betaStep = 2.0 * math.pi / lineNum
        if not self.labels:
            self.labels = []
        for num in xrange(lineNum):
            GetApp().Yield()  # should keep this line to update the BusyInfo dialog
            beta += betaStep
            alpha = 0
            x = 0 - ppl / 2
            y = num - lineNum / 2
            z = 0
#             x = radius * math.cos(alpha) * math.cos(beta)
#             y = radius * math.sin(alpha) * math.cos(beta)
#             z = radius * math.sin(beta)  
#             x = (num - lineNum / 2) * ppl / lineNum
#             y = 0
#             z = 0
            pn = num * ppl
            for deg in xrange(1, ppl):
                alpha += alphaStep
                points.append([x, y, z])  
#                 colors.append([alpha / (2 * math.pi), 1.0 - alpha / (2 * math.pi), beta / (2 * math.pi), 1.0])
                colors.append([alpha / (2 * math.pi), 1.0 - alpha / (2 * math.pi), beta / (2 * math.pi)])
                intensities.append(radius)
                x = deg - ppl / 2
                y = num - lineNum / 2
                z = 0
#                 x = radius * math.cos(alpha) * math.cos(beta)
#                 y = radius * math.sin(alpha) * math.cos(beta)
#                 z = radius * math.sin(beta)
#                 y = deg - ppl / 2
#                 z = 0
                if (deg % 2) == 0:
                    label = "test1"
                else:
                    label = "test2"
                self.labels.append(label)
                if ((deg % 100) == 0):
                    self.SetStatusText("Importing data: " + str(pn + deg) + "/" + str(totalData))
        
        points = array(points, float32)
        intensities = array(intensities, float32)
        colors = array(colors, float32)
        return points, intensities, colors

    
#----------------------- Start main script -----------------------------------#

app = App()
frame = MainWindow()
app.MainLoop()

#----------------------- End main script -------------------------------------#
