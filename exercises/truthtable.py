class Truthtable:
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
            return valuation[formula[0]]
        elif formula[0] == 'not':
            return not self._evaluate(formula[1], valuation)
        elif formula[0] == 'and':
            return self._evaluate(formula[1], valuation) and self._evaluate(formula[2], valuation)
        elif formula[0] == 'or':
            return self._evaluate(formula[1], valuation) or self._evaluate(formula[2], valuation)
        elif formula[0] == 'arrow':
            return (not self._evaluate(formula[1], valuation)) or self._evaluate(formula[2], valuation)

    def _get_atoms(self, formula):
        if len(formula) == 1:
            return set(formula[0])
        elif len(formula) == 2:
            return self._get_atoms(formula[1])
        else:
            return self._get_atoms(formula[1]) | self._get_atoms(formula[2])

    def build(self, formula):
        import itertools

        self.atoms = sorted(list(self._get_atoms(formula)))
        valuetable = list(itertools.product([False, True], repeat=len(self.atoms)))
        atomvalues = [ { p:row[self.atoms.index(p)] for p in self.atoms } for row in valuetable ]
        print(atomvalues)
        self.values = [ self._evaluate(formula, values) for values in atomvalues ]

import random
from random_formula import generate_random_formula

f = generate_random_formula((2, 4))
t = Truthtable(f)

print(f)
print(t.atoms)
print(t.values)
