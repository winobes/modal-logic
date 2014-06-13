import util

#
# Utilitiy Functions
#

# A predicate is a string starting with P,Q,R or S.
def pred(f):
    return f[0][0] in 'PQRS'

# A constant is just a 0-ary function
def constant(x):
    return function(x) and len(x[1]) == 0 

# Variables always start a letter from the end of the alphabet.
def variable(x):
    return isinstance(x, str) and x[0][0] in 'wxyz'

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

# Helper function for skolemize(): return a list of all function symbols used
# in the formula f.
def get_funcs(f):
    if pred(f):
        return flatten([get_funcs_in_term(t) for t in f[1]])
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

# Helper function for get_funcs
def get_funcs_in_term(t):
    if variable(t):
        return []
    if function(t):
        return [t[0]] + flatten([get_funcs_in_term(s) for s in t[1]])
    pass

# Turns a list of lists of things into a list of things
def flatten(l):
    return [item for sublist in l for item in sublist]

#
# Parsing & Printing
#

def parse(s):
    return rpn_to_fmls(parse_to_rpn(s), 1)[0]

def rpn_to_fmls(rpn, n):

    op = rpn.pop()

    if op[0] in {'all', 'exist'}:
        subs = rpn_to_fmls(rpn, 1)
        return [(op[0], op[1], subs[0])]
    elif pred(op):
        if n == 1:
            return [op]
        else:
            return [op] + rpn_to_fmls(rpn, n-1)
    elif op in {'arrow'}:
        subs = rpn_to_fmls(rpn, 2)
        return [(op, subs[1], subs[0])]
    elif op in {'and', 'or'}:
        subs = rpn_to_fmls(rpn, 2)
        return [(op, subs)]
    elif op == 'not':
        subs = rpn_to_fmls(rpn, 1)
        return [(op, subs[0])]
    else:
        raise ValueError("unrecognized expression", op)

# Convert a string to a formula
def parse_to_rpn(s):

    ops = {'->', '~', '&'}
    quants = {'A', 'E'}
    stack = []
    output = []
    name = ""
    quant = False

    while s:
        c = s[0]
        s = s[1:]

        if not name:
            if c == '(':
                stack.append('(')
            elif c == ')':
                while True:
                    pop = stack.pop()
                    if pop == '(':
                        break
                    else:
                        output.append(pop)
            elif c in ops:
                stack.append(op_to_name(c))
            elif c in quants:
                if quant:
                    stack.append(name)
                quant = True
                name = c
            else:
                name += c
        elif name:
            if c ==  '(':
                if quant:
                    quant = False
                    stack.append(parse_quant(name))
                    stack.append('(')
                    name = ""
                else:
                    out, s = parse_args(s)
                    output.append((name, out))
                    name = ""
            else: 
                name += c 
                if name in ops:
                    stack.append(op_to_name(name))
                    name = ""

    return output + stack

def op_to_name(s):
    d = {'A':  'all',
         'E':  'exist',
         '->': 'arrow',
         '&':  'and',
         '|':  'or',
         '~':  'not'
         }
    if not s in d:
        raise ValueError('unknown operator ', s)
    else:
        return d[s]

def parse_quant(s):
    return (op_to_name(s[0]), parse_quant_vars(s[1:]))

def parse_quant_vars(s):

    vs = set() 
    v = ''

    for c in s: 
        if c in {'x', 'y', 'z'}: 
            if v:
                vs.add(v)
            v = c
        else:
            v += c
    vs.add(v)

    return vs

def parse_args(s):
    stack = []
    term = None #string if varriable, tuple if function or constant
    output = []
    while s:
        c = s[0]
        s = s[1:]
        if c == ',' or c == ')' and not stack:
            if type(term) == str and not term[0] in {'x','y','z'}:
                term = (term, [])
            output.append(term)
            term = ""
            if c == ')':
                return (output, s)
        elif not term:
            term = c
        elif term:
            if c == '(':
                out, s = parse_args(s)
                term = (term, out)
            else:
                term += c
    return output
        

# Convert a formula to a string.
def fml_to_str(f):
    if pred(f):
        s = f[0] + '(' + termlist_to_str(f[1]) + ')'
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
            return term[0] + '(' + termlist_to_str(term[1]) + ')'

# Convert a substitution to a string.
def subst_to_str(subst):
    string = '{'
    if subst != None:
        for v in subst:
            string += v + ' -> ' + term_to_str(subst[v]) + ', '
        if len(string) > 1:
            string = string[:-2]
    string += '}'
    return string


#
# Substitution
#

# Return the composition of two substitutions. That is, return the substitution
# equivalent to the application of s1 after s2.
def compose_subst(s1, s2):
    comp = {}
    comp.update(s1)
    comp.update({t:subst_term(s1, s2[t]) for t in s2})
    return comp 

# Helper function for skolemize():
def subst_formula(subst, f):
    if pred(f):
        return (f[0], subst_termlist(subst, f[1]))
    if f[0] == 'not':
        return ('not', subst_formula(subst, f[1]))
    if f[0] == 'and' or f[0] == 'or':
        return (f[0], [subst_formula(subst, g) for g in f[1]])
    if f[0] == 'arrow':
        return ('arrow', subst_formula(subst, f[1]),
            subst_formula(subst, f[2]))
    if f[0] == 'all' or f[0] == 'exists':
        return (f[0], f[1], 
            subst_formula({v:subst[v] for v in subst if not v in f[1]}, f[2]))
    raise ValueError('unknown operator: %s' % f[0])

# Apply a substitution to a list of terms.
def subst_termlist(subst, termlist):
    return [subst_term(subst, t) for t in termlist]

# Apply a substitution to a term.
def subst_term(subst, term):
    if variable(term):
        return subst_term(subst, subst[term]) if term in subst else term
    else:
        return (term[0], subst_termlist(subst, term[1]))

#
# Unification
#


# - A list of terms simply is the list of arguments of a predicate or a
#   function.
# - A substitution is a dictionary mapping from variables to terms

# Return a substitution that unifies two lists of terms. Return None if no such
# substitution exists.
def unify_termlists(t1, t2):
    if len(t1) == len(t2) == 0:
        return {}
    if len(t1) != len(t2):
        return None
    else:
        subst = {}
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
            return {}
        else:
            return {t1:t2}
    if variable(t1) and not variable(t2):
        if t1 in variables_in_term(t2):
            return None
        else:
            return {t1:t2}
    if not variable(t1) and variable(t2):
        if t2 in variables_in_term(t1):
            return None
        else:
            return {t2:t1}
    else:
        if t1[0] != t2[0]:
            return None
        else:
            return unify_termlists(t1[1], t2[1])

# Return the set of all variables occurring in a term.
def variables_in_term(term):
    if variable(term):
        return {term}
    else:
        var = set()
        for t in term[1]:
            var |= variables_in_term(t)
        return var

#
# Tableaux
#

def tableau(f, gdepth):
    branches = tableau_expand(f, gdepth)
    return tableau_closed(branches)

def tableau_expand(f, qdepth):
    branch = [tableau_canonize(('not', f))]
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

            if f[0] == 'and':
                util.dprint('alpha rule on', fml_to_str(f))
                branch.remove(f)
                subs = [tableau_canonize(g) for g in f[1]]
                branch += subs
                return tableau_expand_do(branches, gdepth, skolem_func_counter, uni_var_counter)

        # Handle beta formulas.
        for f in branch:

            if f[0] == 'or':
                util.dprint('beta rule on', fml_to_str(f))
                branches.remove(branch)
                branch.remove(f)
                subs = [tableau_canonize(g) for g in f[1]]
                for g in subs:
                    branches.append(branch + [g])
                return tableau_expand_do(branches, gdepth, skolem_func_counter, uni_var_counter)

        # Handle delta formulas (before gamma formulas).
        for f in branch:

            if f[0] == 'exists':
                util.dprint('delta rule on', fml_to_str(f))
                branch.remove(f)
                g, skolem_func_counter = tableau_skolemize(f[2], f[1],
                    skolem_func_counter)
                branch.append(tableau_canonize(g))
                return tableau_expand_do(branches, gdepth, skolem_func_counter, uni_var_counter)

        # Handle gamma formulas.
        for f in branch:

            if f[0] == 'all':
                util.dprint('gamma rule on', fml_to_str(f))
                branch.remove(f)
                if gdepth > 0:
                    branch.append(f)
                    gdepth -= 1
                new_f = f[2]
                for var in f[1]:
                    parameter =  'x' + str(uni_var_counter)
                    uni_var_counter += 1
                    new_f = subst_formula({var:parameter}, new_f)
                branch.append(tableau_canonize(new_f))
                return tableau_expand_do(branches, gdepth, skolem_func_counter, uni_var_counter)

    return branches

# Rewrites formulas in canonical form:
# Alpha formulas have 'and'    as the main operator.
# Beta  formulas have 'or'     as the main operator.
# Delta formulas have 'exists' as the main operator.
# Gamma formulas have 'all'    as the main operator.
def tableau_canonize(f):

    # Handle double negations.
    if f[0] == 'not' and f[1][0] == 'not':
        return tableau_canonize(f[1][1])

    # Handle alpha formulas.
    if f[0] == 'and':
        return f 
    if f[0] == 'not' and f[1][0] == 'or':
        return ('and', [('not', g) for g in f[1][1]])
    if f[0] == 'not' and f[1][0] == 'arrow':
        return ('and', [f[1][1], ('not', f[1][2])])

    # Handle beta formulas.
    if f[0] == 'or':
        return f 
    if f[0] == 'not' and f[1][0] == 'and':
        return ('or', [('not', g) for g in f[1][1]])
    if f[0] == 'arrow':
        return ('or', [('not', f[1]), f[2]])

    # Handle delta formulas.
    if f[0] == 'exists':
        return f 
    if f[0] == 'not' and f[1][0] == 'all':
        return ('exists', f[1][1], ('not', f[1][2]))

    # Handle gamma formulas.
    if f[0] == 'all':
        return f
    if f[0] == 'not' and f[1][0] == 'exists':
        return ('all', f[1][1], ('not', f[1][2]))

    # Handle literals. 
    else:
        return f 

def tableau_skolemize(f, exists_vars, func_counter):
    free_vars = get_free_vars(f, exists_vars)
    used_funcs = get_funcs(f)

    g = f
    for v in exists_vars:
        while 'f' + str(func_counter) in used_funcs:
            func_counter += 1
        skolem_func = 'f' + str(func_counter)
        used_funcs.append(skolem_func)
        g = subst_formula({v:(skolem_func, list(free_vars))}, g)
    return (g, func_counter + 1)

def tableau_closed(branches):
    util.dprint('tableau_closed:')
    for b in branches:
        util.dprint('branch:')
        for f in b:
            util.dprint('  ', fml_to_str(f))
    util.dprint()
    substs = {}
    for branch in branches:
        util.dprint('substs so far:', subst_to_str(substs))
        newsubsts = tableau_branch_closed(branch, substs)
        util.dprint('new substitutions:', subst_to_str(newsubsts))
        if newsubsts == None:
            return False
        substs.update(newsubsts)
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
