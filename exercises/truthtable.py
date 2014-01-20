from formula import Formula, Operator, Language
import itertools

from formula import L
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
    def __init__(self, arg1 = None, arg2 = None):
        self.atoms = None
        self.values = None

        if arg2 == None:
            if type(arg1) == Formula:
                formula = arg1
                self.atoms = sorted(list(formula.atomics()))
            elif type(arg1) == Operator:
                if arg1.arity < len('pqrstuv'):
                    atom_names = [c for c in 'pqrstuv']
                else:
                    atom_names = ['p_' + str(n) for n in range(arg1.arity)]
                self.atoms = [L.build(name) for name in atom_names]
                formula = L.build(arg1, *self.atoms)
            else:
                raise TypeError('truthtable can only be built from Formula or \
                                 Operator')

            valuetable = list(itertools.product([False, True], 
                                        repeat=len(self.atoms)))
            atomvalues = [ {p:row[self.atoms.index(p)] for p in self.atoms } 
                           for row in valuetable ]
            self.values = [formula.evaluate(values) for values in atomvalues]
        else:
            self.atoms = arg1
            self.values = arg2

    def is_equal(self, other):
    # Assumes that self and other share all the same atomics.    
    # TODO handle the case where they don't
        return self.values == other.values
