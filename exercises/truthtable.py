from formula import Formula

class Truthtable:
    """
    t = Truthtable()
    t.atoms = {prop1, prop2, propq}
    t.values = [True, False, True, False, False, True, True, True]
       
    is a representation of the following truthtable:

      t.atoms | prop1 | prop2 | propq | t.values 
                False   False   False | True
                True    False   False | False
                False   True    False | True
                True    True    False | False
                False   False   True  | False
                True    False   True  | True
                False   True    True  | True
                True    True    True  | True
        
    Initialization schema:
        arg1 = values 
        arg2 = atoms
   
        arg1 = Formula
        arg2 = None
        (builds the truth table for the given formula)

        arg1 = Operator
        arg2 = None (or Operator.arity atoms)
        (builds the truth table for the given operator)
    """
    # TODO: __eq__ method for truth tables
    #       build truth tables from operators
    def __init__(self, arg1 = None, arg2 = None):
        self.atoms = None
        self.values = None

        if arg1 == None:
            if not arg2 == None:
                raise ValueError('needs first argument if seccond is supplied')
        else:
            if arg2 == None:
                if type(arg1) == Formula:
                    self.atoms = sorted(list(formula.atomics()))
                    self.values = self.__build_from_formula(arg1)
                elif type(arg1) == Operator:
                    
                else:
                    raise TypeError('truthtable can be build from Formula or \
                                     Operator')
            else:
                self.atoms = arg1
                self.values = arg2

    def __build_from_formula(self, f):
        import itertools
        valuetable = list(itertools.product([False, True], repeat=len(self.atoms)))
        atomvalues = [ { p:row[self.atoms.index(p)] for p in self.atoms } for row in valuetable ]
        return [ f.evaluate(values) for values in atomvalues ]

    def 


""" 
TESTING
"""

import random
from random_formula import generate_random_formula

from formula import L

f = Formula(L, "a->b") 
t = Truthtable(f)

print(f)
print(t.atoms)
print(t.values)
