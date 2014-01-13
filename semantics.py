from structure import Model
from syntax import Language

def evaluate(M, w, form):

    if   form[0] == '\u2227': # wedge
        return (evaluate(M, w, form[1]) or
               evaluate(M, w, form[2]))

    elif form[0] == '\u2228': # vee
        return (evaluate(M, w, form[1]) and 
               evaluate(M, w, form[2]))

    elif form[0] == '\u2192': # arrow 
        return (not evaluate(M, w, form[1]) or 
               evaluate(M, w, form[2]))

    elif form[0] == '\u00AC': # lnot 
        return not evaluate(M, w, form[1])

    elif form[0] == '\u25c7': # diamond
        if any([evaluate(M, v, form[1]) for v in M.W if (w,v) in M.R]):
            return True
        else:
            return False

    elif form[0] == '\u25fb': # diamond
        if all([evaluate(M, v, form[1]) for v in M.W if (w,v) in M.R]):
            return True
        else:
            return False

    elif form[0] == '\u22a5': # bottom
        return False

    else: # assume it's a proposition
        if w in M.V[form]:
            return True
        else:
            return False
