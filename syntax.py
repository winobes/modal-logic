import itertools

default_language = [{'p','q','r'},
                    [{'\u22A5'}, # bottom
                    {'\u00AC'}, # lnot 
                    {'\u2227', '\u2228', '\u2192'}], # wedge, vee, arrow
                    ('\u25C7', '\u25FB'), # diamond, box
                    {('(',')'), ('[',']'), ('{','}')}
                   ] 
                            

class Language:
    """
    A basic modal language consists of:
    - a set of propositions (one character strings)
    - a list of sets of constants (list position is arity) 
    - a modal operator and it's dual 
    - a a set of pairs of opening and closing brackets 
    """
    def __init__(self, prop = None, 
                       constants = None, 
                       modality = None, 
                       brackets = None):
        if prop == None:
            prop = default_language[0]
        self.prop = prop
        if constants == None:
            constants = default_language[1] 
        self.constants = constants
        if modality == None:
            modality = default_language[2] 
        self.modality = modality
        if brackets == None:
            brackets = default_language[3] 
        self.brackets = brackets

    def __repr__(self):
        return ('language' + '(' + str(self.prop) + ', ' +
                str(self.constants) + ', ' + 
                str(self.modality) + ', ' +
                str(self.brackets) + ')')

def parse_formula(L, formula):
    return tuple_tableau(list_tableau(L, formula))

def list_tableau(L, formula):
    """
    Takes a formula as a string and gives it a tableau form for
    easier parsing by other functions (e.g. valuation, satisfaction).
    The language argument lets the function know how to interpret 
    the symbols (i.e. as connectives, modal operators, propositions).
    Properly formatted formulas must include all but the outermost
    parenthesis, and may include spaces for better readability.

    tableau("p ∧ q") = ['∧', 'p', 'q']

    tableau("◇ p ∧ q") = ['∧', ['◇', 'p'], 'q']

    tableau("◇ p ∧ (q →  ¬(p ∨ ◻ q))") =
    ['∧', ['◇', 'p'],  ['→ ', 'q', ['¬', ['∨', 'p', ['◻ ','q']]]]]
    """
    
    # Remove whitespace from the formula.
    formula = ''.join(formula.split())
    tableau = []

    # If it's atomic, return.
    if len(formula) == 1:
        if formula in L.prop:
            return formula
        else: raise ValueError("unexpected character; expected a proposition")
    
    # First partition by subformulas.
    partition = [[]]
    bracket_stack = []
    i = 0 # Index of current subformula/partition.
    for ch in formula:
        partition[i].append(ch)
        if ch in {pair[0] for pair in L.brackets}:
            bracket_stack.append(ch)
        elif ch in {pair[1] for pair in L.brackets}:
            if not (bracket_stack[-1], ch) in L.brackets:
                raise ValueError("mismatched brackets")
            bracket_stack.pop()
            # If the bracket we just popped was the last in the stack,
            # then we are at the end of a subformula.
            if bracket_stack == []: 
                i += 1
                partition.append([])
        elif bracket_stack == []:
        # If the bracket stack is empty, propositions and 0-place 
        # logical constants are get theirl lown partitiony.
        # Likewise for constants of arity >2; they deliminate subformulas.
            if (((len(L.constants)) > 0 and ch in L.constants[0]) or
               ch in L.prop):
                i += 1
                partition.append([])    
            if (len(L.constants) > 2 and 
               any(ch in constants for constants in L.constants[2:])):
                i += 1 
                partition.append([])
    partition = partition[:-1]

    # Either we need to remove outter brackets, or a unary operator is
    # the main connective.
    if len(partition) == 1:
        if (partition[0][0], partition[0][-1]) in L.brackets:
            tableau = parse_formula(L, formula[1:-1])
        elif partition[0][0] in L.constants[1] or partition[0][0] in L.modality:
            tableau = [partition[0][0], parse_formula(L, formula[1:])]
        else: 
            raise ValueError("can not partition formula")
    # One of the partitions should be the main connective. Find it,
    # add it to the tableau, and parse the remaning subformulas
    else:
        for sub in partition: 
            if (len(sub) == 1 and 
                sub[0] in {const for const in itertools.chain(*L.constants)}):
                tableau = [sub[0]] + \
                          [parse_formula(L, ''.join(form)) \
                          for form in partition if not form[0] == sub[0]]

    return tableau

def tuple_tableau(form):
    if type(form) == list:
        return tuple(tuple_tableau(sub) for sub in form)
    elif type(form) == str or type(form) == tuple:
        return form
    else: 
        print(form)
        raise ValueError("error converting formula list to tuples:") 

def get_subformulas(f):
    """
    Return the set of all subformulas of f.
    """

    subforms = {f}
    if len(f) > 1:
        # f has a unary or binary operator: get first operand.
        subforms = subforms.union(get_subformulas(f[1]))
    if len(f) == 3:
        # f has a binary operator: get second operand.
        subforms = subforms.union(get_subformulas(f[2]))
    return subforms

def subformula_close(fset):
    """
    Close fset under subformulas.
    """

    closed_fset = set()
    for f in fset:
        closed_fset = closed_fset.union(get_subformulas(f))
    return closed_fset

class logical_constant:
    """
    A logical constant defines is a function from one or more booleans
    to a boolean value.

    The symbol may be a unicode character. e.g.:
    '\u2227' - wedge
    '\u2228' - vee
    '\u00AC' - lnot
    '\u2192' - arrow
    '\u22A5' - bottom

    The interpretation s ia dictionary from ntuples of boolean
    values to bolean values. It should give a value to each possible
    key in the space. e.g.:

    and.interpretation = {(0,0):0, (0,1):0, (1,0):0, (1,1):1}
    """

    def __init__(self, symbol, n_place, interpretation):
        self.symbol = symbol 
        self.place = n_place
        self.interpretation = interpretation

    def __repr__(self):
        return ('logical_constant(' + '"' + str(self.symbol) + '"' + ', '  +
                 str(self.place) + ', ' + str(self.interpretation) + ')')
