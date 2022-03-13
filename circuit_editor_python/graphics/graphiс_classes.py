import wx
import math

class MakeDialog(wx.Dialog):
    def __init__(self, parent, size, style, title, characteristics):
        super().__init__(parent, size=size, style=style, title=title)
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.widgets = []
        self.texts = []
        self.characteristics = characteristics
        for i in characteristics:
            self.widgets.append(wx.BoxSizer())
            self.widgets[-1].Add(wx.StaticText(panel, label=i[1] + ": "), flag = wx.LEFT, border = 20)
            self.texts.append(wx.TextCtrl(panel, value=str(i[0])))
            self.widgets[-1].Add(self.texts[-1], flag = wx.RIGHT|wx.LEFT, border = 10, proportion = 1)
            self.widgets[-1].Add(wx.StaticText(panel, label=i[2]), flag = wx.RIGHT, border = 20)
            vbox.Add(self.widgets[-1], flag = wx.EXPAND|wx.TOP, border = 10)
            
        btn_cls_yes = wx.Button(panel, id=1, label="Сохранить")
        btn_cls_now = wx.Button(panel, id=2, label='Закрыть без сохранения')
        btn_cls_yes.Bind(wx.EVT_BUTTON, self.on_close_new)
        btn_cls_now.Bind(wx.EVT_BUTTON, self.on_close_old)
        btn_delete = wx.Button(panel, id=3, label='Удалить')
        btn_delete.Bind(wx.EVT_BUTTON, self.on_close_delete)
        
        self.widgets.append(wx.BoxSizer())
        self.widgets[-1].Add(btn_cls_yes, flag = wx.RIGHT, border = 10)
        self.widgets[-1].Add(btn_cls_now, flag = wx.LEFT, border = 10)
        vbox.Add(self.widgets[-1], flag=wx.CENTER|wx.TOP, border = 20)
        
        vbox.Add(btn_delete, flag=wx.CENTER|wx.TOP, border=10)
        
        panel.SetSizer(vbox)
        
       # self.Bind(wx.EVT_CLOSE, self.on_close)
        
    def on_close_new(self, e):
        print("закрытие с сохранением")
        for i, a in zip(self.texts, range(len(self.characteristics))):
            self.characteristics[a][0] = i.GetValue()
        self.EndModal(wx.ID_OK)
        
    def on_close_old(self, e):
        print("Закрытие без сохранения")
        self.EndModal(wx.ID_CANCEL)
        
    def on_close_delete(self, e):
        print("Удаление элемента")
        self.EndModal(wx.ID_CLEAR)
    

class element:
    def __init__(self, name, coord0, coord1):
        self.U = 0
        self.I = 0
        self.name = name
        self.coord0 = coord0
        self.coord1 = coord1
        self.is_activ = 0
        
    def make_dialog(self, window):
        with MakeDialog(window, (600, 400), 0, "Настройки элемента", self.characteristics) as dialog:
            res = dialog.ShowModal()
            if res == wx.ID_OK:
                self.characteristics = dialog.characteristics
            elif res == wx.ID_CLEAR:
                self.is_activ = -1
        self.name = self.characteristics[0][0]
    

class wire(element):
    def __init__(self, name, coord0, coord1):
        super().__init__(name, coord0, coord1)
        self.characteristics = [[name, "имя", ""]]
        self.type = "провод"
        
    def draw(self, dc, coord, k):
        if self.is_activ:
            color = wx.RED
        else:
            color = wx.BLACK
            
        dc.SetPen(wx.Pen(color, 3))
        x, y = coord
        dc.DrawLine(int((self.coord0[0] + x)/k), int((self.coord0[1] + y)/k), int((self.coord1[0] + x)/k), int((self.coord1[1] + y)/k))
        dc.SetBrush(wx.Brush(color, wx.SOLID))
        dc.DrawCircle(int((self.coord0[0] + x)/k), int((self.coord0[1] + y)/k), 2)
        dc.DrawCircle(int((self.coord1[0] + x)/k), int((self.coord1[1] + y)/k), 2)
    
    def update_coords(self):
        pass
        
        
        
        
class resistor(element):
    def __init__(self, name, coord0, coord1):
        super().__init__(name, coord0, coord1)
        self.a = 30
        self.b = 60
        self.characteristics = [[name, "имя", ""], [10, "сопротивление", "Ом"]]
        self.type = "резистор"
    
    def update_coords(self):
        x0, y0 = self.coord0
        x, y = self.coord1
        l = math.sqrt((x - x0)**2 + (y - y0)**2)
        a, b = self.a, self.b
        sina = (y - y0)/l
        cosa = (x - x0)/l
        
        x1 = x0 + ((l-b)/2) * cosa
        y1 = y0 + ((l-b)/2) * sina
        self.coord1v = (x1, y1)
        
        x2 = x1 + b*cosa
        y2 = y1 + b*sina
        self.coord2v = (x2, y2)
        
        dx = (a/2)*sina
        dy = (a/2)*cosa
        
        x3 = x1 - dx
        y3 = y1 + dy
        self.coord3v = (x3, y3)
        
        x4 = x2 - dx
        y4 = y2 + dy
        self.coord4v = (x4, y4)
        
        x5 = x1 + dx
        y5 = y1 - dy
        self.coord5v = (x5, y5)
        
        x6 = x2 + dx
        y6 = y2 - dy
        self.coord6v = (x6, y6)
        
    def draw(self, dc, coord, k):
        if self.is_activ:
            color = wx.RED
        else:
            color = wx.BLACK
            
        dc.SetPen(wx.Pen(color, 3))
        x, y = coord
        
        dc.DrawLine(int((self.coord0[0] + x)/k), int((self.coord0[1] + y)/k), int((self.coord1v[0] + x)/k), int((self.coord1v[1] + y)/k))
        dc.DrawLine(int((self.coord2v[0] + x)/k), int((self.coord2v[1] + y)/k), int((self.coord1[0] + x)/k), int((self.coord1[1] + y)/k))
        dc.DrawLine(int((self.coord3v[0] + x)/k), int((self.coord3v[1] + y)/k), int((self.coord4v[0] + x)/k), int((self.coord4v[1] + y)/k))
        dc.DrawLine(int((self.coord5v[0] + x)/k), int((self.coord5v[1] + y)/k), int((self.coord6v[0] + x)/k), int((self.coord6v[1] + y)/k))
        dc.DrawLine(int((self.coord3v[0] + x)/k), int((self.coord3v[1] + y)/k), int((self.coord5v[0] + x)/k), int((self.coord5v[1] + y)/k))
        dc.DrawLine(int((self.coord4v[0] + x)/k), int((self.coord4v[1] + y)/k), int((self.coord6v[0] + x)/k), int((self.coord6v[1] + y)/k))
        
        dc.SetBrush(wx.Brush(color, wx.SOLID))
        dc.DrawCircle(int((self.coord0[0] + x)/k), int((self.coord0[1] + y)/k), 2)
        dc.DrawCircle(int((self.coord1[0] + x)/k), int((self.coord1[1] + y)/k), 2)
        
        
 
    
 
class capacitor(element):
    def __init__(self, name, coord0, coord1, r=0):
        super().__init__(name, coord0, coord1)
        self.characteristics = [[name, "имя", ""], [0.1, "ёмкость", "Ф"]]
        self.r = r
        self.a = 30
        self.b = 10
        self.type = "конденсатор"
    
    def update_coords(self):
        x0, y0 = self.coord0
        x, y = self.coord1
        l = math.sqrt((x - x0)**2 + (y - y0)**2)
        a, b = self.a, self.b
        sina = (y - y0)/l
        cosa = (x - x0)/l
        
        x1 = x0 + ((l-b)/2) * cosa
        y1 = y0 + ((l-b)/2) * sina
        self.coord1v = (x1, y1)
        
        x2 = x1 + b*cosa
        y2 = y1 + b*sina
        self.coord2v = (x2, y2)
        
        dx = (a/2)*sina
        dy = (a/2)*cosa
        
        x3 = x1 - dx
        y3 = y1 + dy
        self.coord3v = (x3, y3)
        
        x4 = x2 - dx
        y4 = y2 + dy
        self.coord4v = (x4, y4)
        
        x5 = x1 + dx
        y5 = y1 - dy
        self.coord5v = (x5, y5)
        
        x6 = x2 + dx
        y6 = y2 - dy
        self.coord6v = (x6, y6)
        
    def draw(self, dc, coord, k):
        if self.is_activ:
            color = wx.RED
        else:
            color = wx.BLACK
            
        dc.SetPen(wx.Pen(color, 3))
        x, y = coord
        
        dc.DrawLine(int((self.coord0[0] + x)/k), int((self.coord0[1] + y)/k), int((self.coord1v[0] + x)/k), int((self.coord1v[1] + y)/k))
        dc.DrawLine(int((self.coord2v[0] + x)/k), int((self.coord2v[1] + y)/k), int((self.coord1[0] + x)/k), int((self.coord1[1] + y)/k))
        dc.DrawLine(int((self.coord3v[0] + x)/k), int((self.coord3v[1] + y)/k), int((self.coord5v[0] + x)/k), int((self.coord5v[1] + y)/k))
        dc.DrawLine(int((self.coord4v[0] + x)/k), int((self.coord4v[1] + y)/k), int((self.coord6v[0] + x)/k), int((self.coord6v[1] + y)/k))
        
        dc.SetBrush(wx.Brush(color, wx.SOLID))
        dc.DrawCircle(int((self.coord0[0] + x)/k), int((self.coord0[1] + y)/k), 2)
        dc.DrawCircle(int((self.coord1[0] + x)/k), int((self.coord1[1] + y)/k), 2)
        
        
        
        
class power(element):
    
    def __init__(self, name, coord0, coord1, r=0):
        super().__init__(name, coord0, coord1)
        self.characteristics = [[name, "имя", ""], [10, "напряжение", "В"]]
        self.r = r
        self.a = 60
        self.b = 10
        self.c = 30
        self.type = "источник питания"
    
    def update_coords(self):
        x0, y0 = self.coord0
        x, y = self.coord1
        l = math.sqrt((x - x0)**2 + (y - y0)**2)
        a, b, c = self.a, self.b, self.c
        sina = (y - y0)/l
        cosa = (x - x0)/l
        
        x1 = x0 + ((l-b)/2) * cosa
        y1 = y0 + ((l-b)/2) * sina
        self.coord1v = (x1, y1)
        
        x2 = x1 + b*cosa
        y2 = y1 + b*sina
        self.coord2v = (x2, y2)
        
        dx1 = (a/2)*sina
        dy1 = (a/2)*cosa
        dx2 = (c/2)*sina
        dy2 = (c/2)*cosa
        
        x3 = x1 - dx2
        y3 = y1 + dy2
        self.coord3v = (x3, y3)
        
        x4 = x2 - dx1
        y4 = y2 + dy1
        self.coord4v = (x4, y4)
        
        x5 = x1 + dx2
        y5 = y1 - dy2
        self.coord5v = (x5, y5)
        
        x6 = x2 + dx1
        y6 = y2 - dy1
        self.coord6v = (x6, y6)
        
    def draw(self, dc, coord, k):
        if self.is_activ:
            color = wx.RED
        else:
            color = wx.BLACK
            
        dc.SetPen(wx.Pen(color, 3))
        x, y = coord
        
        dc.DrawLine(int((self.coord0[0] + x)/k), int((self.coord0[1] + y)/k), int((self.coord1v[0] + x)/k), int((self.coord1v[1] + y)/k))
        dc.DrawLine(int((self.coord2v[0] + x)/k), int((self.coord2v[1] + y)/k), int((self.coord1[0] + x)/k), int((self.coord1[1] + y)/k))
        dc.DrawLine(int((self.coord3v[0] + x)/k), int((self.coord3v[1] + y)/k), int((self.coord5v[0] + x)/k), int((self.coord5v[1] + y)/k))
        dc.DrawLine(int((self.coord4v[0] + x)/k), int((self.coord4v[1] + y)/k), int((self.coord6v[0] + x)/k), int((self.coord6v[1] + y)/k))
        
        dc.SetBrush(wx.Brush(color, wx.SOLID))
        dc.DrawCircle(int((self.coord0[0] + x)/k), int((self.coord0[1] + y)/k), 2)
        dc.DrawCircle(int((self.coord1[0] + x)/k), int((self.coord1[1] + y)/k), 2)
        
    