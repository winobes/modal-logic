from structure import Model
from syntax import Language

default_unicode = {
                   '\u22A5':  False,                 # bottom
                   '\u00AC': {(True): False,         # not 
                              (False): True},  
                   '\u2227': {(True, True): True,    # wedge    
                              (True, False): False,
                              (False, True): False, 
                              (False, False): False},
                   '\u2228': {(True, True): True,    # vee 
                              (True, False): True,
                              (False, True): True, 
                              (False, False): False},
                   '\u2192': {(True, True): True,    # arrow 
                              (True, False): False,
                              (False, True): True, 
                              (False, False): True}
                  }

 
default_ascii = {
                   'F':   False,                 # bottom
                   '~': {(True): False,                 # not 
                         (False): True},
                   '&': {(True, True): True,            # wedge    
                         (True, False): False,
                         (False, True): False, 
                         (False, False): False},
                   'V': {(True, True): True,            # vee 
                         (True, False): True,
                         (False, True): True, 
                         (False, False): False},
                   '>': {(True, True): True,            # arrow 
                         (True, False): False,
                         (False, True): True, 
                         (False, False): True}
                  }

class Language:
    """
    A basic modal language consists of:
    - a set of propositions (one character strings)
    - a list of sets of constants (list position is arity) 
    - a modal operator and it's dual (a pair)
    - a a set of pairs of opening and closing brackets 
    """
    def __init__(self, prop = None, 
                       constants = None, 
                       modality = None, 
                       brackets = None):
        if prop == None:
            prop = default_language[0]
        self.prop = prop

class Interpreted_Language(Language):
    """
    Adds an interpretation to the constants in a modal langugae. 
    For each constant, a dictionary from tuples of booleans to a boolean.
    """
    
    def __init__(self, L = None, I = {}):
        if L == None:
            L = super().__init__()
        self.truth_table = I 
       
def evaluate(M, w, form):

    if   form[0] == 'wedge': # wedge
        return (evaluate(M, w, form[1]) or
               evaluate(M, w, form[2]))

    elif form[0] == 'vee': # vee
        return (evaluate(M, w, form[1]) and 
               evaluate(M, w, form[2]))

    elif form[0] == 'arrow': # arrow 
        return (not evaluate(M, w, form[1]) or 
               evaluate(M, w, form[2]))

    elif form[0] == 'not': # not 
        return not evaluate(M, w, form[1])

    elif form[0] == 'diamond': # diamond
        if any([evaluate(M, v, form[1]) for v in M.W if (w,v) in M.R]):
            return True
        else:
            return False

    elif form[0] == 'box': # box
        if all([evaluate(M, v, form[1]) for v in M.W if (w,v) in M.R]):
            return True
        else:
            return False

    elif form[0] == 'bottom': # bottom
        return False

    else: # assume it's a proposition
        if len(form) > 1:
            print("evaluating", form)
            raise ValueError("expected a proposition")
        if w in M[form]:
            return True
        else:
            return False
