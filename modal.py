class Relation:
    """
        Relations are encoded as sets of tuples of the same length
    where the length of the tuples corresponds to the arity (+1) of the
    modal operators in the intended modal language.
        In a basic modal logic with one unary modal operator for example,
    the set of relations contain a single set of pairs, where a pair
    indicates the relation between worlds.
    """
    def __init__(self, relation, arity=2):

        self.arity = arity
        if all((len(r) == arity for r in relation)):
            self.relation = {tuple(r) for r in relation} 
        else: raise ValueError("tuple does not match the arity")

    def copy(self):
        return self
   
    def __add__(self, other):
        if type(other) == type(self):
            if not other.arity == self.arity:
                raise ValueError("cannot add relations of different arities") 
            return Relation(self.relation | other.relation, self.arity)
        else: raise TypeError("unsupported operand type")


    def __repr__(self):
        return "Relation("  + str(self.relation) + ", " + str(self.arity) + ")"
    
    def __str__(self):
        relations_str = ""
        for r in self.relation: relations_str += str(r) + ", "
        return "{" + relations_str[:-2:] + "}" 


class Frame:
    """
    A frame has two parts:
    - a set of worlds (just lables)
    - a set of relations on those worlds
        It takes any interable full of world lables and either an iterable
    list of relations or a single relation. Relations between lables not in
    worlds are preserved.
    """
           
    def __init__(self, worlds, relations):
        self.W = worlds
        self.R = list(relations) # todo: allow entry of a set of tuples or a single relation

    def __add__(self, other):
        if type(other) == type(self):
            if len(self.R) == len(other.R) and all([a.arity == b.arity for (a,b) in zip(self.R, other.R)]):
                return Frame(self.W | other.W, [a+b for (a,b) in zip(self.R, other.R)])
            else: raise ValueError ("frames are not the same similarity type")
        else: raise TypeError ("unsupported operand type")

            

    def __repr__(self):
        return "Frame(" + str(self.W)+ ", " + str(self.R) +  ")"

    def __str__(self):
        Rs = ""
        for r in self.R:
            Rs = Rs + "R" + str(self.R.index(r)) + " = " + str(r.relation) + "\n"
        return "W = " + str(self.W) + "\n" + Rs 

class Model:
    """
    A model is a frame along with a valuation. Valuations are stripped
    of worlds that do not exist in the model.
    """

    def __init__(self, frame, valuation):
        self.F = frame
        self.V = {p:{w for w in valuation[p] if w in frame.W} 
                  for p in valuation}

    def __getitem__(self, p):
        assert (p[0] in self.F.W), "That world does not exist in this model."
        if p[1] == "":
            {q for q in self.V if p[0] in self.V[q]}
        else:
            if p[0] in self.V[p[1]]: return True
            else: return False

    def __str__(self):
        return str(self.F) + "V = " + str(self.V) + "\n"

