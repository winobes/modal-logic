import random 
from formula import Formula, Language, Operator

def generate_random_formula(language, atoms_range,
                    possible_atoms = None):
    """
    Generates a random formula from:
        atoms_range - range tuple (first element smaller than seccond)
              The formula with have some number of atoms in this range.
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
     
    unary_operators = {op for op in language.operators if op.arity == 1}
    binary_operators = {op for op in language.operators if op.arity == 2}

    if (not atoms_range[0] > 0 or
        not atoms_range[0] <= atoms_range[1]):
        raise ValueError('bad range for number of atoms')

    n_atoms = random.randrange(*atoms_range)
    # generate list of atoms if none given
    if possible_atoms == None:
        n_possibles = random.randrange(int((n_atoms + 1)/2), int(2 * n_atoms))
        possible_atoms = [(p, 1/min(n_possibles,11)) 
                for p in ascii_lowercase[15:min(15 + n_possibles, 26)]]
    # generate operator probability from language if none given
    possible_binary_operators = [(o, 1/len(binary_operators)) for o in binary_operators]

    atoms_list = generate_symbol_list(n_atoms, possible_atoms)
    operators_list = generate_symbol_list(n_atoms - 1, possible_binary_operators) 
    for operator in unary_operators:
        number = random.randrange(0, n_atoms + 1)
        operators_list.extend([operator for n in range(number)])

    return construct_formula(language, atoms_list, operators_list)

def generate_symbol_list(n_symbols, possible_symbols):
    """
    possible_symbols - list of pairs (symbol, probability)
    where symbol is either a string (atomic prop) or an operator
    returns a random list of n_symbols symbols from 
    possible_symbols
    """

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

def construct_formula(language, atoms, operators): 
    """
    Builds a random formula from a list of atoms and operators.
    The order of the lists does not matter. 
    """
    for op in operators: 
        if not op in language.operators:
            raise ValueError('unexpected operator')

    subformulas = [Formula(language, atom) for atom in atoms]
   
    while not operators == []:
        # pop a random operator and a number of random formulas
        # matching its arity from the subformula list
        op = pop_random(operators)
        if op.arity == 1:
            formula = language.build_formula(op, pop_random(subformulas))
        elif op.arity == 2:
            if len(subformulas) == 1:
                raise ValueError('too many operators')
            formula = language.build_formula(op, pop_random(subformulas), 
                                                 pop_random(subformulas))
        subformulas.append(formula)

    if not len(subformulas) == 1:
        raise ValueError('too many atoms')
 
    return subformulas[0]

def pop_random(l):
    """
    Returns a random element from a list, removing it from
    the list.
    """
    if len(l) == 0:
        raise ValueError('list must have at least one element')
    return l.pop(random.randint(0, len(l) - 1))
