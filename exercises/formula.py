import itertools
import re


class Operator:
    """
    operator class
        arity (if None, it's any)
        truth_function() (a function taking 
                a n (arity) arguments and 
                returning a truth value)
    """
    # TODO: Build an __eq__ method for Operator that checks if
    # two operators are equal by building a truth table for them
    # and comparing the truth tables
    def __init__(self, ascii_symbol, unicode_symbol, 
                       truth_function, arity = None):
        self.ascii_symbol = ascii_symbol
        self.unicode_symbol = unicode_symbol
        if self.unicode_symbol == None:
            self.unicode_symbol = self.ascii_symbol
        self.truth_function = truth_function
        self.arity = arity 
    
    def __repr__(self):
        return self.ascii_symbol

class Language:
    """
    language class
        operators
        (everythnig else is assumed
        to be a proposition)
        parsing function
    """

    def __init__(self, operators, brackets = None, charset = None):
        if charset == None:
            charset = 'ascii'
        self.set_charset(charset)
        self.operators = operators
        self.brackets = {('(',')'), ('[',']'), ('{','}')}

    def set_charset(self, charset):
        """ 
        sets the charset to either 'ascii' or 'unicode'.
        """
        if not charset in {'ascii', 'unicode'}:
            raise ValueError("charset must be 'ascii' or 'unicode'.")
        self.charset = charset

    def build_formula(self, operator, *args):
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
            main_connective = [s[0] for s in partition 
                               if len(s) == 1 and s[0] in 
                               {o for o in operators_set if not operator_dict[o].arity == 0}]
            if len(main_connective) > 1: 
                raise ValueError('more than one main connective', f_string)
            elif len(main_connective) < 1:
                raise ValueError('subformula has no main connective', f_string)
            else:
                main_connective = main_connective[0] 
            form = tuple([operator_dict[main_connective]] +\
                   [self.parse("".join(s)) for s in partition 
                    if not (len(s) == 1 and s[0] == main_connective)])

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

    def subformulas(self):
        subforms = {self} 
        if self.depth() > 0:
            for f in [self[i+1] for i in range(self[0].arity)]:
                subforms = subforms.union(f.subformulas()) 
        return subforms

    def main_connective(self):
        if self.depth() == 0:
            return None
        else:
            return self[0]

    def depth(self):
        for level in itertools.count():
            if not self:
                return level - 1
            self = list(itertools.chain.from_iterable(s for s in self 
                        if isinstance(s, tuple) or isinstance(s, Formula)))
    
    def copy(self):
        return Formula(self.language, self)

    def __getitem__(self, i):
        if i == 0:
            return tuple.__getitem__(self, i)
        else:
            return Formula(self.language, tuple.__getitem__(self, i)) 

    def __str__(self):
        if len(self) == 1:
            if self[0] in self.language.operators:
                if self.language.charset == 'unicode':
                    return self[0].unicode_symbol
                else: # 'ascii'
                    return self[0].ascii_symbol
            else: 
                return str(self[0])
        if self[0].arity == 1:
            return self.__build_str(self)
        else: 
            return self.__build_str(self)[1:-1]

    def __build_str(self, form):
        if form in self.language.operators:
            if self.language.charset == 'unicode':
                return ' ' + form.unicode_symbol + ' '
            else: # 'ascii'
                return form.ascii_symbol
        elif len(form) == 1:
            if form[0] in form.language.operators:
                if form.language.charset == 'unicode':
                    return form[0].unicode_symbol
                else: # 'ascii'
                    return form[0].ascii_symbol
            else:
                return str(form[0])
        elif form[0].arity == 1:
            return self.__build_str(form[0]) + self.__build_str(form[1])
        elif form[0].arity == 2:
            return '(' + self.__build_str(form[1]) + self.__build_str(form[0]) + self.__build_str(form[2]) + ')'
        else:
            return '(' + "".join([self.__build_str(sub) + ',' for sub in form])[:-1] + ')'


"""
TESTING
"""

ops = {
       Operator('F', '\u22a5', lambda: False, 0),
       Operator('&', '\u2227', lambda x, y: x and y, 2),
       Operator('|', '\u2228', lambda x, y: x or y, 2),
       Operator('->', '\u2192', lambda x, y: not x or y, 2),
       Operator('~', '\u00ac', lambda x: not x,      1)
      }

L = Language(ops, None, 'ascii')

phi = Formula(L, "((p&q)->~q)|~(p&F)")
psi = Formula(L, "p&q")
chi = Formula(L, "q->(F|r)")
fm1  = Formula(L, "F")
fm2  = Formula(L, "p")
fm3  = Formula(L, "~p")
fm4  = Formula(L, "~(prop&otherprop)")
