from formula import Operator, Formula, L, Language

# TODO change to commented when we have defined a good op __eq__
arrow = [op for op in L.operators if op.ascii_symbol == '->'][0]
land = [op for op in L.operators if op.ascii_symbol == '&'][0]
lor = [op for op in L.operators if op.ascii_symbol == '|'][0]
lnot = [op for op in L.operators if op.ascii_symbol == '~'][0]

def remove_arrows(f):
    """
    Transform implication subformulas into or subformulas.
    """
    #arrow = Operator('->', '\u2192', lambda x, y: not x or y, 2)
    #lor   = Operator('|', '\u2228', lambda x, y: x or y, 2)
    #lnot  = Operator('~', '\u00ac', lambda x: not x,      1)
    build = L.build_formula

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

    if f.is_atomic():
        return f
    elif f.operator() == lnot:
        if f[1].is_atomic():
            return f
        elif f[1].operator() == lnot:
            return negation_normal_form(f[1][1])
        else:
            if f[1].operator == land:
                return L.build_formula(lor,
                    negation_normal_form(L.build_formula(lnot, f[1][1])),
                    negation_normal_form(L.build_formula(lnot, f[1][2])))
            else:
                return L.build_formula(land,
                    negation_normal_form(L.build_formula(lnot, f[1][1])),
                    negation_normal_form(L.build_formula(lnot, f[1][2])))
    else:
        return L.build_formula(f.operator(), negation_normal_form(f[1]),
            negation_normal_form(f[2]))
