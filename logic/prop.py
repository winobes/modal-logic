def atom(f):
    return len(f) == 1 

def literal(f):
    return atom(f) or (f[0] == 'not' and atom(f[1]))

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
def random_fml(flen = (2, 8), n_atoms = 4):
    from random import randrange
    from util import get_random_item, pop_random_item

    if flen[0] < 1 or flen[0] >= flen[1]:
        raise ValueError('invalid range')

    default_atoms = [(p,) for p in 'pqrs']
    if n_atoms <= 4:
        atoms = default_atoms[:n_atoms]
    else:
        atoms = [('p' + str(i),) for i in range(n_atoms)]
    operators = ('not', 'and', 'or', 'arrow')

    flen = randrange(*flen)
    fmls = []

    for i in range(flen):
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
    if atom(f):
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

# Converts well-formatted strings into formulas
def parse(fml_str):
    import re
    fml_str = ''.join(fml_str.split())
    re_symbols = {re.escape(s) for s in {'(', ')', '&', '->', 'V', '~'}}
    re_string =  '(' + ''.join(s + '|' for s in re_symbols)[:] + ')'
    fml_lst = list(filter(None, re.split(re_string, fml_str)))
    if len(fml_lst) == 1: 
    # atomic formula
        return fml_str 

    # partition fml_lst by subformula 
    partition = [[]] 
    bracket_stack = []
    i = 0
    for s in fml_lst:
        partition[i].append(s)
        if s == '(':
            bracket_stack.append(s)
        elif s == ')':
            if not (bracket_stack.pop(), s) == ('(', ')'):
                raise ValueError('mismatched brakets')
            if bracket_stack == []:
                i += 1
                partition.append([])
        elif bracket_stack == []:
            if not s == '~' :
                i += 1
                partition.append([])
    partition = partition[:-1]

    # extra outter brackets
    if len(partition) == 1 and (partition[0][0], partition[0][-1]) == ('(', ')'):
        fml = tuple(parse(fml_str[1:-1]))
    # ~ is main connective
    elif len(partition) == 1 and partition[0][0] == '~':
        fml = tuple(['not', parse(fml_str[1:])])
    else: 
        operator = [s[0] for s in partition if len(s) == 1 and s[0] in
                        {'&', 'V', '->'}]
        if not all(operator[0] == o for o in operator):
            raise ValueError(' more than one main connective', fml_str)
        elif len(operator) < 1:
            raise ValueError('subformula has no main connective', fml_str)
        elif operator[0] == '->':
            fml = tuple(['arrow', parse("".join(partition[0])), parse("".join(partition[2])) ])
        elif operator[0] == '&':
            fml = tuple(['and', [parse("".join(s)) for s in partition if not s == ['&'] ] ])
        elif operator[0] == 'V':
            fml = tuple(['or', [parse("".join(s)) for s in partition if not s == ['V'] ] ])
    return fml 

#
# Negation normal form
#

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
    raise ValueError('unexpected operator:', f[0])

#
# Conjunctive normal form
#

# Convert to conjunctive normal form.
def cnf(f):
    return cnf_remove_dups(cnf_flatten(cnf_do(nnf(f))))

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
        else:
            return cnf_distribute(cnf_do(f[1][0]), cnf_do(('or', f[1][1:])))
    else:
        raise ValueError('unknown operator:', f[0])

# Helper function for cnf(): distribute disjunction over conjunction.
def cnf_distribute(f1, f2):
    if f1[0] == 'and':
        if len(f1[1]) == 0:
            return f1
        else:
            return ('and', [cnf_distribute(g, f2) for g in f1[1]])
    if f2[0] == 'and':
        if len(f2[1]) == 0:
            return f2
        else:
            return ('and', [cnf_distribute(f1, g) for g in f2[1]])
    else:
        return ('or', [f1, f2])

# Helper function for cnf(): collapse conjunction lists and disjunction lists.
def cnf_flatten(f):
    if f[0] == 'and':
        return ('and', cnf_flatten_conj(f[1]))
    if f[0] == 'or':
        return ('or', cnf_flatten_disj(f[1]))
    else:
        return f

# Helper function for cnf_flatten().
def cnf_flatten_conj(flist):
    if flist == []:
        return flist
    if flist[0][0] == 'and':
        return cnf_flatten_conj(flist[0][1] + flist[1:])
    else:
        return [cnf_flatten(flist[0])] + cnf_flatten_conj(flist[1:])

# Helper function for cnf_flatten().
def cnf_flatten_disj(flist):
    if flist == []:
        return flist
    if flist[0][0] == 'or':
        return cnf_flatten_disj(flist[0][1] + flist[1:])
    else:
        return [flist[0]] + cnf_flatten_disj(flist[1:])

# Helper function for cnf(): remove duplicate disjuncts and conjuncts.
def cnf_remove_dups(f):
    if f[0] == 'and':
        cnj = []
        for g in f[1]:
            g = cnf_remove_dups(g)
            if not g in cnj:
                cnj.append(g)
        return ('and', cnj)
    if f[0] == 'or':
        return ('or', list(set(f[1])))
    else:
        return f

#
# Disjunctive normal form
#

# Convert to disjunctive normal form.
def dnf(f):
    return dnf_remove_dups(dnf_flatten(dnf_do(nnf(f))))

# Helper function for dnf().
def dnf_do(f):
    if atom(f) or f[0] == 'not':
        return f
    if f[0] == 'or':
        return ('or', [dnf_do(g) for g in f[1]])
    if f[0] == 'and':
        if len(f[1]) == 0:
            return f
        if len(f[1]) == 1:
            return dnf_do(f[1][0])
        else:
            return dnf_distribute(dnf_do(f[1][0]), dnf_do(('and', f[1][1:])))
    else:
        raise ValueError('unknown operator:', f[0])

# Helper function for dnf(): distribute conjunction over disjunction.
def dnf_distribute(f1, f2):
    if f1[0] == 'or':
        if len(f1[1]) == 0:
            return f1
        else:
            return ('or', [dnf_distribute(g, f2) for g in f1[1]])
    if f2[0] == 'or':
        if len(f2[1]) == 0:
            return f2
        else:
            return ('or', [dnf_distribute(f1, g) for g in f2[1]])
    else:
        return ('and', [f1, f2])

# Helper function for dnf(): collapse disjunction lists and conjunction lists.
def dnf_flatten(f):
    if f[0] == 'or':
        return ('or', dnf_flatten_disj(f[1]))
    if f[0] == 'and':
        return ('and', dnf_flatten_conj(f[1]))
    else:
        return f

# Helper function for dnf_flatten().
def dnf_flatten_disj(flist):
    if flist == []:
        return flist
    if flist[0][0] == 'or':
        return dnf_flatten_disj(flist[0][1] + flist[1:])
    else:
        return [dnf_flatten(flist[0])] + dnf_flatten_disj(flist[1:])

# Helper function for dnf_flatten().
def dnf_flatten_conj(flist):
    if flist == []:
        return flist
    if flist[0][0] == 'and':
        return dnf_flatten_conj(flist[0][1] + flist[1:])
    else:
        return [flist[0]] + dnf_flatten_conj(flist[1:])

# Helper function for dnf(): remove duplicate conjuncts and disjuncts.
def dnf_remove_dups(f):
    if f[0] == 'or':
        dsj = []
        for g in f[1]:
            g = dnf_remove_dups(g)
            if not g in dsj:
                dsj.append(g)
        return ('or', dsj)
    if f[0] == 'and':
        return ('and', list(set(f[1])))
    else:
        return f

#
# Truth tables
#

# Generates all possible valuations for a given set of atoms.     
def gen_tt(atoms):
    from itertools import product
    return [{p:val for (p, val) in zip(atoms, vals)} for vals in 
         product([False, True], repeat=len(atoms))]

# Returns the set of propositions in f.
def get_atom_names(f):
    if atom(f):
        return {f[0]}
    if f[0] == 'not':
        return get_atom_names(f[1])
    if f[0] == 'arrow':
        return get_atom_names(f[1]) | get_atom_names(f[2])
    if f[0] == 'or' or f[0] == 'and':
        return set().union(*[get_atom_names(g) for g in f[1]]) 
    raise ValueError('unknown operator:', f[0]) 

# Given a set of formulas, pretty prints a truth table showing the
# value of each formula in sigma for each row in tt (if tt == None,
# prints all possible rows WRT the atoms in sigma.
def tt_to_str(tt, *sigma):
    if tt == None: 
        tt = gen_tt(set.union(*[get_atom_names(phi) for phi in sigma]))
    atoms = list(tt[0].keys())
    atoms.sort()
    string = ''.join([p + '     ' for p in atoms])  + '   '
    string += ''.join([fml_to_str(phi) + ',   ' for phi in sigma]) + '\n'
    for row in tt:
        string += ''.join([str(row[p]) + '  ' if row[p] else str(row[p]) + ' ' for p in atoms]) 
        string += '   ' + ''.join([str(evaluate(phi, row)) + ' ' * (len(fml_to_str(phi)) - 1) + ' ' if evaluate(phi, row) else str(evaluate(phi, row)) + ' ' * (len(fml_to_str(phi)) - 1) for phi in sigma])  + '   \n'  
    return string

# Uses the truth table method to compute disjunctive normal form
def dnf_tt(f):
    f_true_tt = [row for row in gen_tt(get_atom_names(f)) 
                 if evaluate(f, row) == True]
    return tuple(['or', [tuple(['and', [p if row[p] else tuple(['not', p]) for p in row.keys() ]]) for row in f_true_tt] ])

# Uses the truth table method to compute conjunctive normal form
def cnf_tt(f):
    f_false_tt = [row for row in gen_tt(get_atom_names(f)) 
                 if evaluate(f, row) == False]
    return tuple(['and', [tuple(['or', [p if not row[p] else tuple(['not', p]) 
                 for p in row.keys() ]]) for row in f_false_tt] ])

# Returns True if f evaluates to False for every possible valuation.
def is_contr(f):
    atoms = get_atom_names(f)
    truth_table = gen_tt(atoms)
    return all(not evaluate(f, val) for val in truth_table)

# Returns True if f evaluates to True for every possible valuation.
def is_valid(f):
    atoms = get_atom_names(f)
    truth_table = gen_tt(atoms)
    return all(evaluate(f, val) for val in truth_table)

# Returns True if f and g have the same truth value for every possible valuation.
def are_equiv(f, g):
    atoms = get_atom_names(f) | get_atom_names(g)    
    truth_table = gen_tt(atoms)
    return  all(evaluate(f, val) == evaluate(g, val) for val in truth_table)

# Returns True if phi is true at every line in the truth table where all
# the formulas in sigma are true.
def proves(sigma, phi):
    atoms = set.union(*[get_atom_names(psi) for psi in sigma]) | get_atom_names(phi)
    all_sigma_tt = [row for row in gen_tt(atoms) if 
        all(evaluate(psi, row) for psi in sigma)]
    return all(evaluate(phi, row) for row in all_sigma_tt)

# Returns the strongest implication of a set of premices; that is, the thing
# that is true only at the rows in the truth table where all the premices are 
# true.
def strngst_impcl(sigma):
    atoms = set.union(*[get_atom_names(f) for f in sigma])
    rows = [t for t in gen_tt(atoms) if 
            all(evaluate(f, t) for f in sigma)]
    phi = tuple(['or', [ tuple(['and', [p if row[p] == True else ('not', p) 
                for p in row] ]) for row in rows ] ])
    return phi

#
# Resolution
#

def cnf_to_clauses(f):
    if literal(f):
        return [[f]]
    if f[0] == 'or':
        return [f[1]]
    if f[0] == 'and':
        return [[g] if literal(g) else g[1] for g in f[1]]

def resolve_cnf(f):
    return resolve_do(resolve_clean_clauses(cnf_to_clauses(cnf(('not', f)))))


def resolve_cnf_do(clauses):
    from itertools import combinations

    if [] in clauses:
        return True

    for c1, c2 in combinations(clauses, 2):
        new = resolve_clean_clause(resolve_rule(c1, c2))
        if new == None or new in clauses:
            continue
        else:
            clauses.append(new)
            return resolve_cnf_do(clauses)

    return False

def resolve_clean_clause(clause):

    if not clause:
        return clause

    clean = []
    for f in clause:
        if not f in clean:
            clean.append(f)

    for f in clean:
        if ('not', f) in clean:
            return None
    return clean

def resolve_clean_clauses(clauses):
    clean_clauses = []
    for clause in clauses:
        clean = resolve_clean_clause(clause)
        if clean:
            clean_clauses.append(clean)
    return clean_clauses

    

def resolve_rule(c1, c2):
    for f in c1:
        if f[0] == 'not':
            f_not = f[1]
        else:
            f_not = ('not', f)
        if f_not in c2:
            c1_new = [g for g in c1 if not g == f]
            c2_new = [g for g in c2 if not g == f_not] 
            return c1_new + c2_new

def resolve(f):
    return resolve_do([[('not', f)]])

def resolve_do(clauses):
    from itertools import combinations

    if [] in clauses:
        print('Tautology')
        return True

    for c1, c2 in combinations(clauses, 2):
        new = resolve_clean_clause(resolve_rule(c1, c2))
        if new == None or new in clauses:
            continue
        else:
            clauses.append(new)
            return resolve_do(clauses)

    for clause in clauses:
        print(clause)
    print()
    for clause in clauses:

        # Handle double negations and beta formulas.
        for f in clause:

            betas  = None
            alphas = None
            if f[0] == 'or':
                betas =  f[1]
            if f[0] == 'arrow':
                betas =  [('not', f[1]), f[2]]
            if f[0] == 'and':
                alphas = f[1]
            if f[0] == 'not': 
                if f[1][0] == 'not':
                    betas =  [f[1][1]]
                if f[1][0] == 'and':
                    betas =  [('not', g) for g in f[1][1]]
                if f[1][0] == 'or':
                    alphas = [('not', g) for g in f[1][1]]
                if f[1][0] == 'arrow':
                    alphas = [f[1][1], ('not', f[1][2])]
            
            # Handle double negations and beta formulas.
            if betas: 
                clauses.remove(clause)
                clause.remove(f)
                clauses.append(clause + betas)
                clauses = resolve_clean_clauses(clauses)
                return resolve_do(clauses)
        
            # Handle alpha formulas
            if alphas: 
                clauses.remove(clause)
                clause.remove(f)
                for g in alphas:
                    clauses.append(clause + [g])
                clauses = resolve_clean_clauses(clauses)
                return resolve_do(clauses)

    print('Not Tautology')
    return False

    

#
# Tableaux
#

def tableau(f):
    return tableau_do([('not', f)])

# Helper function for tableau().
def tableau_do(branch):
    if tableau_closed(branch):
        return True

    # Handle double negations and alpha formulas.
    for f in branch:
        if f[0] == 'not' and f[1][0] == 'not':
            return tableau_do([g for g in branch if g != f] + [f[1][1]])
        if f[0] == 'and':
            return tableau_do([g for g in branch if g != f] + f[1])
        if (f[0] == 'not' and f[1][0] == 'or'):
            return tableau_do([g for g in branch if g != f] +
                [('not', g) for g in f[1][1]])
        if (f[0] == 'not' and f[1][0] == 'arrow'):
            return tableau_do([g for g in branch if g != f] +
                [f[1][1], ('not', f[1][2])])

    # Handle beta formulas.
    for f in branch:
        if f[0] == 'or':
            return all(tableau_do([h for h in branch if h != f] + [g])
                for g in f[1])
        if f[0] == 'not' and f[1][0] == 'and':
            return all(tableau_do([h for h in branch if h != f] + [('not', g)])
                for g in f[1][1])
        if f[0] == 'arrow':
            return (tableau_do([g for g in branch if g != f] + [('not', f[1])])
                and tableau_do([g for g in branch if g != f] + [f[2]]))

    return False

# Helper function for tableau(): check if a branch is closed (that is, check
# whether a list of formulas contains both F and ~F for any formula F).
def tableau_closed(branch):
    negations = [f for f in branch if f[0] == 'not']
    for f in negations:
        if f[1] in branch:
            return True
    return False

# Alternative tableaux implementation using dnf().
#
# First transform the negation of the formula to be proved into DNF. Since a
# DNF formula is a disjunction of conjunctions, this gives us a finished
# tableau tree. Now simply check if each conjunction is a closed branch (i.e.
# it contains both an atom and its negation). If so, this means the whole
# tableau is closed and the original formula is proved.
def tableau_dnf(f):
    return tableau_dnf_do(dnf(('not', f)))

# Helper function for tableau_dnf().
def tableau_dnf_do(f):
    if literal(f):
        return False
    if f[0] == 'and':
        return any(atom(g) and ('not', g) in f[1] for g in f[1])
    else:
        return all(tableau_dnf_do(g) for g in f[1])
