import structure 

R1 = {('a', 'b'), ('a', 'c'), ('b', 'a')}
R2 = {('a', 'a'), ('b', 'b'), ('c', 'c'), ('a', 'b'), ('b', 'a')}

W1 = {'a','b'}
W2 = {'a', 'b', 'c'} 


F1 = structure.Frame()
F2 = structure.Frame()

F1.add_multiple_worlds(W1)
F2.add_multiple_worlds(W2)

F1.add_relation("R1", 2)
F2.add_relation("R1", 2)
F2.add_relation("R2", 2)

F1.add_multiple_to_relation("R1", R1)
F2.add_multiple_to_relation("R1", R1)
F2.add_multiple_to_relation("R2", R2)

print(F1)

print(F2)

M1 = structure.Model(F1)
M3 = structure.Model()

"""
print(M1)

print(M3)

print("F2 + F1:")
print(F1 + F2)

V = {'p': {'a','b','c'}, 'q': {'c'}, 'r': {'b','c'}}

M1 = Model(F1,V)
M2 = Model(F2,V)

print("M1:")
print(M1)

print("M2:")
print(M2)

print("M1 + M2")
print(Model(F1+F2, V))
"""
