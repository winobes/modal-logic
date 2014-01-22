import itertools
import re


class Operator:
    """
    operator class
        arity (if None, it's any)
        function() (a function taking 
                a n (arity) arguments and 
                returning a truth value)
    """
    # TODO: Build an __eq__ method for Operator that checks if
    # two operators are equal by building a truth table for them
    # and comparing the truth tables
    def __init__(self, ascii_symbol, unicode_symbol, 
                       function, arity = None):
        self.ascii_symbol = ascii_symbol
        self.unicode_symbol = unicode_symbol
        if self.unicode_symbol == None:
            self.unicode_symbol = self.ascii_symbol
        self.function = function
        self.arity = arity 
    
    def __repr__(self):
        return self.ascii_symbol + '<' + str(self.arity) + '>'

class Language(dict):
    """
    language class
        operators
        (everythnig else is assumed
        to be a proposition)
        parsing function
    """

    def __init__(self, operators_dict, brackets = None, charset = None):
        super(Language, self).__init__(operators_dict)
        if charset == None:
            charset = 'ascii'
        self.set_charset(charset)
        self.operators = operators_dict.values()
        self.brackets = {('(',')'), ('[',']'), ('{','}')}

    def set_charset(self, charset):
        """ 
        sets the charset to either 'ascii' or 'unicode'.
        """
        if not charset in {'ascii', 'unicode'}:
            raise ValueError("charset must be 'ascii' or 'unicode'.")
        self.charset = charset

    def random_formula(self, atoms_range, possible_atoms = None):
        return generate_random_formula(self, atoms_range, possible_atoms)

    def build(self, arg1, *args):
        # if the first argument is the name of an operator in the language
        # then turn it into the operator before continuing
        if arg1 in self.keys():
            arg1 = self[arg1]
        if type(arg1) == str:
            return self.__string_to_formula(arg1)
        else:
            return self.__formulas_to_formula(arg1, *args)

    def __string_to_formula(self, string):
        return Formula(self, string)

    def __formulas_to_formula(self, operator, *args):
        #awaiting operator comparison
        #if not f_tuple[0] in self.operators:
            #raise ValueError('can only build formula with operators from\
                              #the build language.')
        try:
            f_tuple = tuple([tuple(sub) for sub in args])
        except:
            raise TypeError('arguments after the operator must be either a\
                             Formula or tuple')
        if not (len(f_tuple) == operator.arity or 
                                operator.arity == None):
            raise ValueError('number of arguments must match the arity of the\
                              operator.')
        return Formula(self, tuple([operator] + list(f_tuple)))

    def parse(self, f_string):
        """
        takes a string and returns a formula
        strings are stripped of whitespace
        any strings not operators are taken
        to be atomic formulas.
        """
        # remove all whitespace
        # TODO: this doesn't always work for some reason.
        ''.join(f_string.split())
        # set of bracket symbols and operator symbols
        # and dictionary from symbol to operator
        brackets_set = {b for b in itertools.chain.from_iterable(self.brackets)}
        if self.charset == 'ascii':
            operators_set = {o.ascii_symbol for o in self.operators}
            operator_dict = {s:o for s in operators_set for o in self.operators 
                                         if o.ascii_symbol == s}
        else: # self.charset == 'unicode'   
            operators_set = {o.unicode_symbol for o in self. operators}
            operator_dict = {s:o for s in operators_set for o in self.operators 
                                         if o.unicode_symbol == s}
        # turn the string into a list of (we assume) propositions separated 
        # strings we recognize (i.e. operators and brackets in the language)
        re_symbols = {re.escape(s) for s in operators_set|brackets_set}
        re_string =  '(' + ''.join(s + '|' for s in re_symbols)[:-1:] + ')'
        f_list = list(filter(None, re.split(re_string, f_string)))
        if [''] in f_list:
            raise ValueError('two consecutive operators in string')

        if len(f_list) == 1:
            # first check to see if it's actually a 0-ary operator
            try:
                return (operator_dict[f_list[0]], )
            # otherwise we assume it's a proposition
            except:
                return (f_list[0], )

        # partition by subformula:
        partition = [[]]
        bracket_stack = []
        i = 0 # index of current partition
        for s in f_list:
            partition[i].append(s)
            if s in {pair[0] for pair in self.brackets}:
                bracket_stack.append(s)
            elif s in {pair[1] for pair in self.brackets}:
                if not (bracket_stack.pop(), s) in self.brackets:
                    raise ValueError('mismatched brackets')
                # If the bracket we just popped was the last in the stack,
                # then we are at the end of a subformula.
                if bracket_stack == []: 
                    i += 1
                    partition.append([])
            elif bracket_stack == []:
            # If the bracket stack is empty, then the symbol gets its own
            # partition unless it is a one-place operator.
                if not (s in operators_set and operator_dict[s].arity == 1): 
                    i += 1 
                    partition.append([])
        partition = partition[:-1]

       
        # if there's only one partition, then either we need to remove
        # outter brackets or a unary operator is the main connective.
        if len(partition) == 1:
            if (partition[0][0], partition[0][-1]) in self.brackets:
                form = tuple(self.parse(f_string[1:-1]))
            elif partition[0][0] in {o for o in operators_set 
                                     if operator_dict[o].arity == 1}:
                form = tuple([operator_dict[partition[0][0]], 
                        self.parse(f_string[1:])])
            else:
                raise ValueError("can't partition subformula", f_string)
        else:
            operator = [s[0] for s in partition 
                               if len(s) == 1 and s[0] in 
                               {o for o in operators_set if not operator_dict[o].arity == 0}]
            if len(operator) > 1: 
                raise ValueError('more than one main connective', f_string)
            elif len(operator) < 1:
                raise ValueError('subformula has no main connective', f_string)
            else:
                operator = operator[0] 
            form = tuple([operator_dict[operator]] +\
                   [self.parse("".join(s)) for s in partition 
                    if not (len(s) == 1 and s[0] == operator)])

        return tuple(form)

class Formula(tuple):
    """
    Formula must be initialized with a language. The language determines
    how a string init_val is parsed. If a tuple is passed as init_val,
    it is not parsed before assignment. Reccomend only using this 
    feature to create a new formula from an old one.
    """
   
    def __new__ (cls, language, init_val):
        if type(init_val) == str:
            return super(Formula, cls).__new__(cls, language.parse(init_val))
        else: # try to convert it to a tuple (e.g. works for list or Formula) 
            try: return super(Formula, cls).__new__(cls, tuple(init_val))
            except: 
                raise TypeError('class Formula does not support initialization \
                      type', type(init_val), ". Must be either 'str' or 'tuple'.")

    def __init__(self, language, init_val):
        self.language = language 

    def atomics(self):
        return {p for p in self.subformulas() if p.depth() == 0 and 
                            p[0] not in self.language.operators}

    def operand(self):
        """
        Returns of the formulas connected by the main 
        connective (retaining the order they appear in
        the formula).
        """
        if self.is_atomic():
            return None
        else:
            return [self[i+1] for i in range(len(self) - 1)]

    def subformulas(self):
        subforms = {self} 
        if self.depth() > 0:
            for f in [self[i+1] for i in range(self[0].arity)]:
                subforms = subforms.union(f.subformulas()) 
        return subforms

    def operator(self):
        if self.is_atomic():
            return None
        else:
            return self[0]

    def is_atomic(self):
        if not type(self[0]) == Operator:
            return True
        else:
            return False

    def depth(self):
        for level in itertools.count():
            if not self:
                return level - 1
            self = list(itertools.chain.from_iterable(s for s in self 
                        if isinstance(s, tuple) or isinstance(s, Formula)))


    def evaluate(self, values):
        """
        Expects either a dictionary from atomic formulas to
        values or a list of values in alphanumeric order
        with respcet to the atomic formulas' string.
        """
        if not type(values) == dict:            
            alpha_atomics = sorted(self.atomics())
            if len(values) < len(alpha_atomics):
                raise ValueError('not enough values for the forumla.',
                len(value), 'given,', str(self), 'has', len(alpha_atomics),
                'atomics.')
            values = {atom:value for (atom,value) in zip(alpha_atomics, values)}
            print(values) 
            # build the dictionary
       
        if self.is_atomic():
            return values[self]
        else:
            try: 
                return self.operator().function(
                    *[f.evaluate(values) for f in self.operand()])
            except KeyError:
                raise ValueError('values not given for every atomic in \
                                  formula:', str(self))
    
    def copy(self):
        return Formula(self.language, self)

    def __getitem__(self, i):
        if i == 0:
            return tuple.__getitem__(self, i)
        else:
            return Formula(self.language, tuple.__getitem__(self, i)) 

    def __str__(self):
        return _formula_to_string(self, self.language.charset)


def _formula_to_string(f, charset):
    """
    Convert a f in Formula format to a string.
    """
    
    if charset == 'unicode':
        op_to_char = {op: op.unicode_symbol  
                        for op in f.language.operators}
    elif charset == 'ascii':
        op_to_char = {op:op.ascii_symbol 
                        for op in f.language.operators}
    else:
        raise ValueError('unsupported charset:', charset)
    for op in op_to_char.keys():
        if op.arity == 2:
            op_to_char[op] = ' ' + op_to_char[op] + ' '

    if f.is_atomic():
        # The f is atomic.
        string = f[0]

    elif f[0].arity == 0:
        # If the main operator is 0-ary, handle it.
        string = op_to_char[f[0]]

    else:
        # If the main operator is unary, handle it.
        if f[0].arity == 1:
            string = op_to_char[f[0]]
        else:
            string = ''

        # Handle the first (and possibly only) operand.
        if f[1].is_atomic() or f[1][0].arity < 2:
            string += _formula_to_string(f[1], charset)
        else:
            string += '(' + _formula_to_string(f[1], charset) + ')'

        # If the main operator is binary, handle the remainder of the f.
        if f[0].arity == 2:
            # Handle the binary operator.
            string += op_to_char[f[0]]

            # Handle the second operand.
            if f[2].is_atomic() or f[2][0].arity < 2:
                string += _formula_to_string(f[2], charset)
            else:
                string += '(' + _formula_to_string(f[2], charset) + ')'
    return string

import random 

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
            formula = language.build(op, pop_random(subformulas))
        elif op.arity == 2:
            if len(subformulas) == 1:
                raise ValueError('too many operators')
            formula = language.build(op, pop_random(subformulas), 
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


"""
TESTING
"""

