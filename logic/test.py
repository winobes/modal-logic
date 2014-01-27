import prop, pred

# Perhaps it is a good idea to put every useful test in a separate function.
# Then we can just call the test function we are interested in and leave the
# rest untouched.

def cnf_testing():
    # CNF is faster than CNF_TT for random formulas of 13 or fewer atoms.
    # CNF reaches default maximum recursion depth (1000) at 25 atoms  
    # for formulas in DNF, the truth table method is faster starting at
    # 3 atoms.
    import time
    sigma = [prop.random_fml((15,16)) for i in range(1000)]
    sigma_dnf = [prop.dnf_tt(phi) for phi in sigma]

    start = time.time()
    for phi in sigma:
        g = prop.cnf(phi)
    end = time.time()
    print('Random to CNF   Time:', end - start)

    start = time.time()
    for phi in sigma:
        g = prop.cnf_tt(phi)
    end = time.time()
    print('Random to CNF_TT Time:', end - start)

    start = time.time()
    for phi in sigma_dnf:
        g = prop.cnf(phi)
    end = time.time()
    print('DNF to CNF   Time:', end - start)

    start = time.time()
    for phi in sigma_dnf:
        g = prop.cnf_tt(phi)
    end = time.time()
    print('DNF to CNF_TT Time:', end - start)


def print_test():
    fml_strs = {'(EyPx->Syzz)->Azx~Sxzz',
              '~(RxVAxQxzzVQyyy)&~ExQxxy',
               'AxQxzz',
              'PxV~AxRxy',
              'AxRxy',
              'Ax(Pxy&Px&Qyz)'}
    for fml_str in fml_strs:
        print(fml_str)
        print(pred.parse(fml_str),'\n')

def prop_prove_test():
    sigma = [prop.parse(psi) for psi in
            {'p -> (qVr)', '(~q&t) V (s->p)', '~(~r -> ~p)'}]
    phi = prop.parse('~sVq')
    for psi in sigma: print("  ",prop.fml_to_str(psi))
    print('|=', prop.fml_to_str(phi))
    return prop.proves(sigma, phi)

def eval_test():
    no_quant = {'AxyPx', 'AxRx', 'Axy(Px->Rxy)', 'Azy(Rxy->Py)'}
    asgmnt = {'x':'a', 'y':'b', 'z':'c'}
    intprt = {'P':{('a',),('b',)}, 'R':{('a','b'), ('b','c'), ('b','a')}}
    domain = {'a', 'b', 'c'}
    for fml_str in no_quant:
        fml = pred.parse(fml_str)
        print(pred.fml_to_str(fml))
        #print(pred.evaluate(fml, asgmnt, intprt))
        #print()
        print(pred.evaluate(fml, asgmnt, intprt, domain))

def eval_test2():
    domain = {'a', 'b', 'c'}
    asgmnt = {'x':'a', 'y':'b', 'z':'c'}
    intprt = {
        'P':{('a',), ('b',)},
        'Q':{('a',), ('b',), ('c',)},
        'R':{('a', 'b'), ('b', 'c'), ('b', 'a')},
        'S':{('a', 'a'), ('b', 'b'), ('c', 'c')}
    }

    for i in range(100):
        f = pred.random_fml((2, 4), {'P':1, 'Q':1, 'R':2, 'S':2})
        print(pred.fml_to_str(f))
        print(pred.evaluate(f, asgmnt, intprt, domain))
        print()

def random_bool():
    from random import randrange
    return (True, False)[randrange(0, 2)]

def test1():
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

def test2():
    for i in range(100):
        f = pred.random_fml((1, 10))
        print(f)
        print(pred.fml_to_str(f))
        print()

cnf_testing()
