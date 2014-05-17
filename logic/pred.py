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

# Return a random formula.
def random_fml(npreds = (2, 8), arities = {}):
    from random import randrange
    from util import get_random_item, pop_random_item

    if npreds[0] < 1 or npreds[0] >= npreds[1]:
        raise ValueError('invalid range')

    preds = tuple([p, 0] for p in 'PQRS')
    variables = ('x', 'y', 'z')
    functions = tuple([f, 0] for f in 'abcdfghj')
    operators = ('not', 'and', 'or', 'arrow', 'all', 'exists')

    for p in preds:
        p[1] = arities[p[0]] if p[0] in arities else randrange(1, 4)

    for f in functions:
        if f[0] in 'fghj':
            f[1] = arities[f[0]] if f[0] in arities else randrange(1, 3)
        elif f[0] in 'abcd':
            f[1] = 0 

    npreds = randrange(*npreds)
    fmls = []

    for i in range(npreds):
        pred = get_random_item(preds)
        args = []
        for i in range(pred[1]):
            choice = randrange(0, 2)
            if choice == 0:
                args.append(get_random_item(variables))
            else:
                func = get_random_item(functions)
                args.append((func[0],
                    list(get_random_item(variables) for i in range(func[1]))))
        fmls.append((pred[0], args))

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
            fmls.append(('arrow', pop_random_item(fmls),
                pop_random_item(fmls)))
        elif o == 'all':
            nvars = randrange(1, 4)
            fmls.append(('all',
                set(get_random_item(variables) for i in range(nvars)),
                pop_random_item(fmls)))
        elif o == 'exists':
            nvars = randrange(1, 4)
            fmls.append(('exists',
                set(get_random_item(variables) for i in range(nvars)),
                pop_random_item(fmls)))
        else:
            raise ValueError('unexpected operator: %s' % o)

    return fmls[0]

# gives a random list of formulas generated from the same language
# useful for testing functions dealing with entailment
# ranges N and D are a pair of numbers (inclusive)
# preds and funcs are dictionaries from symbols to arities.
def random_fml_list(preds, funcs, consts, N, D):

    from random import randrange

    return [random_fml2(preds, funcs, consts, randrange(D[0], D[1] + 1)) 
                for i in range(randrange(N[0], N[1] + 1))]

# Gives a random formula of the sepecified depth from the
# specified language.
def random_fml2(preds, funcs, consts, depth):

    from random import choice

    if depth == 0:
        if not consts:
            raise ValueError('0-depth formula requires constants')
        pred = choice(list(preds.keys()))
        arity = preds[pred]
        return (pred, [random_term(funcs, consts, 0)  
                for i in range(arity)])

    else:
        
        if not consts: # if there are no constants, we need a quantifier
            op = choice(['exists', 'all'])
        else: # otherwise, we take any operator
            op = choice(['and', 'or', 'arrow', 'not', 'exists', 'all'])

        base_terms = consts.copy()
        if op in ('all', 'exists'):
            var = choice(['x','y','z'])
            base_terms.add(var)  # include bound variables in consts
            return (op, {var}, random_fml2(preds, funcs, base_terms, depth - 1))
        if op == 'not':
            return (op, random_fml2(preds, funcs, base_terms, depth - 1 ))
        if op == 'arrow':
            return (op, random_fml2(preds, funcs, base_terms, depth - 1),
                        random_fml2(preds, funcs, base_terms, depth - 1))
        if op in ('and', 'or'):
            return (op, [random_fml2(preds, funcs, base_terms, depth - 1)
                         for i in range(2)])

def random_term(funcs, base_terms, depth):

    from random import choice

    if depth == 0:
        return choice(list(base_terms))
    else:
        f = choice(list(funcs.keys()))
        arity = funcs[f]
        return (f, [random_term(funcs, base_terms, depth -1) 
                for i in range(arity)])

# Evaluate the formula f. The assignment is a dictionary from free variables to 
# elements of the domain, and the interpretation is a dictionary from predicates
# to a set of n-tuples of elements from the domain where n is the arity of the 
# predicate.
# TODO Test for predicate arity errors in assignment
def evaluate(f, asgmnt, intprt, domain):
    if pred(f):
        return tuple([interpret_arg(arg, intprt, asgmnt) 
                                        for arg in f[1]]) in intprt[f[0]]
    if f[0] == 'not':
        return not evaluate(f[1], asgmnt, intprt, domain)
    if f[0] == 'and':
        return all(evaluate(g, asgmnt, intprt, domain) for g in f[1])
    if f[0] == 'or':
        return any(evaluate(g, asgmnt, intprt, domain) for g in f[1])
    if f[0] == 'arrow':
        return not evaluate(f[1], asgmnt, intprt, domain) or evaluate(f[2], asgmnt, intprt, domain)
    if f[0] == 'all' or f[0] == 'exists' :
        return eval_bound(f, asgmnt, intprt, domain)
    raise ValueError('unknown operator:', f[0])

# Helper function for evaluate. 
def eval_bound(f, asgmnt, intprt, domain):
    from itertools import combinations_with_replacement
    all_asgmnt = [{x:a for (x,a) in zip(f[1], combo)}
        for combo in combinations_with_replacement(domain, len(f[1]))]
    if f[0] == 'all':
        return all(evaluate(f[2], dict(list(asgmnt.items()) + list(d.items())), intprt, domain) for d in all_asgmnt)
        # d overwrites the assignment for bound variables 
    if f[0] == 'exists':
        return any(evaluate(f[2], dict(list(asgmnt.items()) + list(d.items())), intprt, domain) for d in all_asgmnt)
    raise ValueError('unknown operator:', f[0])

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

# Checks the validity of f on k models of size n. Returns the first countermodel
# found. If no countermodel of size n is found, returns None.
def check_models(f, n, k):
    from itertools import combinations, product 
    from random import randint, sample
    domain = {str(i) for i in range(n)}
    preds = get_preds(f)
    variables = get_variables(f)
    funcs = get_functions(f)
    combos = {p:{combo for combo in product(*[domain for i in range(preds[p])])} for p in preds}
    combos.update({f:{combo for combo in product(*[domain for i in range(funcs[f])])} for f in funcs})
    hash_list = []
    checked = 0
    while checked < k:
        intprt = {p:frozenset(sample(combos[p], randint(0, len(combos[p])))) for p in preds}
        intprt.update({f:{x:sample(domain, 1)[0] for x in combos[f]} for f in funcs})
        model_hash = hash(frozenset({a:(intprt[a] if not a in funcs else hash(frozenset(intprt[a].items()))) for a in intprt.keys()}.items()))
        if not model_hash in hash_list:
            hash_list.append(model_hash)
            checked += 1
            asgmnt = {v:sample(domain, 1)[0] for v in variables}
            if not evaluate(f, asgmnt, intprt, domain):
                return (intprt, asgmnt)
    return None
        
# Helper function for evaluate(): interpret the arguments of a predicate or
# function symbol.
def interpret_arg(f, asgmnt, intprt):
    if variable(f):
        return intprt[f] 
    elif function(f):
        return asgmnt[f[0]][tuple([interpret_arg(arg, asgmnt, intprt) 
                        for arg in f[1]])]
    else:
        raise ValueError('expected variable or function')

# takes a well-formatted string and returns a formula
def parse(fml_str):
    import re

    fml_str = ''.join(fml_str.split())
    re_symbols = {re.escape(s) for s in {'(', ')', '&', '->', 'V', '~'}}
    re_string =  '(' + ''.join(s + '|' for s in re_symbols)[:]+ 'A[xyz]*' + '|' + 'E[xyz]*' + ')'
    fml_lst = list(filter(None, re.split(re_string, fml_str)))
    if len(fml_lst) == 1: 
    # atomic formula
        return tuple([fml_lst[0][0], [indv for indv in fml_lst[0][1:]]])

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
            if not (s == '~' or s[0][0] in {'E', 'A'}):
                i += 1
                partition.append([])
    partition = partition[:-1]
    
    if len(partition) == 1:
        # extra outter brackets
        if (partition[0][0], partition[0][-1]) == ('(', ')'):
            fml = tuple(parse(fml_str[1:-1]))
        # ~ is main connective
        elif partition[0][0] == '~':
            fml = tuple(['not', parse(fml_str[1:])])
        elif partition[0][0].startswith('A'):
            fml = tuple(['all', {x for x in partition[0][0][1:]}, parse("".join(partition[0][1:]))])
        elif partition[0][0].startswith('E'):
            fml = tuple(['exists', {x for x in partition[0][0][1:]}, parse("".join(partition[0][1:]))])
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

#def tableau(f):
#    return tableau_do([[cnf(('not', f))]])
#
#def tableau_do(tab):
#    new_tab = [] 
#    for branch in tab:
#        new_branches = tableau_expand(branch)
#        for branch in new_branches:
#            if not tableau_branch_closed(branch):
#                new_tab.append(branch) 
#    if new_tab == []:
#        return True
#    elif new_tab == tab:
#        return False 
#    else: 
#        return tableau_do(new_tab)
#
# Expand a branch and return the result as a list of branches.
#def tableau_expand(branch):
#    branch = branch[:]
#    for f in branch:
#        if f[0] == 'and':
#            branch.remove(f)
#            for g in f[1]: branch.append(g)
#            return [branch]
#        elif f[0] == 'or':
#            branch.remove(f)
#            return [branch + [g] for g in f[1]]
#    return [branch]

def tableau_closed(branches):
    for b in branches:
        print('branch:')
        for f in b:
            print('  ', fml_to_str(f))
    print()
    substs = []
    for branch in branches:
        print('substs so far:', subst_to_str(substs))
        newsubsts = tableau_branch_closed(branch, substs)
        print('new substitutions:', subst_to_str(newsubsts))
        if newsubsts == None:
            return False
        substs += newsubsts
    print('tableau closed with', subst_to_str(substs))
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

def tableau(f, gdepth):
    branches = tableau_expand([('not', f)], gdepth)
    return tableau_closed(branches)

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

def tableau_expand(branch, qdepth):
    return tableau_expand_do([branch], qdepth, 0)

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

def tableau_expand_do(branches, gdepth, skolem_func_counter):
    for branch in branches[:]:

        # Handle alpha formulas.
        for f in branch:
            tmp = tableau_fml_type(f)    
            subs = tmp[1]
            fml_type = tmp[0]

            if fml_type == 'alpha':
                branches.remove(branch)
                branch.remove(f)
                branches.append(branch + subs)
                return tableau_expand_do(branches, gdepth, skolem_func_counter)

        # Handle beta formulas.
        for f in branch:
            tmp = tableau_fml_type(f)    
            subs = tmp[1]
            fml_type = tmp[0]

            if fml_type == 'beta':
                branches.remove(branch)
                branch.remove(f)
                for g in subs:
                    branches.append(branch + [g])
                return tableau_expand_do(branches, gdepth, skolem_func_counter)

        # Handle delta formulas (before gamma formulas).
        for f in branch:
            tmp = tableau_fml_type(f)    
            sub = tmp[1]
            fml_type = tmp[0]

            if fml_type == 'delta':
                branches.remove(branch)
                branch.remove(f)
                g, skolem_func_counter = tableau_skolemize(sub[1], sub[0],
                    skolem_func_counter)
                branch.append(g)
                branches.append(branch)
                return tableau_expand_do(branches, gdepth, skolem_func_counter)

        # Handle gamma formulas.
        for f in branch:
            tmp = tableau_fml_type(f)
            sub = tmp[1]
            fml_type = tmp[0]

            if fml_type == 'gamma':
                branches.remove(branch)
                branch.remove(f)
                branch.append(sub[1])
                branches.append(branch)
                return tableau_expand_do(branches, gdepth, skolem_func_counter)


    return branches
