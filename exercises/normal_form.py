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
            if f[1].operator() == land:
                return L.build_formula(lor,
                    negation_normal_form(L.build_formula(lnot, f[1][1])),
                    negation_normal_form(L.build_formula(lnot, f[1][2])))
            elif f[1].operator() == lor:
                return L.build_formula(land,
                    negation_normal_form(L.build_formula(lnot, f[1][1])),
                    negation_normal_form(L.build_formula(lnot, f[1][2])))
            else:
                raise ValueError('unexpected operator:', f[1].operator())
    else:
        return L.build_formula(f.operator(), negation_normal_form(f[1]),
            negation_normal_form(f[2]))

def conjunctive_normal_form(f):
    f = negation_normal_form(f)

    if f.is_atomic() or f.operator() == lnot:
        return f
    elif f.operator() == land:
        return L.build_formula(land,
            conjunctive_normal_form(f[1]),
            conjunctive_normal_form(f[2]))
    else:
        # (A and B) or C
        if f[1].operator() == land:
            return conjunctive_normal_form(L.build_formula(land,
                L.build_formula(lor, f[1][1], f[2]),
                L.build_formula(lor, f[1][2], f[2])))
        # A or (B and C)
        elif f[2].operator() == land:
            return conjunctive_normal_form(L.build_formula(land,
                L.build_formula(lor, f[1], f[2][1]),
                L.build_formula(lor, f[1], f[2][2])))
        else:
            # TODO: Needs a more elegant solution.
            f1 = conjunctive_normal_form(f[1])
            f2 = conjunctive_normal_form(f[2])
            if f[1] == f1 and f[2] == f2:
                return L.build_formula(lor, f[1], f[2])
            else:
                return conjunctive_normal_form(L.build_formula(lor, f1, f2))

def list_conjuncts(f):
    """
    Return a list of the conjuncts of f, where f is assumed to be in
    conjunctive normal form.
    """

    if f.operator() == land:
        return list_conjuncts(f[1]) + list_conjuncts(f[2])
    else:
        return [f]
