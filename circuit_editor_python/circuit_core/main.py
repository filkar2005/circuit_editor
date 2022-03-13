import sympy as sp
import initialization as init
import time as t
 
class wire:
    def __init__(self, name):
        self.U = 0
        self.I = 0
        self.name = name
        self.symbolI = sp.Symbol(name + 'I')
        print("    Инициализация", self.name)
        
class resistor(wire):
    def __init__(self, R, name):
        super().__init__(name)
        self.R = R
 
class capacitor(wire):
    def __init__(self, C, dT, name, r=0):
        super().__init__(name)
        self.C = C
        self.dT = dT
        self.r = r
        self.symbolU = sp.Symbol(name + 'U')
    def update(self):
        #print(self.U, self.I)
        self.U = (self.U * self.C + self.I * self.dT) / self.C
        
class power(wire):
    def __init__(self, U, name, r=0):
        super().__init__(name)
        self.U = U
        self.r = r
        
class inductance(wire):
    def __init__(self, L, dT, name, r=0):
        super().__init__(name)
        self.dT = dT
        self.L = L
        self.r = r
        self.oldI = 1.9999999999
        self.symbolU = sp.Symbol(name + 'U')
    def update(self):
        dI = self.I - self.oldI
        self.U = self.L * (dI/self.dT)
        print(self.U, self.I)
        self.oldI = self.I

#   Это общий вид данных, передаваемых проге.
graph = {
  1: {3: "P1+", 2: "R1+"},
  2: {1: "R1-", 4: "C2+"},
  3: {1: "P1-", 4: "W2-"},
  4: {2: "C2-", 3: "W2+"},
}

characteristics = {
  "P1": 10,
  "C2": 0.1,
  "R1": 5,
  "W2": None
}
# Вот до сюда.
 
class circuit:
    def __init__(self, graph, characteristics, dT):
        self.dT = dT
        self.graph = graph
        self.cycles = init.SecondLawCycles(graph)
        self.elements_symbols = [] # символьные переменные
        self.elements_names = [] # названия элементов
        self.elements = {} # Все элементы цепи. Имя - объект класса
        self.updating_elements = []
        self.init_elements(characteristics)
        self.init_equations()
        self.first_solve = 1
    def init_elements(self, characteristics):
        print("Инициализация элементов...")
        for i in characteristics:
            if i[0] == 'P':
                a = characteristics[i]
                self.elements.update({i: power(a, i)})
                self.elements_symbols.append(self.elements[i].symbolI)
                self.elements_names.append(self.elements[i].name)
            elif i[0] == 'R':
                a = characteristics[i]
                self.elements.update({i: resistor(a, i)})
                self.elements_symbols.append(self.elements[i].symbolI)
                self.elements_names.append(self.elements[i].name)
            elif i[0] == 'W':
                self.elements.update({i: wire(i)})
                self.elements_symbols.append(self.elements[i].symbolI)
                self.elements_names.append(self.elements[i].name)
            elif i[0] == 'C':
                a = characteristics[i]
                self.elements.update({i: capacitor(a, self.dT, i)})
                self.elements_symbols.append(self.elements[i].symbolI)
                self.elements_names.append(self.elements[i].name)
                self.updating_elements.append(self.elements[i])
            elif i[0] == 'L':
                a = characteristics[i]
                self.elements.update({i: inductance(a, self.dT, i)})
                self.elements_symbols.append(self.elements[i].symbolI)
                self.elements_names.append(self.elements[i].name)
                self.updating_elements.append(self.elements[i])
                
        print("Инициализация элементов закончилась.")
    def init_equations(self):
        print("Инициализация уравнений...")
        self.equations = [] # Уравнения
        self.equations_sp = [] # уравнения в формате библиотеки
        self.second_law_equations()
        self.first_law_equations()
        for i in self.equations:
            eq = sp.Eq(i[0], i[1])
            self.equations_sp.append(eq)
        print("Инициализация уравнений закончилась.")
            
    def second_law_equations(self):  
        print("    Инициализация уравнений по второму закону...")
        print(self.cycles)
        for i in self.cycles:
            equation = 0
            EDS = 0
            for j in i:
                if j[0] == 'P':
                    if j[-1] == '+':
                        EDS += self.elements[j[:-1:]].U
                        equation = equation - self.elements[j[:-1:]].symbolI * self.elements[j[:-1:]].r
                    else:
                        EDS -= self.elements[j[:-1:]].U
                        equation = equation + self.elements[j[:-1:]].symbolI * self.elements[j[:-1:]].r
                elif j[0] == 'R':
                    if j[-1] == '+':
                        equation = equation - self.elements[j[:-1:]].symbolI * self.elements[j[:-1:]].R
                    else:
                        equation = equation + self.elements[j[:-1:]].symbolI * self.elements[j[:-1:]].R
                elif j[0] == 'C':
                    if j[-1] == '+':
                        EDS += self.elements[j[:-1:]].symbolU
                        equation = equation - self.elements[j[:-1:]].symbolI * self.elements[j[:-1:]].r
                    else:
                        EDS -= self.elements[j[:-1:]].symbolU
                        equation = equation + self.elements[j[:-1:]].symbolI * self.elements[j[:-1:]].r
                elif j[0] == 'L':
                    if j[-1] == '+':
                        EDS += self.elements[j[:-1:]].symbolU
                        equation = equation - self.elements[j[:-1:]].symbolI * self.elements[j[:-1:]].r
                    else:
                        EDS -= self.elements[j[:-1:]].symbolU
                        equation = equation + self.elements[j[:-1:]].symbolI * self.elements[j[:-1:]].r
                
            self.equations.append([equation, EDS])
            print(equation, '=', EDS)  #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        print("    Инициализация уравнений по второму закону закончилась.")
    def first_law_equations(self):
        print("    Инициализация уравнений по первму закону...")
        for i in self.graph:
            equation = 0
            for j in self.graph[i]:
                if self.graph[i][j][0] == 'P':
                    if self.graph[i][j][-1] == '+':
                        equation = equation + self.elements[graph[i][j][:-1:]].symbolI
                    else:
                        equation = equation - self.elements[graph[i][j][:-1:]].symbolI
                elif self.graph[i][j][0] == 'R':       # Вот отсюда
                    if self.graph[i][j][-1] == '+':
                        equation = equation - self.elements[graph[i][j][:-1:]].symbolI
                    else:
                        equation = equation + self.elements[graph[i][j][:-1:]].symbolI
                elif self.graph[i][j][0] == 'W':
                    if self.graph[i][j][-1] == '+':
                        equation = equation - self.elements[graph[i][j][:-1:]].symbolI
                    else:
                        equation = equation + self.elements[graph[i][j][:-1:]].symbolI 
                elif self.graph[i][j][0] == 'C':
                    if self.graph[i][j][-1] == '+':
                        equation = equation - self.elements[graph[i][j][:-1:]].symbolI
                    else:
                        equation = equation + self.elements[graph[i][j][:-1:]].symbolI
                elif self.graph[i][j][0] == 'L':
                    if self.graph[i][j][-1] == '+':
                        equation = equation - self.elements[graph[i][j][:-1:]].symbolI
                    else:
                        equation = equation + self.elements[graph[i][j][:-1:]].symbolI #И досюда      
            self.equations.append([equation, 0])# Код можно сократить, не знаю, почему я так написал...
            print(equation, "=", 0) #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        print("    Инициализация уравнений по первму закону закончилась.")
            
    def solve_equations(self):
        try:
            a = sp.linsolve(self.equations_sp, self.elements_symbols)
        
            for i in self.updating_elements:
                a = a.subs(i.symbolU, i.U)
        
            a = list(list(a)[0])
            for i in range(len(a)):
                self.elements[self.elements_names[i]].I = a[i]
            for i in self.updating_elements:
                i.update()
        except:
            a = [None]
            print(''' В схеме содержится ошибка. 
                  Возможно отсутсвуют часть соеденений, возможно где-то короткое замыкание.''')
    

# Этот код не должен быть незаменимым, это лишь проба.                    
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    a = circuit(graph, characteristics, 0.0005)
    gx = []
    gy = []
    
    time1 = t.time()
    time = 0
    for i in range(10000):
        a.solve_equations()
        gx.append(time)
        time += 0.0005
        gy.append(a.elements['C2'].U)
    time2 = t.time()
    print("Время решения 1000 раз:", time2 - time1)
    plt.plot(gx, gy)
    plt.show()
    print()
    b = a.elements
    for i in b:
        print(b[i].name, "=", b[i].I)