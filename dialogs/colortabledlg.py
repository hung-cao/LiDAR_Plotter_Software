'''
Created on 6 Jan 2015

@author: khoicx
'''

from wx import Dialog, Panel, BoxSizer, Button, ListCtrl, ID_ANY, LC_REPORT, BORDER_SUNKEN,\
                EVT_BUTTON, VERTICAL, ALL, EXPAND, CENTER, Colour, GridSizer, HORIZONTAL,\
                ID_OK, ID_CANCEL, LIST_NEXT_ALL, LIST_STATE_SELECTED, YES_NO, NO_DEFAULT,\
                ICON_QUESTION, ID_YES, StaticBox, StaticBoxSizer, StaticText, LEFT, ColourPickerCtrl,\
                ALIGN_CENTER, TOP, BOTTOM, ICON_ERROR, OK
from wx._windows import MessageDialog
from wx._controls import TextCtrl

class NewPairDlg(Dialog):
    def __init__(self, key = None, value = None):
        super(NewPairDlg, self).__init__(None, size=(220, 170))
        self.InitUI()
        if not key is None:
            self.lblText.SetValue(key)
        if not value is None:
            self.colorSelection.SetColour(value)
        
    def InitUI(self):
        pnl = Panel(self)
        vbox = BoxSizer(VERTICAL)

        sb = StaticBox(pnl, label='Label and color')
        sbs = StaticBoxSizer(sb, orient=VERTICAL)
        
        hbox1 = BoxSizer(HORIZONTAL)        
        hbox1.Add(StaticText(pnl, -1, 'Label', size=(75, -1)), flag=LEFT|CENTER)
        self.lblText = TextCtrl(pnl, size=(125, -1))
        hbox1.Add(self.lblText, flag=LEFT|EXPAND, border=5)
        sbs.Add(hbox1, flag=ALL|EXPAND)
        
        hbox2 = BoxSizer(HORIZONTAL)        
        hbox2.Add(StaticText(pnl, -1, 'Color', size=(75, -1)), flag=LEFT|CENTER)
        self.colorSelection = ColourPickerCtrl(pnl, col=Colour(255, 255, 0), size=(125, -1))
        hbox2.Add(self.colorSelection, flag=LEFT|EXPAND, border=5)
        sbs.Add(hbox2, flag=ALL|EXPAND)
        
        pnl.SetSizer(sbs)
       
        hbox3 = BoxSizer(HORIZONTAL)
        okButton = Button(self, label='OK')
        closeButton = Button(self, label='Cancel')
        hbox3.Add(okButton)
        hbox3.Add(closeButton, flag=LEFT, border=5)

        vbox.Add(pnl, proportion=1, flag=ALL|EXPAND, border=5)
        vbox.Add(hbox3, flag=ALIGN_CENTER|TOP|BOTTOM, border=10)

        self.SetSizer(vbox)
        
        okButton.Bind(EVT_BUTTON, self.OnOk)
        closeButton.Bind(EVT_BUTTON, self.OnClose)
        
    def OnOk(self, e):
        if not self.lblText.GetValue().strip():
            if MessageDialog(None, "No label. Do you want to quit", 'Confirm',
                             YES_NO | NO_DEFAULT | ICON_QUESTION).ShowModal() == ID_YES:
                self.EndModal(ID_CANCEL)            
        else:
            self.EndModal(ID_OK)
        
    def OnClose(self, e): 
        self.EndModal(ID_CANCEL)
    
    def GetPair(self):
        return self.lblText.GetValue(), self.colorSelection.GetColour()

class ColorTableDlg(Dialog):
    def __init__(self, fistColName = "", initDict = None):
        super(ColorTableDlg, self).__init__(None, size=(500, 600))
        self.Center()
        self.InitUI(fistColName)
        if not initDict is None:
            self.AddItems(initDict)
        
    def InitUI(self, firstColName):
        # Add a panel so it looks the correct on all platforms
        panel = Panel(self, ID_ANY)
        self.index = 0
 
        panel1 = Panel(panel, size=(-1, 500))
        self.list_ctrl = ListCtrl(panel1, style=LC_REPORT|BORDER_SUNKEN)
        self.list_ctrl.InsertColumn(0, firstColName, width=150)
        self.list_ctrl.InsertColumn(1, 'Color', width=250)
        sizer1 = GridSizer()
        sizer1.Add(self.list_ctrl, 0, ALL|EXPAND, border=5)
        panel1.SetSizer(sizer1)
 
        panel2 = Panel(panel)
        addNewPairBtn = Button(panel2, label="Add Pair")
        addNewPairBtn.Bind(EVT_BUTTON, self.OnAddNew)
        editPairBtn = Button(panel2, label="Edit")
        editPairBtn.Bind(EVT_BUTTON, self.OnEdit)
        deleteBtn = Button(panel2, label="Delete")
        deleteBtn.Bind(EVT_BUTTON, self.OnDelete)
        okBtn = Button(panel2, label="OK")
        okBtn.Bind(EVT_BUTTON, self.OnOk)
        cancelBtn = Button(panel2, label="Cancel")
        cancelBtn.Bind(EVT_BUTTON, self.OnClose)
        sizer2 = BoxSizer(HORIZONTAL)
        sizer2.Add(addNewPairBtn, border=5)
        sizer2.Add(editPairBtn, border=5)
        sizer2.Add(deleteBtn, border=5)
        sizer2.Add(okBtn, border=5)
        sizer2.Add(cancelBtn, border=5)
        panel2.SetSizer(sizer2)
 
        sizer = BoxSizer(VERTICAL)
        sizer.Add(panel1, 0, ALL|EXPAND)
        sizer.Add(panel2, 0, ALL|CENTER)
        panel.SetSizer(sizer)
    
    def OnOk(self, e):
        self.EndModal(ID_OK)
        
    def OnClose(self, e):
        self.EndModal(ID_CANCEL)
    
    def OnAddNew(self, event):
        newDlg = NewPairDlg()
        while 1:
            if not newDlg.ShowModal() == ID_OK:
                return
            label, color = newDlg.GetPair()
            if not self.AddLine(label, color):
                MessageDialog(None, 'Label existing. Change the label or use Edit instead',
                               'Error', OK | ICON_ERROR).ShowModal()
                continue
            break
        
    def OnEdit(self, event):
        focusedItem = self.list_ctrl.GetFocusedItem()
        if focusedItem == -1:
            return
        label = self.list_ctrl.GetItemText(focusedItem, 0)
        color = Colour()
        color.SetFromName(self.list_ctrl.GetItemText(focusedItem, 1))
        currentItems = self.GetNewDict()
        newDlg = NewPairDlg(label, color)
        while 1:
            if not newDlg.ShowModal() == ID_OK:
                return
            newLabel, newColor = newDlg.GetPair()
            if newLabel != label and newLabel in currentItems:
                continue
            self.list_ctrl.SetItemText(focusedItem, newLabel)
            self.list_ctrl.SetStringItem(focusedItem, 1, newColor.GetAsString())
            self.list_ctrl.SetItemBackgroundColour(focusedItem, newColor)
            break
        
    def OnDelete(self, event):
        item = -1
        while 1:        
            item = self.list_ctrl.GetNextItem(item, LIST_NEXT_ALL, LIST_STATE_SELECTED)
            if item == -1:
                break
            else:
                msg = 'Are you sure to delete key ' + self.list_ctrl.GetItemText(item, 0)
                msg += ' permanently?'
                confirm = MessageDialog(None, msg, 'Confirm', 
                                        YES_NO | NO_DEFAULT | ICON_QUESTION)
                if confirm.ShowModal() == ID_YES:
                    self.RemoveLine(item)
    
    def AddLine(self, label, color, idx=-1):
        currentItems = self.GetNewDict()
        if label in currentItems:
            return False
        line = idx
        if line == -1:
            line = self.index
        self.list_ctrl.InsertStringItem(line, label)
        self.list_ctrl.SetStringItem(line, 1, color.GetAsString())
        self.list_ctrl.SetItemBackgroundColour(line, color)
        self.index += 1
        return True
        
    def RemoveLine(self, idx=-1):
        line = idx
        if line == -1:
            line = self.index
        self.list_ctrl.DeleteItem(line)
        self.index -= 1
        
    def AddItems(self, items):
        for k, v in items.iteritems():
            colorTuple = [int(i * 255) for i in v]
            color = Colour(colorTuple[0], colorTuple[1], colorTuple[2])
            self.AddLine(str(k), color)
    
    def GetNewDict(self, ktype = 'string'):
        ret = {}
        item = -1
        while 1:        
            item = self.list_ctrl.GetNextItem(item)
            if item == -1:
                break
            else:
                key = self.list_ctrl.GetItemText(item, 0)
                if ktype == 'int':
                    if key.isdigit():
                        key = int(key)
                    else:
                        raise TypeError("One of keys cannot be converted to int")
                color = Colour()
                color.SetFromName(self.list_ctrl.GetItemText(item, 1))
                # divide to 255 to fit with color used in OpenGL
                ret[key] = [i / 255.0 for i in color.Get()]
        return ret