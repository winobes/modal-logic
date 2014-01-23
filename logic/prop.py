def atom(f):
    return len(f) == 1

# Convert a formula to a string.
def fml_to_str(f):
    if atom(f):
        s = f[0]
    elif f[0] == 'not':
        s = '~' + subfml_to_str(f[1])
    elif f[0] == 'and' or f[0] == 'or':
        s = ''
        for i in range(len(f[1])):
            s += subfml_to_str(f[1][i])
            if i != len(f[1]) - 1:
                if f[0] == 'and':
                    s += ' & '
                else:
                    s += ' V '
    elif f[0] == 'arrow':
        s = subfml_to_str(f[1]) + ' -> ' + subfml_to_str(f[2])
    else:
        raise ValueError('unknown operator:', f[0])

    return s

# Helper function for fml_to_str(): enclose a subformula in parentheses if
# necessary.
def subfml_to_str(f):
    if (f[0] == 'and' or f[0] == 'or') and len(f[1]) != 1:
        return '(' + fml_to_str(f) + ')'
    if f[0] == 'arrow':
        return '(' + fml_to_str(f) + ')'
    return fml_to_str(f)

# Return a random formula.
def random_fml(natoms = (2, 8)):
    from random import randrange
    from util import get_random_item, pop_random_item

    if natoms[0] < 1 or natoms[0] >= natoms[1]:
        raise ValueError('invalid range')

    atoms = ('p', 'q', 'r', 's')
    operators = ('not', 'and', 'or', 'arrow')

    natoms = randrange(*natoms)
    fmls = []

    for i in range(natoms):
        fmls.append(get_random_item(atoms))

    while len(fmls) > 1:
        o = get_random_item(operators)
        if o == 'not':
            fmls.append(('not', pop_random_item(fmls)))
        elif o == 'and':
            nconjuncts = randrange(2, int(len(fmls) / 2) + 2)
            fmls.append(('and',
                [pop_random_item(fmls) for i in range(nconjuncts)]))
        elif o == 'or':
            ndisjuncts = randrange(2, int(len(fmls) / 2) + 2)
            fmls.append(('or',
                [pop_random_item(fmls) for i in range(ndisjuncts)]))
        elif o == 'arrow':
            fmls.append(('arrow', pop_random_item(fmls), pop_random_item(fmls)))
        else:
            raise ValueError('unexpected operator:', o)

    return fmls[0]

# Evaluate the formula f. The valuation val is a dictionary from proposition
# letters to truth values.
def evaluate(f, val):
    if atom(f[0]):
        if not f[0] in val:
            raise ValueError('atom not in valuation:', f[0])
        return val[f[0]]
    if f[0] == 'not':
        return not evaluate(f[1], val)
    if f[0] == 'and':
        return all(evaluate(g, val) for g in f[1])
    if f[0] == 'or':
        return any(evaluate(g, val) for g in f[1])
    if f[0] == 'arrow':
        return not evaluate(f[1], val) or evaluate(f[2], val)
    raise ValueError('unknown operator:', f[0])

# Convert each implicative subformula to a disjunctive one.
def impl_to_disj(f):
    if atom(f):
        return f
    if f[0] == 'not':
        return ('not', impl_to_disj(f[1]))
    if f[0] == 'or' or f[0] == 'and':
        return (f[0], [impl_to_disj(g) for g in f[1]])
    if f[0] == 'arrow':
        return ('or', [('not', impl_to_disj(f[1])), impl_to_disj(f[2])])
    raise ValueError('unknown operator:', f[0])

# Convert to negation normal form.
def nnf(f):
    return nnf_do(impl_to_disj(f))

# Helper function for nnf().
def nnf_do(f):
    if atom(f):
        return f
    elif f[0] == 'not':
        if atom(f[1]):
            return f
        elif f[1][0] == 'not':
            return nnf_do(f[1][1])
        elif f[1][0] == 'and':
            return ('or', [nnf_do(('not', g)) for g in f[1][1]])
        elif f[1][0] == 'or':
            return ('and', [nnf_do(('not', g)) for g in f[1][1]])
        else:
            raise ValueError('unknown operator:', f[1][0])
    elif f[0] == 'and' or f[0] == 'or':
        return (f[0], [nnf_do(g) for g in f[1]])
    elif f[0] == 'arrow':
        return ('arrow', nnf_do(f[1]), nnf_do(f[2]))
    raise ValueError('unknown operator:', f[0])

# Convert to conjunctive normal form.
def cnf(f):
    return cnf_remove_dups(remove_double_neg(cnf_flatten(cnf_do(nnf(f)))))

# Helper function for cnf().
def cnf_do(f):
    if atom(f) or f[0] == 'not':
        return f
    if f[0] == 'and':
        return ('and', [cnf_do(g) for g in f[1]])
    if f[0] == 'or':
        if len(f[1]) == 0:
            return f
        if len(f[1]) == 1:
            return cnf_do(f[1][0])
        return cnf_distribute(cnf_do(f[1][0]), cnf_do(('or', f[1][1:])))
    raise ValueError('unknown operator:', f[0])

# Helper function for cnf(): distribute disjunction over conjunction.
def cnf_distribute(f1, f2):
    if f1[0] == 'and':
        if len(f1[1]) == 0:
            return f1
        if len(f1[1]) == 1:
            return cnf_distribute(f1[1][0], f2)
        return ('and', [cnf_distribute(f1[1][0], f2)] +
            [cnf_distribute(g, f2) for g in f1[1][1:]])
    if f2[0] == 'and':
        if len(f2[1]) == 0:
            return f2
        if len(f2[1]) == 1:
            return cnf_distribute(f1, f2[1][0])
        return ('and', [cnf_distribute(f1, f2[1][0])] +
            [cnf_distribute(f1, g) for g in f2[1][1:]])
    return ('or', [f1, f2])

# Helper function for cnf(): collapse conjunction lists and disjunction lists.
def cnf_flatten(f):
    if f[0] == 'and':
        return ('and', cnf_flatten_conj(f[1]))
    if f[0] == 'or':
        return ('or', cnf_flatten_disj(f[1]))
    return f

# Helper function for cnf_flatten().
def cnf_flatten_conj(flist):
    if flist == []:
        return flist
    if flist[0][0] == 'and':
        return cnf_flatten_conj(flist[0][1] + flist[1:])
    return [cnf_flatten(flist[0])] + cnf_flatten_conj(flist[1:])

# Helper function for cnf_flatten().
def cnf_flatten_disj(flist):
    if flist == []:
        return flist
    if flist[0][0] == 'or':
        return cnf_flatten_disj(flist[0][1] + flist[1:])
    return [flist[0]] + cnf_flatten_disj(flist[1:])

# Helper function for cnf(): remove duplicate disjuncts and conjuncts.
def cnf_remove_dups(f):
    if f[0] == 'and':
        # TODO: Remove duplicates in "and" list.
        return ('and', [cnf_remove_dups(g) for g in f[1]])
    if f[0] == 'or':
        return ('or', list(set(f[1])))
    return f

# Remove double negations.
def remove_double_neg(f):
    if atom(f):
        return f
    if f[0] == 'not':
        if f[1][0] == 'not':
            return f[1][1]
        return f
    if f[0] == 'and' or f[0] == 'or':
        return (f[0], [remove_double_neg(g) for g in f[1]])
    if f[0] == 'arrow':
       return ('arrow', remove_double_neg(f[1]), remove_double_neg(f[2]))
    raise ValueError('unknown operator:', f[0])

# Returns the set of propositions in f.
def get_atoms(f):
    atoms = set() 
    if atom(f):
        atoms.add(f[0])
        return atoms 
    if f[0] == 'not':
        return atoms | get_atoms(f[1])
    if f[0] == 'arrow':
        return atoms | get_atoms(f[1]) | get_atoms(f[2])
    if f[0] == 'or' or f[0] == 'and':
        return atoms.union(*[get_atoms(g) for g in f[1]]) 
    raise ValueError('unknown operator:', f[0]) 

# Returns True if f evaluates to False for every possible valuation.
def is_contr(f):
    atoms = get_atoms(f)
    truth_table = gen_tt(atoms)
    return all(not evaluate(f, val) for val in truth_table)

# Returns True if f evaluates to True for every possible valuation.
def is_valid(f):
    atoms = get_atoms(f)
    truth_table = gen_tt(atoms)
    return all(evaluate(f, val) for val in truth_table)

# Returns True if f and g have the same truth value for every possible valuation.
def are_equiv(f, g):
    atoms = get_atoms(f) | get_atoms(g)    
    truth_table = gen_tt(atoms)
    return  all(evaluate(f, val) == evaluate(g, val) for val in truth_table)

# Generates all possible valuations for a given set of atoms.     
def gen_tt(atoms):
    from itertools import product
    return [{p:val for (p, val) in zip(atoms, vals)} for vals in 
         product([False, True], repeat=len(atoms))]


"""
def remove_dups(f):
    if atom(f):
        return f
    if f[0] == 'not':
        return ('not', remove_dups(f[1]))
    if f[0] == 'and' or f[0] == 'or':
        f[1] = [remove_dups(g) for g in f[1]]
        i = 0
        while i < len(f[1]):
            j = i + 1
            while j < len(f[1]):
                if f[i][0] != 'and' and f[i][0] != 'or':
                    if (f[1][i] == f[1][j])
                        f[1].remove(f[1][j])
                else
                    # ...
                j += 1
            i += 1
    if f[0] == 'arrow':
        return ('arrow', remove_dups(f[1]), remove_dups(f[2]))
    raise ValueError('unknown operator:', f[0])
"""
