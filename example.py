from modal import Frame
from modal import Model

R1 = {('a', 'b'), ('a', 'c'), ('b', 'a')}
R2 = {('a', 'a'), ('b', 'b'), ('c', 'c'), ('a', 'b'), ('b', 'a')}

W1 = {'a','b'}
W2 = {'a', 'b', 'c'} 


F1 = Frame(W1,[R1])
F2 = Frame(W2,[R2])

print("F1:")
print(F1)

print("F2:")
print(F2)

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
