class Frame:
    """
    A frame has two parts:
    - a set of world lables
    - a list of relations, each of which is a set of tuples (of the same length) of world lables 
    """
           
    def __init__(self, worlds, relations):
        self.W = worlds
        self.R = relations

    def arity(self, index=0):
        """
        Returns the arity of the requested relation
        """
        return len(next(iter(self.R[0])))

    def __add__(self, other):
        """
        Niave union of two  frames. Should probably be replaced with 
        a more useful operation like disjoint union.
        """
        if type(other) == type(self):
            if len(self.R) == len(other.R) and all([len(next(iter(a))) == len(next(iter(b))) for (a,b) in zip(self.R, other.R)]):
                return Frame(self.W | other.W, [a | b for (a,b) in zip(self.R, other.R)])
            else: raise ValueError ("frames are not the same similarity type")
        else: raise TypeError ("unsupported operand type")

    def __repr__(self):
        return "Frame(" + str(self.W)+ ", " + str(self.R) +  ")"

    def __str__(self):
        Rs = ""
        for r in self.R:
            Rs = Rs + "R" + str(self.R.index(r)) + " = " + str(r) + "\n"
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

