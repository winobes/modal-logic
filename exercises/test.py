from formula import Formula, L, Language, Operator
from random_formula import generate_random_formula
from normal_form import conjunctive_normal_form, list_conjuncts, negation_normal_form
from truthtable import Truthtable

for i in range(10):
    f = generate_random_formula(L, (1, 10))
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
