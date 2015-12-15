'''
Created on 21 Jan 2015

@author: khoicx
'''

from wx import Dialog, Panel, BoxSizer, Button, ListCtrl, ID_ANY, LC_REPORT, BORDER_SUNKEN,\
                EVT_BUTTON, VERTICAL, ALL, EXPAND, CENTER, Colour, GridSizer, HORIZONTAL,\
                ID_OK, ID_CANCEL, LIST_NEXT_ALL, LIST_STATE_SELECTED, YES_NO, NO_DEFAULT,\
                ICON_QUESTION, ID_YES, StaticBox, StaticBoxSizer, StaticText, LEFT, ColourPickerCtrl,\
                ALIGN_CENTER, TOP, BOTTOM, ICON_ERROR, OK, MessageDialog, TextCtrl, SUNKEN_BORDER
from ObjectListView import ObjectListView, ColumnDefn

class Data(object):
    def __init__(self, retID, ptnNum):
        """Constructor"""
        self.returnID = retID
        self.pointsNum = ptnNum

class ReturnSelectionDlg(Dialog):
    '''
    classdocs
    '''
    _width = 330
    _height = 300

    def __init__(self, avaiReturns):
        '''
        Constructor
        '''
        super(ReturnSelectionDlg, self).__init__(None, size=(self._width, self._height))
        self.Center()
        self.InitUI()
        self.AddAvailabeItems(avaiReturns)
        
    def InitUI(self):
        panel = Panel(self, ID_ANY)
        self.index = 0
 
        panel1 = Panel(panel, size=(-1, self._height - 60))
        self.list_ctrl = ObjectListView(panel1, style=LC_REPORT|SUNKEN_BORDER)
        sizer1 = GridSizer()
        sizer1.Add(self.list_ctrl, 0, ALL|EXPAND, border = 5)
        panel1.SetSizer(sizer1)
 
        panel2 = Panel(panel)
        okBtn = Button(panel2, label="OK")
        okBtn.Bind(EVT_BUTTON, self.OnOk)
        cancelBtn = Button(panel2, label="Cancel")
        cancelBtn.Bind(EVT_BUTTON, self.OnClose)
        sizer2 = BoxSizer(HORIZONTAL)
        sizer2.Add(okBtn, border=5)
        sizer2.Add(cancelBtn, border=5)
        panel2.SetSizer(sizer2)
 
        sizer = BoxSizer(VERTICAL)
        sizer.Add(panel1, 0, ALL|EXPAND)
        sizer.Add(panel2, 0, ALL|CENTER)
        panel.SetSizer(sizer)
        
    def AddAvailabeItems(self, avaiItems):
        '''
        Add checked boxes
        '''
        self.list_ctrl.SetColumns([
            ColumnDefn("Return Value", "left", 100, "returnID"),
            ColumnDefn("Points Number", "left", 180, "pointsNum")
            ])
        data = []
        for i in xrange(len(avaiItems)):
            item = Data(str(i + 1), str(avaiItems[i]))
            data.append(item)
        self.list_ctrl.CreateCheckStateColumn()
        self.list_ctrl.SetObjects(data)
        
    def OnOk(self, e):
        self.EndModal(ID_OK)
        
    def OnClose(self, e):
        self.EndModal(ID_CANCEL)
        
    def GetUsedReturns(self):
        checkedData = self.list_ctrl.GetCheckedObjects()
        if checkedData is None:
            print 'cannot get checked returns'
            return []
        if len(checkedData) == 0:
            return []
        print "checked length:", len(checkedData)
        ret = []
        for item in checkedData:
            ret.append(int(item.returnID))
        return ret