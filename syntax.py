def main_connective(language, formula, offset = 0):
    """
    Finds the main connective in a formula and returns its index.
    """
    if not formula.count('(') == formula.count(')'):
        raise ValueError("formula contains non-matching brackets")
    elif formula.count('(') == 0:
        for two_place in [symbol for symbol in language.lexicon if language.n_place(symbol) == 2]:
            if not formula.find(two_place) == -1:
                return formula.find(two_place) + offset
        print("offset = " + str(offset))
        return 0 + offset
    else:
        i = 0
        c = 0
        paren = False
        for ch in formula:
            c += 1
            if ch == '(': 
                i += 1
                paren = True
            if ch == ')': 
                i -= 1
                paren = True
            if i == 0 and paren == True:
                if c == len(formula):
                    if not formula[0] == '(':
                        print("offset = " + str(offset))
                        return 0 + offset
                    return main_connective(language, formula[1:-1], offset + 1)
                else: 
                    print("offset = " + str(offset))
                    print("count = " + str(c))
                    return c + offset

def make_tableau(language, formula):
    """
    Takes a formula as a string and gives it a tableau form for
    easier parsing by other functions (e.g. valuation, satisfation).
    The language argument lets the function know how to interpret 
    the symbols (i.e. as connectives, modal operators, propositions).
    Properly formatted formulas must include all but the outtermost
    parenthesis, and may include spaces for better readability.

    tableau("p ∧ q") = ['∧', 'p', 'q']

    tableau("◇ p ∧ q") = ['∧', ['◇', 'p'], 'q']

    tableau("◇ p ∧ (q →  ¬(p ∨ □ q))") =
    ['∧', ['◇', 'p'],  ['→ ', 'q', ['¬', ['∨', 'p', ['□ ','q']]]]]
    """
    tableau = []
    formula = formula.replace(' ','')
    print("now parsing " + formula)
    if formula[0]  == '(' and formula.count('(') > formula.count(')'):
        formula = formula[1:]
    if formula[-1] == ')' and formula.count(')') > formula.count('('):
        print("fixing extra ')'")
        formula = formula[:-1]
    if len(formula) == 1:
        tableau = formula
    else:
        connective = main_connective(language, formula)
        print("appending the connective")
        tableau.append(formula[connective])
        if language.n_place(formula[connective]) == 1:
            print("(it's a one-place)")
            tableau.append(make_tableau(language, formula[1:]))
        elif language.n_place(formula[connective]) == 2:
            print("(it's a two-place)")
            tableau.append(make_tableau(language, formula[:connective]))
            tableau.append(make_tableau(language, formula[connective + 1:]))
    return tableau
            


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

class modal_operator:
    """l
    A modal operator has some arity (correspoding to the arity of a
    relation in a structure), a symbol and optionally a symbol for its
    dual (if no dual, initialize with None).
    """
    
    def __init__(self, symbol, dual, arity):
        self.symbol = symbol
        self.dual = dual
        self.arity = arity

    def __repr__(self):
        return ('modal_operator(' + '"' + str(symbol) + '"' +  ', ' + 
                '"' + str(dual) + '"' + ', ' + str(arity) + ')')

class language:
    """
    A language consists of:
    - a set of propositions (one character strings)
    - a set of logical constants
    - a set of modal operators
    - a dictionary from symbols to their objects
    """
    def __init__(self, propositions, constants, modal_operators):
        self.P = propositions
        self.C = constants
        self.O = modal_operators
        self.lexicon = dict( list({p:p for p in self.P}.items()) +
                             list({c.symbol:c for c in self.C}.items()) +
                             list({o.symbol:o for o in self.O}.items())
                           ) 

    def n_place(self, symbol):
        """
        Returns the number of places of an operator or logical constant (or
        0 for a proposition)
        """
        if self.lexicon[symbol] in self.P: 
            return 0
        if self.lexicon[symbol] in self.C:
            return self.lexicon[symbol].place
        if self.lexicon[symbol] in self.O:
            return 1
        else: return None

    def __repr__(self):
        return ('language' + '(' + str(self.P) + ', ' +
                str(self.C) + ', ' + str(self.O) + ')')
