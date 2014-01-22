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
    print(prop.evaluate(f, val))
    print(prop.cnf(f))
    print(prop.fml_to_str(prop.cnf(f)))
    print(prop.evaluate(prop.cnf(f), val))
    if prop.evaluate(f, val) != prop.evaluate(prop.cnf(f), val):
        print('*** incorrect CNF')
    print()
