import structure 
import syntax
import semantics

F1 = structure.Frame(set(), set())
F2 = structure.Frame(set(), set())

F1.add_worlds({'w','u', 'v'})
F2.add_worlds(set(range(10)))

F1.add_edges({('w', 'v'), ('v', 'v'), ('v', 'w'), ('w', 'u')})
F2.add_edges({(s,t) for s in F2.W for t in F2.W if s < t})

print(F1, '\n')
print(F2, '\n')

V1 = {'p': {'w','v','u'}, 'q': {'w','u'}, 'r': {'v'}}
V2 = {'p': {s for s in F2.W if s % 2 == 0}, 'q': {t for t in F2.W if t % 2 == 1}}

M1 = structure.Model(F1,V1)
M2 = structure.Model(F2,V2)

print(M1, '\n')
print(M2, '\n')

# Call syntax.Language with no arguments for basic modal language (default).
BML = syntax.Language()

# phi = (◻ p ∧ (◇ r ∨ ¬(r → ◻ q)))
phi = syntax.parse_formula(BML, "\u25FB p \u2227 (\u25C7 r \u2228 \u00AC(r \u2192 \u25FB q))")
# psi = (p ∧ q)
psi = syntax.parse_formula(BML, "p \u2228 r")

print("phi =", phi)
print("psi =", psi, '\n')

print("Evaluate psi at M1,w:", semantics.evaluate(M1, 'w', psi))
print("Evaluate phi at M1,w:", semantics.evaluate(M1, 'w', psi))
