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
        self.U = ((self.U / self.C) + (self.I * self.dT)) / self.C
        print(self.U, self.I)
        
class power(wire):
    def __init__(self, U, name, r=0):
        super().__init__(name)
        self.U = U
        self.r = r
        
graph = {
  1: {3: "P1+", 2: "W1+"},
  2: {1: "W1-", 4: "R1+"},
  3: {1: "P1-", 4: "W2-"},
  4: {2: "R1-", 3: "W2+"},
}

characteristics = {
  "P1": 10,
  "R1": 10,
  "W1": None,
  "W2": None
}
 
class circuit:
    def __init__(self, graph, characteristics):
        self.graph = graph
        self.cycles = init.SecondLawCycles(graph)
        self.elements_symbols = [] # символьные переменные
        self.elements_names = [] # названия элементов
        self.elements = {} # Все элементы цепи. Имя - объект класса
        self.updating_elements = []
        self.init_elements(characteristics)
        self.init_equations()
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
                self.elements.update({i: capacitor(a[0], a[1], i)})
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
        print(self.equations)
        for i in self.equations:
            eq = sp.Eq(i[0], i[1])
            self.equations_sp.append(eq)
        print("Инициализация уравнений закончилась.")
            
    def second_law_equations(self):  
        print("    Инициализация уравнений по второму закону...")
        for i in self.cycles:
            equation = 0
            EDS = 0
            for j in i:
                if j[0] == 'P':
                    if j[-1] == '-':
                        EDS += self.elements[j[:-1:]].U
                        equation = equation + self.elements[j[:-1:]].symbolI * self.elements[j[:-1:]].r
                    else:
                        EDS -= self.elements[j[:-1:]].U
                        equation = equation - self.elements[j[:-1:]].symbolI * self.elements[j[:-1:]].r
                elif j[0] == 'R':
                    if j[-1] == '-':
                        equation = equation - self.elements[j[:-1:]].symbolI * self.elements[j[:-1:]].R
                    else:
                        equation = equation + self.elements[j[:-1:]].symbolI * self.elements[j[:-1:]].R
                # далее необходимо добавить конденсаторы!
                
            self.equations.append([equation, EDS])
            print("    Инициализация уравнений по второму закону закончилась.")
    def first_law_equations(self):
        print("    Инициализация уравнений по первму закону...")
        for i in self.graph:
            equation = 0
            for j in self.graph[i]:
                if self.graph[i][j][0] == 'P':
                    if self.graph[i][j][-1] == '+':
                        equation = equation - self.elements[graph[i][j][:-1:]].symbolI
                    else:
                        equation = equation + self.elements[graph[i][j][:-1:]].symbolI
                elif self.graph[i][j][0] == 'R':
                    if self.graph[i][j][-1] == '+':
                        equation = equation + self.elements[graph[i][j][:-1:]].symbolI
                    else:
                        equation = equation - self.elements[graph[i][j][:-1:]].symbolI
                elif self.graph[i][j][0] == 'W':
                    if self.graph[i][j][-1] == '+':
                        equation = equation + self.elements[graph[i][j][:-1:]].symbolI
                    else:
                        equation = equation - self.elements[graph[i][j][:-1:]].symbolI                   
            self.equations.append([equation, 0])
        print("    Инициализация уравнений по первму закону закончилась.")
            
    def solve_equations(self):
        a = list(list(sp.linsolve(self.equations_sp, self.elements_symbols))[0])
        for i in range(len(a)):
            self.elements[self.elements_names[i]].I = a[i]
                        
if __name__ == '__main__':
    a = circuit(graph, characteristics)
    
    time1 = t.time()
    for i in range(100):
        a.solve_equations()
        
    time2 = t.time()
    print("Время решения 100 раз:", time2 - time1)
    
    a.solve_equations()
    b = a.elements
    for i in b:
        print(b[i].name, b[i].I)