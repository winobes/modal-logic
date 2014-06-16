debug = 0

def dprint(*args):
    if debug:
        print(*args)

def get_random_item(lst):
    from random import randrange
    return lst[randrange(len(lst))]

def pop_random_item(lst):
    from random import randrange
    return lst.pop(randrange(len(lst)))

# Based on http://stackoverflow.com/a/480227.
def prune_list(lst):
    seen = set()
    return [x for x in lst if x not in seen and not seen.add(x)]
