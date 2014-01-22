def get_random_item(lst):
    from random import randint
    return lst[randint(0, len(lst) - 1)]

def pop_random_item(lst):
    from random import randint
    return lst.pop(randint(0, len(lst) - 1))
