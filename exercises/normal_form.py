from formula import Operator, Formula, Language

def remove_arrows(f):
    """
    Transform implication subformulas into or subformulas.
    """
    #arrow = Operator('->', '\u2192', lambda x, y: not x or y, 2)
    #lor   = Operator('|', '\u2228', lambda x, y: x or y, 2)
    #lnot  = Operator('~', '\u00ac', lambda x: not x,      1)
    build = f.language.build_formula

    # TODO change to commented when we have defined a good op __eq__
    arrow = [op for op in f.language.operators if op.ascii_symbol == '->'][0]
    lor = [op for op in f.language.operators if op.ascii_symbol == '|'][0]
    lnot = [op for op in f.language.operators if op.ascii_symbol == '~'][0]

    if f.depth() == 0:
        return f
    elif f[0].arity == 1:
        return build(f[0], remove_arrows(f[1]))
    elif not f[0].ascii_symbol == '->':
        return build(f.operator(), remove_arrows(f[1]), 
                                          remove_arrows(f[2]))
    else:
        return build(lor, build(lnot, remove_arrows(f[1])), remove_arrows(f[2]))

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

"""
TESTING
"""

from random_formula import sigma
from formula import L

for f in sigma:
    print(f)
    print(remove_arrows(f))
    print()


