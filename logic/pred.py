import util

def pred(f):
    return f[0] in 'PQRS'

# A constant is just a 0-ary function
def constant(x):
    return function(x) and len(x[1]) == 0 

# Variables always start a letter from the end of the alphabet.
def variable(x):
    return isinstance(x, str) and x[0] in 'xyz'

# Functions (and constants) always start with a letter from the 
# beginning of the alphabet
def function(x):
    return isinstance(x, tuple) and x[0][0] in 'abcdfghj'

# Convert a formula to a string.
def fml_to_str(f):
    if pred(f):
        s = f[0] + args_to_str(f[1])
    elif f[0] == 'not':
        s = '~' + subfml_to_str(f[1])
    elif f[0] == 'and' or f[0] == 'or':
        s = ''
        for i in range(len(f[1])):
            s += subfml_to_str(f[1][i])
            if i != len(f[1]) - 1:
                s += ' & ' if f[0] == 'and' else ' V '
    elif f[0] == 'arrow':
        s = subfml_to_str(f[1]) + ' -> ' + subfml_to_str(f[2])
    elif f[0] == 'all' or f[0] == 'exists':
        s = 'A' if f[0] == 'all' else 'E'
        for t in f[1]:
            s += t
        s += subfml_to_str(f[2])
    else:
        raise ValueError('unknown operator: %s' % f[0])

    return s

# Helper function for fml_to_str(): enclose a subformula in parentheses if
# necessary.
def subfml_to_str(f):
    if (f[0] == 'and' or f[0] == 'or') and len(f[1]) != 1:
        return '(' + fml_to_str(f) + ')'
    if f[0] == 'arrow':
        return '(' + fml_to_str(f) + ')'
    return fml_to_str(f)

# Helper function for fml_to_str(): convert a list of predicate or function
# arguments to a string.
def args_to_str(a):
    s = '('
    for x in a:
        if function(x):
            s += x[0]
            if not constant(x):
                s += args_to_str(x[1]) 
        else: 
            s += str(x)
        s += ', '
    s = s[:-2]
    s += ')'
    return s

# Returns a dictionary from predicates to their arities
def get_preds(f):
    preds = {} 
    if pred(f):
        if f[0] in preds: 
            raise ValueError('Conflicting arities for predicate: %s' % f[0])
        preds[f[0]] = len(f[1])
    if f[0] == 'not':
        preds.update(get_preds(f[1]))
    if f[0] == 'and' or f[0] == 'or':
        for g in f[1]: preds.update(get_preds(g))
    if f[0] == 'arrow':
        preds.update(get_preds(f[1]))
        preds.update(get_preds(f[2]))
    if f[0] == 'all' or f[0] == 'exists' :
        preds.update(get_preds(f[2]))
    return preds

# Return a set of constants.
def get_constants(f):
    if pred(f):
        consts = set()
        for a in f[1]:
            if constant(a):
                consts.add(a)
        return consts
    if f[0] == 'not':
        return get_constants(f[1])
    if f[0] == 'and' or f[0] == 'or':
        consts = set()
        for g in f[1]:
            consts |= (get_constants(g))
        return consts
    if f[0] == 'arrow':
        return get_constants(f[1]) | (get_constants(f[2]))
    if f[0] == 'all' or f[0] == 'exists':
        return get_constants(f[2])

# Return a set of variables.
def get_variables(f):
    if pred(f):
        variables = set()
        for a in f[1]:
            if variable(a):
                variables.add(a)
            if function(a):
                for b in a[1]:
                    variables.add(b)
        return variables
    if f[0] == 'not':
        return get_variables(f[1])
    if f[0] == 'and' or f[0] == 'or':
        variables = set()
        for g in f[1]:
            variables |= (get_variables(g))
        return variables
    if f[0] == 'arrow':
        return get_variables(f[1]) | (get_variables(f[2]))
    if f[0] == 'all' or f[0] == 'exists':
        return get_variables(f[2])

# Return a dictionary from functions to their arities.
def get_functions(f):
    if pred(f):
        funcs = {}
        for a in f[1]:
            if function(a):
                funcs[a[0]] = len(a[1])
        return funcs
    if f[0] == 'not':
        return get_functions(f[1])
    if f[0] == 'and' or f[0] == 'or':
        funcs = {}
        for g in f[1]:
            funcs.update(get_functions(g))
        return funcs
    if f[0] == 'arrow':
        funcs = get_functions(f[1])
        funcs.update(get_functions(f[2]))
        return funcs
    if f[0] == 'all' or f[0] == 'exists':
        return get_functions(f[2])

# Standardise variables; i.e. each variable is bound at most once. If
# necessary, variables are renamed to an indexed x variable (e.g. "x0").
def safe(f):
    return safe_do(f, [])

# Helper function for safe(). The boundvars argument is a list of variables
# already bound.
def safe_do(f, boundvars):
    if pred(f):
        return f
    if f[0] == 'not':
        return ('not', safe_do(f[1], boundvars))
    if f[0] == 'and' or f[0] == 'or':
        return (f[0], [safe_do(g, boundvars) for g in f[1]])
    if f[0] == 'arrow':
        return ('arrow', safe_do(f[1], boundvars), safe_do(f[2], boundvars))
    if f[0] == 'all' or f[0] == 'exists':
        g = safe_do(f[2], boundvars)
        quantvars = set()
        for v in f[1]:
            if v in boundvars:
                i = 0
                while 'x' + str(i) in boundvars:
                    i += 1
                w = 'x' + str(i)
                g = safe_replace(g, v, w)
            else:
                w = v
            quantvars.add(w)
            boundvars.append(w)
        return (f[0], quantvars, g)
    raise ValueError('unknown operator: %s' % f[0])

# Helper function for safe(): replace every occurrence of the variable v with
# w.
def safe_replace(f, v, w):
    if pred(f):
        return (f[0], [replace_terms(t, v, w) if t != v else w for t in f[1]])
    if f[0] == 'not':
        return ('not', safe_replace(f[1], v, w))
    if f[0] == 'and' or f[0] == 'or':
        return (f[0], [safe_replace(g, v, w) for g in f[1]])
    if f[0] == 'arrow':
        return ('arrow', safe_replace(f[1], v, w), safe_replace(f[2], v, w))
    if f[0] == 'all' or f[0] == 'exists':
        return f
    raise ValueError('unknown operator: %s' % f[0])

def replace_terms(t, v, w):
    if variable(t):
        if t == v:
            return w 
        else:
            return t
    elif function(t):
        return (t[0], [replace_terms(s, v, w) for s in t[1]])
    raise ValueError('expected a term, but got', t)

# Skolemize a formule; i.e. replace each existentially quantified variable with
# a Skolem function.
def skolemize(f):
    return skolemize_do(safe(f), skolemize_get_funcs(f), [])

# Helper function for skolemize().
# - The funcs argument is a list of function symbols occurring in the formula.
# - The univars argument is a list of universally quantified variables that
#   need to be arguments for the Skolem function.
def skolemize_do(f, funcs, univars):
    if pred(f):
        return f
    if f[0] == 'not':
        return ('not', skolemize_do(f[1], funcs, univars))
    if f[0] == 'and' or f[0] == 'or':
        return (f[0], [skolemize_do(g, funcs, univars) for g in f[1]])
    if f[0] == 'arrow':
        return ('arrow', skolemize_do(f[1], funcs, univars),
            skolemize_do(f[2], funcs, univars))
    if f[0] == 'all':
        univars += list(f[1])
        return (f[0], f[1], skolemize_do(f[2], funcs, univars))
    if f[0] == 'exists':
        g = f[2]
        for v in f[1]:
            i = 0
            while 'f' + str(i) in funcs:
                i += 1
            func = 'f' + str(i)
            g = skolemize_replace(g, v, (func, univars))
            funcs.append(func)
        return skolemize_do(g, funcs, univars)
    raise ValueError('unknown operator: %s' % f[0])

# Helper function for skolemize(): return a list of all function symbols used
# in the formula f.
def skolemize_get_funcs(f):
    if pred(f):
        return [a[0] for a in f[1] if function(a)]
    if f[0] == 'not':
        return skolemize_get_funcs(f[1])
    if f[0] == 'and' or f[0] == 'or':
        l = []
        for g in f[1]:
            l.append(skolemize_get_funcs(g))
        return l
    if f[0] == 'arrow':
        return skolemize_get_funcs(f[1]) + skolemize_get_funcs(f[2])
    if f[0] == 'all' or f[0] == 'exists':
        return skolemize_get_funcs(f[2])
    raise ValueError('unknown operator: %s' % f[0])

# Helper function for handling gamma formulas
def parametrize(f, v, parm):
    return skolemize_replace(f, v, parm)

# Helper function for skolemize():
def skolemize_replace(f, v, func):
    if pred(f):
        return (f[0], [replace_terms(t, v, func) if t != v else func for t in f[1]])
    if f[0] == 'not':
        return ('not', skolemize_replace(f[1], v, func))
    if f[0] == 'and' or f[0] == 'or':
        return (f[0], [skolemize_replace(g, v, func) for g in f[1]])
    if f[0] == 'arrow':
        return ('arrow', skolemize_replace(f[1], v, func),
            skolemize_replace(f[2], v, func))
    if f[0] == 'all' or f[0] == 'exists':
        return (f[0], f[1], skolemize_replace(f[2], v, func))
    raise ValueError('unknown operator: %s' % f[0])

#
# Unification
#


# - A list of terms simply is the list of arguments of a predicate or a
#   function.
# - A substitution is a list of pairs. For each pair, the first element is a
#   variable and the second element a term.

# Return a substitution that unifies two lists of terms. Return None if no such
# substitution exists.
def unify_termlists(t1, t2):
    if len(t1) == len(t2) == 0:
        return []
    if len(t1) != len(t2):
        return None
    else:
        subst = []
        for (u1, u2) in zip(t1, t2):
            v1 = subst_term(subst, u1)
            v2 = subst_term(subst, u2)
            newsubst = unify_terms(v1, v2)
            if newsubst == None:
                return None
            subst = compose_subst(newsubst, subst)
        return subst

# Return a substitution that unifies two terms. Return None if no such
# substitution exists.
def unify_terms(t1, t2):
    if variable(t1) and variable(t2):
        if t1 == t2:
            return []
        else:
            return [(t1, t2)]
    if variable(t1) and not variable(t2):
        if t1 in variables_in_term(t2):
            return None
        else:
            return [(t1, t2)]
    if not variable(t1) and variable(t2):
        if t2 in variables_in_term(t1):
            return None
        else:
            return [(t2, t1)]
    else:
        if t1[0] != t2[0]:
            return None
        else:
            return unify_termlists(t1[1], t2[1])

# Return the composition of two substitutions. That is, return the substitution
# equivalent to the application of s1 after s2.
def compose_subst(s1, s2):
    return s1 + [(s[0], subst_term(s1, s[1])) for s in s2]

# Return the set of all variables occurring in a term.
def variables_in_term(term):
    if variable(term):
        return {term}
    else:
        var = set()
        for t in term[1]:
            var |= variables_in_term(t)
        return var

# Apply a substitution to a list of terms.
def subst_termlist(subst, termlist):
    return [subst_term(subst, t) for t in termlist]

# Apply a substitution to a term.
def subst_term(subst, term):
    if variable(term):
        return subst_var(subst, term)
    else:
        return (term[0], subst_termlist(subst, term[1]))

# Apply a substitution to a variable.
def subst_var(subst, var):
    if subst == []:
        return var
    if var == subst[0][0]:
        return subst[0][1]
    else:
        return subst_var(subst[1:], var)

# Convert a substitution to a string.
def subst_to_str(subst):
    if subst == None:
        return '{}'
    string = '{'
    for s in subst:
        string += s[0] + ' -> ' + term_to_str(s[1]) + ', '
    if len(string) > 1:
        string = string[:-2]
    string += '}'
    return string

# Convert a list of terms to a string.
def termlist_to_str(termlist):
    s = ''
    for t in termlist:
        s += term_to_str(t) + ', '
    s = s[:-2]
    return s

# Convert a term to a string.
def term_to_str(term):
    if variable(term):
        return term
    else:
        if len(term[1]) == 0:
            return term[0]
        else:
            s = term[0] + '('
            for t in term[1]:
                s += term_to_str(t) + ', '
            s = s[:-2] + ')'
            return s

# Convert each implicative subformula to a disjunctive one.
def impl_to_disj(f):
    if pred(f):
        return f
    if f[0] == 'not':
        return ('not', impl_to_disj(f[1]))
    if f[0] == 'or' or f[0] == 'and':
        return (f[0], [impl_to_disj(g) for g in f[1]])
    if f[0] == 'arrow':
        return ('or', [('not', impl_to_disj(f[1])), impl_to_disj(f[2])])
    if f[0] == 'all' or f[0] == 'exists':
        return (f[0], f[1], impl_to_disj(f[2]))
    raise ValueError('unknown operator:', f[0])

# Convert to negation normal form.
def nnf(f):
    return nnf_do(impl_to_disj(f))

# Helper function for nnf().
def nnf_do(f):
    if pred(f):
        return f
    elif f[0] == 'not':
        if pred(f[1]):
            return f
        elif f[1][0] == 'not':
            return nnf_do(f[1][1])
        elif f[1][0] == 'and':
            return ('or', [nnf_do(('not', g)) for g in f[1][1]])
        elif f[1][0] == 'or':
            return ('and', [nnf_do(('not', g)) for g in f[1][1]])
        elif f[1][0] == 'all':
            return ('exists', f[1][1], nnf_do(('not', f[1][2])))
        elif f[1][0] == 'exists':
            return ('all', f[1][1], nnf_do(('not', f[1][2])))
        else:
            raise ValueError('unknown operator:', f[1][0])
    elif f[0] == 'and' or f[0] == 'or':
        return (f[0], [nnf_do(g) for g in f[1]])
    elif f[0] == 'all' or f[0] == 'exists':
        return (f[0], f[1], nnf_do(f[2]))
    raise ValueError('unexpected operator:', f[0])

# Remove all universal quantifiers.
def remove_universals(f):
    if pred(f):
        return f
    if f[0] == 'not':
        return ('not', remove_universals(f[1]))
    if f[0] == 'and' or f[0] == 'or':
        return (f[0], [remove_universals(g) for g in f[1]])
    if f[0] == 'all':
        return remove_universals(f[2])

# Convert to conjunctive normal form.
def cnf(f):
    return cnf_remove_dups(cnf_flatten(cnf_do(remove_universals(skolemize(
        nnf(f))))))

# Helper function for cnf().
def cnf_do(f):
    if pred(f) or f[0] == 'not':
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
        dsj = []
        for g in f[1]:
            if not g in dsj:
                dsj.append(g)
        return ('or', dsj)
    else:
        return f

#
# Tableaux
#

def tableau(f, gdepth):
    branches = tableau_expand([('not', f)], gdepth)
    return tableau_closed(branches)

def tableau_expand(branch, qdepth):
    return tableau_expand_do([branch], qdepth, 0, 0)

def tableau_expand_do(branches, gdepth, skolem_func_counter, uni_var_counter):
    util.dprint('\ntableau_expand_do:')
    for branch in branches:
        util.dprint('branch:')
        for fml in branch:
            util.dprint('  ', fml_to_str(fml))
    util.dprint()

    for branch in branches[:]:
        # Handle alpha formulas.
        for f in branch:
            fml_type, subs = tableau_fml_type(f)    

            if fml_type == 'alpha':
                util.dprint('alpha rule on', fml_to_str(f))
                branches.remove(branch)
                branch.remove(f)
                branches.append(branch + subs)
                return tableau_expand_do(branches, gdepth, skolem_func_counter, uni_var_counter)

        # Handle beta formulas.
        for f in branch:
            fml_type, subs = tableau_fml_type(f)    

            if fml_type == 'beta':
                util.dprint('beta rule on', fml_to_str(f))
                branches.remove(branch)
                branch.remove(f)
                for g in subs:
                    branches.append(branch + [g])
                return tableau_expand_do(branches, gdepth, skolem_func_counter, uni_var_counter)

        # Handle delta formulas (before gamma formulas).
        for f in branch:
            fml_type, subs = tableau_fml_type(f)    

            if fml_type == 'delta':
                util.dprint('delta rule on', fml_to_str(f))
                branches.remove(branch)
                branch.remove(f)
                g, skolem_func_counter = tableau_skolemize(subs[1], subs[0],
                    skolem_func_counter)
                branch.append(g)
                branches.append(branch)
                return tableau_expand_do(branches, gdepth, skolem_func_counter, uni_var_counter)

        # Handle gamma formulas.
        for f in branch:
            fml_type, subs = tableau_fml_type(f)

            if fml_type == 'gamma':
                util.dprint('gamma rule on', fml_to_str(f))
                branches.remove(branch)
                branch.remove(f)
                new_f = subs[1]
                for var in subs[0]:
                    parameter =  'x' + str(uni_var_counter)
                    uni_var_counter += 1
                    new_f = parametrize(new_f, var, parameter)
                branch.append(new_f)
                branches.append(branch)
                return tableau_expand_do(branches, gdepth, skolem_func_counter, uni_var_counter)

    return branches

# Returns a tuple the first element of which is the type
# If 'alpha' or 'beta', the second element is a list
# of subformulas.
# If 'gamma' or 'delta', the second element is a tuple
# contaning the quantified variables and the subformula.
def tableau_fml_type(f):

    if f[0] == 'not' and f[1][0] == 'not':
        return ('alpha', [f[1][1]])
    if f[0] == 'and':
        return ('alpha', f[1])
    if f[0] == 'not' and f[1][0] == 'or':
        return ('alpha', [('not', g) for g in f[1][1]])
    if f[0] == 'not' and f[1][0] == 'arrow':
        return ('alpha', [f[1][1], ('not', f[1][2])])
    
    if f[0] == 'or':
        return ('beta', f[1])
    if f[0] == 'not' and f[1][0] == 'and':
        return ('beta', [('not', g) for g in f[1][1]])
    if f[0] == 'arrow':
        return ('beta', [('not', f[1]), f[2]])

    if f[0] == 'exists':
        return ('delta', (f[1], f[2]))
    if f[0] == 'not' and f[1][0] == 'all':
        return ('delta', (f[1][1], ('not', f[1][2])))

    if f[0] == 'all':
        return ('gamma', (f[1], f[2]))
    if f[0] == 'not' and f[1][0] == 'exists':
        return ('gamma', (f[1][1], ('not', f[1][2])))

    else:
        return ('literal', f)

def tableau_skolemize(f, exists_vars, func_counter):
    free_vars = tableau_get_free_vars(f, exists_vars)
    used_funcs = skolemize_get_funcs(f)

    g = f
    for v in exists_vars:
        while 'f' + str(func_counter) in used_funcs:
            func_counter += 1
        skolem_func = 'f' + str(func_counter)
        used_funcs.append(skolem_func)
        g = skolemize_replace(g, v, (skolem_func, list(free_vars)))
    return (g, func_counter + 1)

def tableau_get_free_vars(f, bound_vars):
    if pred(f):
        free_vars = set()
        for term in f[1]:
            free_vars = free_vars.union(tableau_get_free_vars_in_term(f[1],
                bound_vars))
        return free_vars
    if f[0] == 'not':
        return tableau_get_free_vars(f[1], bound_vars)
    if f[0] == 'and' or f[0] == 'or':
        free_vars = set()
        for g in f[1]:
            free_vars = free_vars.union(tableau_get_free_vars(g, bound_vars))
        return free_vars
    if f[0] == 'all' or f[0] == 'exists':
        return tableau_get_free_vars(f[2], bound_vars.union(f[1]))
    else:
        return set()

def tableau_get_free_vars_in_term(termlist, bound_vars):
    free_vars = set()
    for t in termlist:
        if variable(t):
            if t not in bound_vars:
                free_vars.add(t)
        if function(t):
            free_vars = free_vars.union(tableau_get_free_vars_in_term(t[1],
                bound_vars))
    return free_vars

def tableau_closed(branches):
    util.dprint('tableau_closed:')
    for b in branches:
        util.dprint('branch:')
        for f in b:
            util.dprint('  ', fml_to_str(f))
    util.dprint()
    substs = []
    for branch in branches:
        util.dprint('substs so far:', subst_to_str(substs))
        newsubsts = tableau_branch_closed(branch, substs)
        util.dprint('new substitutions:', subst_to_str(newsubsts))
        if newsubsts == None:
            return False
        substs += newsubsts
    util.dprint('tableau closed with', subst_to_str(substs))
    return True

def tableau_branch_closed(branch, substs):
    positives = [f for f in branch if pred(f)]
    negatives = [f for f in branch if f[0] == 'not']

    for f in positives:
        for g in negatives:
            if f[0] == g[1][0]:
                f_terms = subst_termlist(substs, f[1])
                g_terms = subst_termlist(substs, g[1][1])
                newsubsts = unify_termlists(f_terms, g_terms)
                if newsubsts != None:
                    return newsubsts
    return None
