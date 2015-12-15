'''
Created on Nov 27, 2014

@author: chuxuankhoi
'''
from wx import Dialog, Panel, BoxSizer, VERTICAL, StaticBox, StaticBoxSizer,\
    HORIZONTAL, StaticText, LEFT, CENTER, ColourPickerCtrl, ALL, EXPAND, Button,\
    ALIGN_CENTER, TOP, BOTTOM, EVT_BUTTON, ID_OK, ID_CANCEL, Colour

class ColorRangeDlg(Dialog):
    upperColor = [0.0, 1.0, 0.0]
    lowerColor = [1.0, 0.0, 0.0]
    
    def __init__(self, upper=upperColor, lower=lowerColor):
        super(ColorRangeDlg, self).__init__(None)
        
        self.upperColor = upper
        self.lowerColor = lower
                    
        self.InitUI()
        self.SetSize((300, 240))
        self.SetTitle("Color range selection")        
        
    def InitUI(self):

        pnl = Panel(self)
        vbox = BoxSizer(VERTICAL)

        sb = StaticBox(pnl, label='Colors')
        sbs = StaticBoxSizer(sb, orient=VERTICAL)
        
        hbox1 = BoxSizer(HORIZONTAL)        
        hbox1.Add(StaticText(pnl, -1, 'Upper color'), flag=LEFT|CENTER)
        self.upperColorCtrl = ColourPickerCtrl(pnl, col=self.ToColour(self.upperColor))
        hbox1.Add(self.upperColorCtrl, flag=LEFT, border=5)
        sbs.Add(hbox1, flag=ALL|EXPAND)
        hbox2 = BoxSizer(HORIZONTAL)        
        hbox2.Add(StaticText(pnl, -1, 'Lower color'), flag=LEFT|CENTER)
        self.lowerColorCtrl = ColourPickerCtrl(pnl, col=self.ToColour(self.lowerColor))
        hbox2.Add(self.lowerColorCtrl, flag=LEFT|EXPAND, border=5)
        sbs.Add(hbox2, flag=ALL|EXPAND)
        
        pnl.SetSizer(sbs)
       
        hbox3 = BoxSizer(HORIZONTAL)
        okButton = Button(self, label='Ok')
        closeButton = Button(self, label='Cancel')
        hbox3.Add(okButton)
        hbox3.Add(closeButton, flag=LEFT, border=5)

        vbox.Add(pnl, proportion=1, 
            flag=ALL|EXPAND, border=5)
        vbox.Add(hbox3, 
            flag=ALIGN_CENTER|TOP|BOTTOM, border=10)

        self.SetSizer(vbox)
        
        okButton.Bind(EVT_BUTTON, self.OnOk)
        closeButton.Bind(EVT_BUTTON, self.OnClose)
        
    def OnOk(self, e):
        self.EndModal(ID_OK)
        
    def OnClose(self, e): 
        self.EndModal(ID_CANCEL)       
        
    def GetUpperColor(self):
        return self.ToOpenGLColor(self.upperColorCtrl.GetColour())
    
    def GetLowerColor(self):
        return self.ToOpenGLColor(self.lowerColorCtrl.GetColour())
    
    def ToColour(self, color):
        r = int(color[0] * 255)
        g = int(color[1] * 255)
        b = int(color[2] * 255)
        return Colour(r, g, b, 255)
    
    def ToOpenGLColor(self, colour):
        r = float(colour.Red()) / 255
        g = float(colour.Green()) / 255
        b = float(colour.Blue()) / 255
        return [r, g, b]