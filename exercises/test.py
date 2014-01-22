from formula import Formula, Language, Operator
from propositional_logic import conjunctive_normal_form, list_conjuncts, negation_normal_form, Truthtable, L

phi = L.build('p->q')
psi = L.build('arrow', phi[1], phi[2])

for i in range(10):
    f = L.random_formula((1, 10))
    f_nnf = negation_normal_form(f)
    f_cnf = conjunctive_normal_form(f)
    t = Truthtable(f)
    t_nnf = Truthtable(f_nnf)
    t_cnf = Truthtable(f_cnf)
    print('f:     ', f)
    print('f_nnf: ', f_nnf)
    print('f_cnf: ', f_cnf)
    print('t == t_nnf:', t.is_equal(t_nnf))
    print('t == t_cnf:', t.is_equal(t_cnf))
    for c in list_conjuncts(conjunctive_normal_form(f)):
        print(c)
    print()



#Sigma = [L.random_formula((5,10)) for i in range(100)]
#print("Generated formulas.")
#Delta = [conjunctive_normal_form(f) for f in Sigma]
#print("Got Conjunctive Normal Forms.")
#print()
#
#print("Searching for equivallences in standard form...")
#for f in Sigma:
    #for g in Sigma:
        #if Truthtable(f).is_equal(Truthtable(g)) and not f == g: 
            #print("\tFound equvallent formulas:")
            #print('\t', f)
            #print('\t', g)
#print("Done.")
#
#print("Searching for equivallences in CNF...")
#for f in Delta:
    #for g in Delta:
        #if Truthtable(f).is_equal(Truthtable(g)) and not f == g: 
            #print("\tFound equvallent formulas:")
            #print('\t', f)
            #print('\t', g)
#print("Done.")
#
