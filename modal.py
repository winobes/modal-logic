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
           
    def __init__(self):
        self.W = set()
        self.R = {}
        self.arity = {} 
        self.name = "F"

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

    def add_relation(self, name, arity):
        self.R[name] = set()
        self.arity[name] = arity

    def remove_relation(self, name):
        if name in self.R: 
            del self.R[name]
            del self.arity[name]

    def add_to_relation(self, name, relation):
        if len(relation) == self.arity[name]:
            for w in relation:
                if not w in self.W:
                    self.add_world(w)
            self.R[name].add(tuple(relation))
        else: raise ValueError("wrong arity for that relation")

    def remove_from_relation(self, name, relation):
        if relation in self.R[name]:
            self.R[name].remove(tuple(relation))

    def add_multiple_to_relation(self, name, relations):
        for r in relations: self.add_to_relation(name, r)
    
    def remove_multiple_from_relation(self, name, relations):
        for r in relations: self.remove_from_relation(name, r)

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

    def __init__(self, F = None):
        if F == None: super().__init__()
        else:
            self.W = F.W
            self.R = F.R
            self.arity = F.arity 
        self.name = "M"
        self.V = {}

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

