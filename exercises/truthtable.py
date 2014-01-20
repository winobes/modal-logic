class Truthtable:
    """
    May be initialized with atoms (arg2) and values (arg1)
    or simply a formula (arg1). If only a formula is supplied,
    the truth table is calculated from the possible
    values of its atomic forumlas.
    """
    # TODO: __eq__ method for truth tables
    #       build truth tables from operators
    def __init__(self, arg1 = None, arg2 = None):
        self.formula = None
        self.atoms = None
        self.values = None

        if arg1 == None:
            if not arg2 == None:
                raise ValueError('...')
        else:
            if arg2 == None:
                self.formula = arg1
                self.build(self.formula)
            else:
                self.atoms = arg1
                self.values = arg2

    def _evaluate(self, formula, valuation):
        if len(formula) == 1:
            return valuation[formula]
        else:
            return formula[0].truth_function(*[self._evaluate(sub, valuation) for sub in formula[1:]] )

    def build(self, f):
        import itertools

        self.atoms = sorted(list(f.atomics()))
        valuetable = list(itertools.product([False, True], repeat=len(self.atoms)))
        atomvalues = [ { p:row[self.atoms.index(p)] for p in self.atoms } for row in valuetable ]
        self.values = [ self._evaluate(f, values) for values in atomvalues ]


""" 
TESTING
"""

import random
from random_formula import generate_random_formula

from formula import L

f = generate_random_formula(L, (2, 4))
t = Truthtable(f)

print(f)
print(t.atoms)
print(t.values)


