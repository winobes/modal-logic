def pred(f):
    return f[0] in 'PQRS'

def constant(x):
    return isinstance(x, str) and x in 'abc'

def variable(x):
    return isinstance(x, str) and x in 'xyz'

def function(x):
    return isinstance(x, tuple) and x[0] in 'fghj'

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
    for i in range(len(a)):
        s += a[i][0] + args_to_str(a[i][1]) if function(a[i]) else str(a[i])
        if i != len(a) - 1:
            s += ', '
    s += ')'
    return s

# Return a random formula.
def random_fml(npreds = (2, 8), arities = {}):
    from random import randrange
    from util import get_random_item, pop_random_item

    if npreds[0] < 1 or npreds[0] >= npreds[1]:
        raise ValueError('invalid range')

    preds = tuple([p, 0] for p in 'PQRS')
    constants = ('a', 'b', 'c')
    variables = ('x', 'y', 'z')
    functions = tuple([f, 0] for f in 'fghj')
    operators = ('not', 'and', 'or', 'arrow', 'all', 'exists')

    for p in preds:
        p[1] = arities[p[0]] if p[0] in arities else randrange(1, 4)

    for f in functions:
        f[1] = arities[f[0]] if f[0] in arities else randrange(1, 2)

    npreds = randrange(*npreds)
    fmls = []

    for i in range(npreds):
        pred = get_random_item(preds)
        args = []
        for i in range(pred[1]):
            choice = randrange(0, 3)
            if choice == 0:
                args.append(get_random_item(constants))
            elif choice == 1:
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

# Evaluate the formula f. The assignment is a dictionary from free variables to 
# elements of the domain, and the interpretation is a dictionary from predicates
# to a set of n-tuples of elements from the domain where n is the arity of the 
# predicate.
# TODO Test for predicate arity errors in assignment
def evaluate(f, asgmnt, intprt, domain):
    if pred(f):
        return tuple(interpret_args(list(f[1]), asgmnt, intprt)) in \
            intprt[f[0]]
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

# Checks the validity of f on k models of size n. Returns the first countermodel
# found. If no countermodel of size n is found, returns None.
def check_models(f, n, k):
    from itertools import combinations, combinations_with_replacement
    from random import randint, sample
    domain = {str(i) for i in range(n)}
    preds = get_preds(f)
    combos = {p:{combo for combo in combinations_with_replacement(domain, preds[p])} for p in preds}
    hash_list = []
    checked = 0
    while checked < k:
        intprt = {p:frozenset(sample(combos[p], randint(0, len(combos[p])))) for p in preds}
        model_hash = hash(frozenset(intprt.items()))
        if not model_hash in hash_list:
            hash_list.append(model_hash)
            checked += 1
            if not evaluate(f, {}, intprt, domain):
                return intprt
    return None
        
# Helper function for evaluate(): interpret the arguments of a predicate or
# function symbol.
def interpret_args(args, asgmnt, intprt):
    for i in range(len(args)):
        if constant(args[i]):
            args[i] = intprt[args[i]]
        elif function(args[i]):
            funcsymbol = args[i][0]
            funcargs = interpret_args(args[i][1], asgmnt, intprt)
            args[i] = intprt[funcsymbol][tuple(funcargs)]
        elif variable(args[i]):
            args[i] = asgmnt[args[i]]
    return args

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
