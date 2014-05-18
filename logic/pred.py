import util


#
# Utilitiy Functions
#

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

# Return a set of free variables from a formula (assuming bound
# vars are initially considered bound).
def get_free_vars(f, bound_vars):
    if pred(f):
        free_vars = set()
        for term in f[1]:
            free_vars = free_vars.union(get_free_vars_in_term(f[1],
                bound_vars))
        return free_vars
    if f[0] == 'not':
        return get_free_vars(f[1], bound_vars)
    if f[0] == 'and' or f[0] == 'or':
        free_vars = set()
        for g in f[1]:
            free_vars = free_vars.union(get_free_vars(g, bound_vars))
        return free_vars
    if f[0] == 'all' or f[0] == 'exists':
        return get_free_vars(f[2], bound_vars.union(f[1]))
    else:
        return set()

# Herper functtion for get_free_vars
def get_free_vars_in_term(termlist, bound_vars):
    free_vars = set()
    for t in termlist:
        if variable(t):
            if t not in bound_vars:
                free_vars.add(t)
        if function(t):
            free_vars = free_vars.union(get_free_vars_in_term(t[1],
                bound_vars))
    return free_vars

# Return the set of all variables occurring in a term.
def variables_in_term(term):
    if variable(term):
        return {term}
    else:
        var = set()
        for t in term[1]:
            var |= variables_in_term(t)
        return var

# Helper function for skolemize(): return a list of all function symbols used
# in the formula f.
def get_funcs(f):
    if pred(f):
        return [a[0] for a in f[1] if function(a)]
    if f[0] == 'not':
        return get_funcs(f[1])
    if f[0] == 'and' or f[0] == 'or':
        l = []
        for g in f[1]:
            l.append(get_funcs(g))
        return l
    if f[0] == 'arrow':
        return get_funcs(f[1]) + get_funcs(f[2])
    if f[0] == 'all' or f[0] == 'exists':
        return get_funcs(f[2])
    raise ValueError('unknown operator: %s' % f[0])


#
# Printing
#

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
        s += term_to_str(x)
        s += ', '
    s = s[:-2]
    s += ')'
    return s

# Convert a term to a string.
def term_to_str(term):
    if variable(term):
        return term
    else:
        if len(term[1]) == 0:
            return term[0]
        else:
            return term[0] + args_to_str(term[1])

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


#
# Substitution
#

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

# Return the composition of two substitutions. That is, return the substitution
# equivalent to the application of s1 after s2.
def compose_subst(s1, s2):
    return s1 + [(s[0], subst_term(s1, s[1])) for s in s2]

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
    free_vars = get_free_vars(f, exists_vars)
    used_funcs = get_funcs(f)

    g = f
    for v in exists_vars:
        while 'f' + str(func_counter) in used_funcs:
            func_counter += 1
        skolem_func = 'f' + str(func_counter)
        used_funcs.append(skolem_func)
        g = skolemize_replace(g, v, (skolem_func, list(free_vars)))
    return (g, func_counter + 1)

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
