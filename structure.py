class Frame:
    """
    A frame has three parts:
    - a set of world lables (can be any hashable object)
    - a dictionary from relation names (should be strings) to arities
    - a dictionary from relation names to sets of n-tuples of world lables
      (where n is the arity of the relation)
    It may be a good idea to use the associated modal operator as the name
    for the relation.
    """
           
    def __init__(self, name = 'F', W = set(), R = {}, arity = {},):
        self.W = W 
        self.R = R 
        self.arity = arity 
        self.name = name 

    def set_name(self, name):
        if type(name) == str:
            self.name = name
        else:
            raise TypeError("the name of a structure must be a string")

    def add_world(self, w):
        self.W.add(w)

    def remove_world(self, w):
        if w in self.w:
            self.W.remove(w)

    def add_multiple_worlds(self, worlds):
        for w in worlds: self.add_world(w)

    def remove_multiple_worlds(self, worlds):
        for w in worlds: self.remove_world(w)

    def add_relation(self, operator, arity):
        self.R[operator] = set()
        self.arity[operator] = arity

    def remove_relation(self, name):
        if name in self.R: 
            del self.R[name]
            del self.arity[name]

    def add_to_relation(self, operator, relation):
        if len(relation) == self.arity[operator]:
            for w in relation:
                if not w in self.W:
                    self.add_world(w)
            self.R[operator].add(tuple(relation))
        else: raise ValueError("wrong arity for that relation")

    def remove_from_relation(self, operator, relation):
        if relation in self.R[name]:
            self.R[operator].remove(tuple(relation))

    def add_multiple_to_relation(self, operator, relations):
        for r in relations: self.add_to_relation(operator, r)
    
    def remove_multiple_from_relation(self, operator, relations):
        for r in relations: self.remove_from_relation(operator, r)

    def __repr__(self):
        return ('Frame(' + repr(self.name) + ', ' + str(self.W) + ', ' +
                str(self.R) + ', ' + str(self.arity) + ')')

    def __str__(self):
        relation_names = ''
        for r in self.R: relation_names += str(r) + ', '
        description = self.name + ' = (W, (' + relation_names[:-2:] + '))'
        relations = ''
        for r in self.R: relations += str(r) + ' = ' + str(self.R[r]) + '\n'
        return (description + '\n' + 'W = ' + str(self.W) + '\n' + relations)

class Model(Frame):
    """
    A model is a frame along with a valuation. A valuation is a dictionary
    from propositions to a set of worlds. A proposition can be any hashable
    object. 
    """

    def __init__(self, name = 'M', F = Frame('', set(), {}, {}), V = {}):
        super().__init__(name, F.W, F.R, F.arity)
        self.name = name 
        self.V = {}

    def remove_world(self, w):
        super().remove_world(w)
        for p in self.V:
            if w in V[p]: V[p].remove(w)

    def add_proposition(self, p):
        if not p in self.V:
            self.V[p] = set()

    def remove_proposition(self, p):
        if p in self.V:
            del self.V[p]

    def add_to_valuation(self, p, worlds):
        if not p in self.V:
            self.add_proposition(p)
        for w in worlds: 
            if w not in self.W:
                self.add_wold(w)
            self.V[p].add(w)

    def remove_from_valuation(self, p, worlds):
        if p in self.V:
            for w in worlds:
                if w in self.V[p]:
                    self.V[p].remove(w)

    def __str__(self):
        relation_names = ''
        for r in self.R: relation_names += str(r) + ', '
        description = self.name + ' = (W, (' + relation_names[:-2:] + '), V)'
        relations = ''
        for r in self.R: relations += str(r) + ' = ' + str(self.R[r]) + '\n'
        return (description + '\n' + 'W = ' + str(self.W) + '\n' + relations + "V = " + str(self.V) + "\n")

