import prop

def random_bool():
    from random import randrange
    return (True, False)[randrange(0, 2)]

val = {
    'p':random_bool(),
    'q':random_bool(),
    'r':random_bool(),
    's':random_bool()
}

print(val)
print()

for i in range(100):
    f = prop.random_fml((3, 10))
    print(f)
    print(prop.fml_to_str(f))
    print(prop.cnf(f))
    print(prop.fml_to_str(prop.cnf(f)))
    print('random valuation:', prop.evaluate(f, val))
    print('contradiction:   ', prop.is_contr(f))
    print('validity:        ', prop.is_valid(f))
    print('cnf equivalent:  ', prop.are_equiv(f, prop.cnf(f)))
    print()
