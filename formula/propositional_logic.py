from formula import Operator, Formula, Language
import itertools

L = Language(
    {
    "falsum": Operator('F', '\u22a5', lambda: False, 0),
    "and"   : Operator('&', '\u2227', lambda x, y: x and y, 2), 
    "or"    : Operator('|', '\u2228', lambda x, y: x or y, 2),
    "arrow" : Operator('->', '\u2192', lambda x, y: not x or y, 2),    
    "not"   : Operator('~', '\u00ac', lambda x: not x,      1)
    }, None, 'ascii')

def remove_arrows(f):
    """
    Transform implication subformulas into or subformulas.
    """

    if f.depth() == 0:
        return f
    elif not f.operator() == L['arrow']:
        return L.build(f.operator(), *[remove_arrows(f[i+1]) for i in range(len(f)-1) ])
    else: # remove the arrow
        return L.build('or', L.build('not', remove_arrows(f[1])), remove_arrows(f[2]))

def negation_normal_form(f):
    f = remove_arrows(f)

    if f.is_atomic():
        return f
    elif f.operator() == L['not']:
        if f[1].is_atomic():
            return f
        elif f[1].operator() == L['not']:
            return negation_normal_form(f[1][1])
        else:
            if f[1].operator() == L['and']:
                return L.build('or',
                    negation_normal_form(L.build('not', f[1][1])),
                    negation_normal_form(L.build('not', f[1][2])))
            elif f[1].operator() == L['or']:
                return L.build('and',
                    negation_normal_form(L.build('not', f[1][1])),
                    negation_normal_form(L.build('not', f[1][2])))
            else:
                raise ValueError('unexpected operator:', f[1].operator())
    else:
        return L.build(f.operator(), negation_normal_form(f[1]),
            negation_normal_form(f[2]))

def conjunctive_normal_form(f):
    f = negation_normal_form(f)

    if f.is_atomic() or f.operator() == L['not']:
        return f
    elif f.operator() == L['and']:
        return L.build('and',
            conjunctive_normal_form(f[1]),
            conjunctive_normal_form(f[2]))
    else:
        # (A and B) or C
        if f[1].operator() == L['and']:
            return conjunctive_normal_form(L.build('and',
                L.build('or', f[1][1], f[2]),
                L.build('or', f[1][2], f[2])))
        # A or (B and C)
        elif f[2].operator() == L['and']:
            return conjunctive_normal_form(L.build('and',
                L.build('or', f[1], f[2][1]),
                L.build('or', f[1], f[2][2])))
        else:
            # TODO: Needs a more elegant solution.
            f1 = conjunctive_normal_form(f[1])
            f2 = conjunctive_normal_form(f[2])
            if f[1] == f1 and f[2] == f2:
                return L.build('or', f[1], f[2])
            else:
                return conjunctive_normal_form(L.build('or', f1, f2))

def list_conjuncts(f):
    """
    Return a list of the conjuncts of f, where f is assumed to be in
    conjunctive normal form.
    """

    if f.operator() == L['and']:
        return list_conjuncts(f[1]) + list_conjuncts(f[2])
    else:
        return [f]

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
        
    Initialization schemes:
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

def look_at_formula(Formula):
    t = Truthtable(Formula)
    if all(t.values):
        print("Tautology")
    elif any(t.values):
        print("Satisfiable")
    else:
        print("Contradiction")
