def pred(f):
    return f[0] in 'PQRS'

# Convert a formula to a string.
def fml_to_str(f):
    if pred(f):
        s = f[0]
        for t in f[1]:
            s += t
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
    elif f[0] == 'all' or f[0] == 'exists':
        if f[0] == 'all':
            s = 'A'
        else:
            s = 'E'
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

# Return a random formula.
def random_fml(npreds = (2, 8)):
    from random import randint, randrange
    from util import get_random_item, pop_random_item

    if npreds[0] < 1 or npreds[0] >= npreds[1]:
        raise ValueError('invalid range')

    preds = tuple([p, randrange(1, 4)] for p in 'PQRS')
    variables = ('x', 'y', 'z')
    operators = ('not', 'and', 'or', 'arrow', 'all', 'exists')

    npreds = randrange(*npreds)
    fmls = []

    for i in range(npreds):
        p = get_random_item(preds)
        fmls.append((p[0],
            list(get_random_item(variables) for i in range(p[1]))))

    while len(fmls) > 1:
        o = get_random_item(operators)
        if o == 'not':
            fmls.append(('not', pop_random_item(fmls)))
        elif o == 'and':
            nconjuncts = randint(2, int(len(fmls) / 2) + 1)
            fmls.append(('and',
                [pop_random_item(fmls) for i in range(nconjuncts)]))
        elif o == 'or':
            ndisjuncts = randint(2, int(len(fmls) / 2) + 1)
            fmls.append(('or',
                [pop_random_item(fmls) for i in range(ndisjuncts)]))
        elif o == 'arrow':
            fmls.append(('arrow', pop_random_item(fmls),
                pop_random_item(fmls)))
        elif o == 'all':
            nvars = randint(1, 3)
            fmls.append(('all',
                set(get_random_item(variables) for i in range(nvars)),
                pop_random_item(fmls)))
        elif o == 'exists':
            nvars = randint(1, 3)
            fmls.append(('exists',
                set(get_random_item(variables) for i in range(nvars)),
                pop_random_item(fmls)))
        else:
            raise ValueError('unexpected operator: %s' % o)

    return fmls[0]
