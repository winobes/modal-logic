import structure 
import syntax
import semantics

F1 = structure.Frame(set(), set())
F2 = structure.Frame(set(), set())
F3 = structure.Frame(set(), set())

F1.add_worlds({'w','u', 'v'})
F2.add_worlds(set(range(10)))
F3.add_worlds({n + 1 for n in range(100)})

F1.add_edges({('w', 'v'), ('v', 'v'), ('v', 'w'), ('w', 'u')})
F2.add_edges({(s,t) for s in F2.W for t in F2.W if s < t})
F3.add_edges({(s,t) for s in F3.W for t in F3.W if s % t == 0})

V1 = {'p': {'w','v','u'}, 'q': {'w','u'}, 'r': {'v'}}
V2 = {'p': {s for s in F2.W if s % 2 == 0}, 
      'q': {t for t in F2.W if t % 2 == 1}}
V3 = {'p': {s for s in F2.W if s % 3 == 0}, 
      'q': {s for s in F2.W if s % 3 == 1}, 
      'r': {t for t in F2.W if t % 3 == 2}}

M1 = structure.Model(F1,V1)
M2 = structure.Model(F2,V2)
M3 = structure.Model(F3,V3)

print(M1, '\n')
print(M2, '\n')
# print(M3, '\n')

# Call syntax.Language with no arguments for basic modal language
BML = syntax.Language()

# phi = (◻ p ∧ (◇ r ∨ ¬(r → ◻ q)))
phi = syntax.parse_formula(BML, "\u25FB p \u2227 (\u25C7 r \u2228 \u00AC(r \u2192 \u25FB q))")
# psi = (p ∧ q)
psi = syntax.parse_formula(BML, "p \u2228 r")

print("phi =", phi)
print("psi =", psi, '\n')


print("Evaluate phi at M1,w:", semantics.evaluate(M1, 'w', phi))
print("Evaluate psi at M1,w:", semantics.evaluate(M1, 'w', psi))
print("Evaluate phi at M1,v:", semantics.evaluate(M1, 'u', phi))
print("Evaluate psi at M1,v:", semantics.evaluate(M1, 'u', psi))
print("Evaluate phi at M1,u:", semantics.evaluate(M1, 'v', phi))
print("Evaluate psi at M1,u:", semantics.evaluate(M1, 'v', psi))

print("Evaluate phi at M2,1:", semantics.evaluate(M2, 1, phi))
print("Evaluate psi at M2,2:", semantics.evaluate(M2, 2, psi))
print("Evaluate phi at M2,3:", semantics.evaluate(M2, 3, phi))
print("Evaluate psi at M2,4:", semantics.evaluate(M2, 4, psi))
print("Evaluate phi at M2,5:", semantics.evaluate(M2, 5, phi))
print()

print("Submodel generated by (M2, 5):")
print(structure.generate_submodel(M2, 5), '\n')
print("Submodel generated by (M2, 4):")
print(structure.generate_submodel(M2, 4), '\n')
print("Submodel generated by (M1, 'u'):")
print(structure.generate_submodel(M1, 'u'), '\n')
