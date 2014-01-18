def remove_arrows(f):
    """
    Transform implication subformulas into or subformulas.
    """

    if len(f) == 1:
        return f
    elif len(f) == 2:
        return (f[0], remove_arrows(f[1]))
    elif not f[0] == 'arrow':
        return (f[0], remove_arrows(f[1]), remove_arrows(f[2]))
    else:
        return ('or', ('not', remove_arrows(f[1]), remove_arrows(f[2])))

def negation_normal_form(f):
    f = remove_arrows(f)

    if len(f) == 1:
        return f
    elif len(f) == 2:
        if len(f[1]) == 1:
            return f
        elif len(f[1]) == 2:
            return negation_normal_form(f[1][1])
        else:
            if f[1][0] == 'and':
                return ('or', negation_normal_form(('not', f[1][1])), negation_normal_form(('not', f[1][2])))
            else:
                # or
                return ('and', negation_normal_form(('not', f[1][1])), negation_normal_form(('not', f[1][2])))
    else:
        return (f[0], negation_normal_form(f[1]), negation_normal_form(f[2]))

def conjunctive_normal_form(f):
    f = negation_normal_form(f)

def make_main_connective_and(f):
    i=0
    while not f[i][0] = 'and'

from random_formula import generate_random_formula

for i in range(10):
    f = generate_random_formula((2, 5))
    print("original: ", f)
    print("nnf:      ", negation_normal_form(f))
    print()
