def get_random_item(lst):
    from random import randrange
    return lst[randrange(len(lst))]

def pop_random_item(lst):
    from random import randrange
    return lst.pop(randrange(len(lst)))
