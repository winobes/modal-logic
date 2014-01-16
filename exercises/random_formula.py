import random 

def generate_random_formula(n_atoms_range, negation_probability, 
                            possible_atoms = None, possible_operators = None):
    """
    Generates a random formula from:
        n_atoms_range - range tuple (first element smaller than seccond)
              The formula with have some number of atoms in this range.
        negation_probablity - the probability that any given subformula 
              in the formula is negated.
        possible_atoms - a list of tuples whose first element is an
              atomic sentence and whose seccond element is the element's
              probability distribution (such that they all sum to 1)
              If None, defaults to some random number of characters 
              between 'p' and 'z' (more for longer formulas, less
              for shorter formulas. 
        possible_operators - likewise for operators. If None, defaults 
              to [('and', 1/3), ('or', 1/3), ('arrow', 1/3)]
    """
    from string import ascii_lowercase

    if (not n_atoms_range[0] > 0 or
        not n_atoms_range[0] <= n_atoms_range[1]):
        raise ValueError('bad range for number of atoms')

    n_atoms = random.randrange(*n_atoms_range)
    if possible_atoms == None:
        n_possibles = random.randrange(int(n_atoms/2), n_atoms)
        possible_atoms = [(p, 1/min(n_possibles,11)) for p in ascii_lowercase[15:min(15 + n_possibles, 26)]]
    if possible_operators == None:
        possible_operators = [(o, 1/3) for o in {'and', 'or', 'arrow'}]

    atoms_list = generate_symbol_list(n_atoms, possible_atoms)
    operators_list = generate_symbol_list(n_atoms - 1, possible_operators) 

    return construct_formula(atoms_list, operators_list, negation_probability)

def generate_symbol_list(n_symbols, possible_symbols):
    """
    possible_symbols - list of pairs (symbol, probability)
    returns a random list of n_symbols symbols from 
    possible_symbols
    """
    print([item[1] for item in possible_symbols])
    print(sum( [item[1] for item in possible_symbols]))

    if not abs(1 - sum([item[1] for item in possible_symbols])) < .01:
        raise ValueError('symbol occurance probabilities must sum to 1')

    pos_ops = [possible_symbols[0]]
    for i in range(1, len(possible_symbols)):
        pos_ops.append((possible_symbols[i][0], possible_symbols[i][1] + pos_ops[i-1][1]))

    symbols = []
    for i in range(n_symbols):
        r = random.random()
        for op in pos_ops:
            if op[1] > r:
                symbols.append(op[0]) 
                break
    return symbols 

def construct_formula(atoms, operators, negation_probability): 
    """
    Builds a random formula from a list of atoms and operators.
    The order of the lists does not matter. negation_probability
    determines the probability that any given subformula will
    be negated.
    """
    if len(atoms) > len(operators) + 1:
        raise ValueError('too many atomositions')
    if len(atoms) < len(operators) + 1:
        raise ValueError('too many operators')

    subformulas = [] 
    for p in atoms:
        if random.random() > negation_probability:
            subformulas.append(p)
        else:
            subformulas.append(('not', p))
             
    while not operators == []:
        # pop a random operator and two random formulas
        # from the subformula list
        formula = (pop_random(operators), 
                  pop_random(subformulas), pop_random(subformulas))
        # with some probability, the new subformula is
        # negated before being added back to the list
        if random.random() > negation_probability:
            formula = ('not', formula)

        subformulas.append(formula)

    return subformulas[0]

def pop_random(l):
    """
    Returns a random element from a list, removing it from
    the list.
    """
    if len(l) == 0:
        raise ValueError('list must have at least one element')
    return l.pop(random.randint(0, len(l) - 1))


