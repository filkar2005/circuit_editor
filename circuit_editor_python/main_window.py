import graphics.graphiс_classes as gr_cl
from graphics.graphiс_classes import wx

class main_window(wx.Frame):
    def __init__(self, parent, title, size):
        super().__init__(parent, title=title, size=size)
        self.draw_k = 1           # коэффициент для изменения масштаба.
        self.coord = (0, 0)       # координаты начальной точки, относительно которой всё и считается
        self.position = (0, 0)    # просто необходима для нахождения delta_pos
        self.activ_element = 0    # индекс активного элемента, при -1 - движение по рабочей области, иначе - новый элемент.
        self.texts = []
        self.is_make_new_element = 0
        
        self.all_elements = {       # собственно, ссылки на все элементы
            0: [None, "Перемещение по рабочему пространству"], 
            1: [gr_cl.wire, "Добавить провод"],
            2: [gr_cl.resistor, "Добавить резистор"],
            3: [gr_cl.power, "Добавить источник питания"],
            4: [gr_cl.capacitor, "Добавить конденсатор"]
            }
        
        self._init_frame()
        
        self.list_objects = wx.SplitterWindow(self, wx.ID_ANY, style=wx.SP_LIVE_UPDATE|wx.SP_NOBORDER)
        self.list_objects.SetMinimumPaneSize(150)
        self.listbox = wx.ListBox(self.list_objects)
        self.panel = wx.Panel(self.list_objects)
        self.list_objects.SplitVertically(self.listbox, self.panel)
        self.list_objects.SetSashPosition(250)
        
        
        #  Инициализация событий. Желательно всё сюда пихать, а то вконец запутаюсь.
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_PAINT, self.onPaint)
        self.panel.Bind(wx.EVT_MOTION, self.onChangePosMouse)
        self.panel.Bind(wx.EVT_MOUSEWHEEL, self.onChangeK)
        self.panel.Bind(wx.EVT_LEFT_UP, self.onLeftUp)
        self.listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.on_listbox_double)
        self.listbox.Bind(wx.EVT_LISTBOX, self.on_listbox)
        
        self.elements = []   # список, содержащий все добавленные элементы.
        self.coordinats = set([])  # список, содеоржащий координаты элементов, для ускорения работы
        
        self.stbar = self.CreateStatusBar()
        self.stbar.SetStatusText(self.all_elements[self.activ_element][1])
        
        self.Show()
        
    def _init_frame(self):
        self.menubar = wx.MenuBar()
        self.SetMenuBar(self.menubar)
        
        self.fileMenu = wx.Menu()
        self.fileMenu.Append(wx.ID_OPEN, "Открыть", "Открыть схему")
        self.fileMenu.Append(wx.ID_EXIT, "Выход", "Выход из приложения")
        
        self.editMenu = wx.Menu()
        self.kindEditMenu = wx.Menu()
        for i in self.all_elements:
            self.kindEditMenu.Append(i, str(self.all_elements[i][1]), kind=wx.ITEM_RADIO)
        self.kindEditMenu.Bind(wx.EVT_MENU, self.onChangeKind)
        self.editMenu.AppendSubMenu(self.kindEditMenu, "Выбор элемента:")

        
        self.menubar.Append(self.fileMenu, "&Файл")
        self.menubar.Append(self.editMenu, "&Редактировать")
        
        self.toolbar = self.CreateToolBar()
        self.toolbar.AddTool(wx.ID_SETUP, "Запуск", wx.Bitmap("graphics/setup.bmp"))
        self.toolbar.AddTool(wx.ID_STOP, "Стоп", wx.Bitmap("graphics/stop.bmp"))
        self.toolbar.Realize()
        
        self.Bind(wx.EVT_MENU, self.on_close, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_import, id=wx.ID_OPEN)
        self.toolbar.Bind(wx.EVT_TOOL, self.calculation)
        
        
    def on_exit(self, event):
        print("    *Официальное закрытие*")
        self.Destroy()
        
    def on_import(self, event):
        print("    *импорт*")
        
    def on_close(self, event):
        print("    *Закрытие окна*")
        window = wx.MessageDialog(None, "Вы действительно хотите выйти?", 'Вопрос', wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
        result = window.ShowModal()
        
        if result == wx.ID_YES:
            self.on_exit(None)
        else:
            print("    *Сброс закрытия окна*")
            event.Veto()
    
    # основная функция по рисованию.
    def onPaint(self, e):
        k = self.draw_k
        x, y = self.coord
        dc = wx.PaintDC(self)
        
        for i in self.elements:
            i.draw(dc, self.coord, k)

        
        
    def onChangePosMouse(self, e): 
        if e.Dragging():
            if self.activ_element == 0:
                coord = (e.GetX(), e.GetY())
                delta = (coord[0] - self.position[0], coord[1] - self.position[1])
                self.coord = (self.coord[0] + delta[0]*self.draw_k, self.coord[1] + delta[1]*self.draw_k)
                self.Refresh()
            else:
                self.onAppendElement(e)
        self.position = (e.GetX(), e.GetY())
        
    def onAppendElement(self, e): 
        coord = e.GetPosition()
        size_sash = self.list_objects.GetSashPosition() +  self.list_objects.GetSashSize()
        x, y = self.coord
        k = self.draw_k
        
        if self.is_make_new_element == 0:
            coord0 = self._point_near(self.coordinats, (coord[0], coord[1]), 20)
            self.elements.append(self.all_elements[self.activ_element][0]("R1", ((size_sash + coord0[0])*k - x, (coord0[1])*k - y), ((size_sash + coord0[0])*k - x + 1, (coord0[1])*k - y + 1)))
            self.is_make_new_element = 1
            self.coordinats.add(coord0)
        else:
            self.elements[-1].coord1 = ((size_sash + coord[0])*k - x, (coord[1])*k - y)
            self.elements[-1].update_coords()
            self.Refresh()
    
    def _distance(self, point1, point2):
        x0, y0 = point1
        x, y = point2
        return gr_cl.math.sqrt((x - x0)**2 + (y - y0)**2)
    
    def _point_near(self, points, point, near):
        is_near = False
        nearest = 10000
        point_near = None
        for i in points:
            l = self._distance(i, point)
            if l <= near:
                is_near = True
                if l < nearest:
                    nearest = l
                    point_near = i
        if is_near:
            return point_near
        else:
            return point
    
    def onChangeK(self, e):
        self.draw_k += e.GetWheelRotation() / 1000
        self.Refresh()
    
    def onChangeKind(self, e):
        self.activ_element = e.GetId()
        self.stbar.SetStatusText(self.all_elements[self.activ_element][1])
    
    def onLeftUp(self, e):
        if self.is_make_new_element:    
            size_sash = self.list_objects.GetSashPosition() +  self.list_objects.GetSashSize()
            x, y = self.coord
            k = self.draw_k
            coord = e.GetPosition()
            coord0 = self._point_near(self.coordinats, (coord[0], coord[1]), 20)
            self.elements[-1].coord1 = ((size_sash + coord0[0])*k - x, (coord0[1])*k - y)
            self.elements[-1].update_coords()
            self.coordinats.add(coord0)
            self.Refresh()
            
            self.is_make_new_element = 0
            self.elements[-1].make_dialog(self)
            
            self.listbox.Append("  " + self.elements[-1].type + "  " + self.elements[-1].name)
            
    def on_listbox_double(self, e):
        id_element = self.listbox.GetSelection()
        self.elements[id_element].make_dialog(self)
        if self.elements[id_element].is_activ == -1:
            self.elements.pop(id_element)
        self.listbox.Clear()
        for i in self.elements:
            self.listbox.Append("  " + i.type + "  " + i.name)
        
        self.Refresh()
        
    def on_listbox(self, e):
        id_element = self.listbox.GetSelection()
        for i in self.elements:
            i.is_activ = 0
        self.elements[id_element].is_activ = 1
        self.Refresh()
        
    def calculation(self, e):
        ID = e.GetId()
        if ID == wx.ID_SETUP:
            print("Начать расчёты")
        elif ID == wx.ID_STOP:
            print("Закончить расчёты")
                
            
    
app = wx.App()

frame = main_window(None, 'Симулятор электрических схем', (1200, 800))

app.MainLoop()