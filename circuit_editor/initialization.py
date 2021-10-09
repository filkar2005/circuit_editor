'''
Файл готов, изменению не подлежит!
Функция SecondLawCycles() должна возвращать
все циклы для второго закона.
'''

def DFS(graph, start, end, way=[]):
    way = way + [start]
    if start == end:
        return way
    for node in graph[start]:
        if node not in way:
            new_way = DFS(graph, node, end, way)
            if new_way:
              return new_way
    return []

def AllCycles(graph):
  cycles = []
  for i in graph:
    for a in graph[i]:
      cycle = DFS(graph, i, a)
      if len(cycle) > 2:
        cycles.append(cycle)
  return cycles
 
def DeleteIdenticalCycles(cycles):
  test_cycles = []
  while test_cycles != cycles:
    test_cycles = cycles.copy()
    for i in cycles:
      for a in cycles:
        if i != a and set(i) == set(a):
          cycles.remove(i)
          break
  return cycles
 
def SecondLawCycles(graph):
  cycles = DeleteIdenticalCycles(AllCycles(graph))
  cycles_elements = []
  for i in cycles:
    elements = []
    for a in range(len(i)):
      if i[-1] == i[a]:
        elements.append(graph[i[a]][i[0]])
      else:
        elements.append(graph[i[a]][i[a + 1]])
    cycles_elements.append(elements)
  return cycles_elements