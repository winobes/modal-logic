import random

class Frame:
    """
    A frame has three parts:
    - W, a set of worlds (worlds can be any hashable object)
    - R, a binary relation on W (a set of two-tuples of elemest of W)
    for the relation.
    """
           
    def __init__(self, W = None, R = None):
        self.W = set()
        if not W == None:
            self.add_worlds(W)
        self.R = set()
        if not R == None:
            self.add_edges(R)

    def add_world(self, w):
        self.W.add(w)

    def remove_world(self, w):
        if w in self.w:
            self.W.remove(w)

    def add_worlds(self, worlds):
        for w in worlds: self.add_world(w)

    def remove_worlds(self, worlds):
        for w in worlds: self.remove_world(w)

    def add_edge(self, edge):
        if len(edge) == 2:
            for w in edge:
                if not w in self.W:
                    raise ValueError("edge contains an element not in W")
            self.R.add(tuple(edge))
        else: raise ValueError("wrong arity for that relation")

    def remove_edge(self, edge):
        if edge in self.R: 
            self.R.remove(tuple(edge))

    def add_edges(self, edges):
        for edge in edges: self.add_edge(edge)
    
    def remove_edges(self, edges):
        for edge in edges: self.remove_edge(edge)

    def __repr__(self):
        return ('Frame(' + str(self.W) + ', ' + str(self.R) + ')')

    def __str__(self):
        return 'W = ' +  str(self.W) + '\n' + 'R = ' + str(self.R)

class Model(Frame):
    """
    A model is a frame along with a valuation. A valuation is a dictionary
    from propositions to a set of worlds. A proposition can be any hashable
    object, but character strings are the obvious choice.
    """

    def __init__(self, F = Frame(set(), set()), V = None):
        super().__init__(F.W, F.R)
        self.V = {}
        if not V == None:
            for v in V.items(): self.add_to_valuation(v[0], v[1])

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
                self.add_world(w)
            self.V[p].add(w)

    def remove_from_valuation(self, p, worlds):
        if p in self.V:
            for w in worlds:
                if w in self.V[p]:
                    self.V[p].remove(w)

    def __getitem__(self, p):
        return self.V.get(p, set()) 

    def __repr__(self):
        return ('Model(' + 'Frame(' + str(self.W) + ', ' + str(self.R) + '), ' 
                + str(self.V) + ')')

    def __str__(self):
        return 'W = ' + str(self.W) + '\n' + 'R = ' + str(self.R) + '\n' + 'V = ' + str(self.V)

def generate_random_frame(W, pr):
    """
    Generates an Erdos-Reyni random frame from a list of worlds. Each 
    edge is formed with independent probability (pr).
    """
    if pr > 1 or pr < 0:
        raise ValueError("pr should be a probability between 0 and 1")

    F = Frame(W, None)  
 
    for edge in {(w,v) for w in W for v in W}:
        if random.uniform(0,1) < pr:
            F.add_edge(edge)
    return F 

def generate_submodel(M, w):
    """
    Returns a model containing only the worlds reachable from w.
    """
    N = Model(Frame({w}, None), None)

    while True:
        new_worlds = {wv[1] for wv in set().union(*[{(w,v) for v in M.W if (w,v) in M.R} for w in N.W])}
        if new_worlds <= N.W:
            break
        else:
            N.add_worlds(new_worlds)

    N.add_edges({(w,v) for w in N.W for v in N.W if (w,v) in M.R})
    N.V = {p:{w for w in M[p] if w in N.W} for p in M.V.keys()}

    return N
