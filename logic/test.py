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
    domain = {0, 1, 2}
    asgmnt = {'x':0, 'y':1, 'z':2}
    intprt = {
        'P':{(0,), (1,)},
        'Q':{(0,), (1,), (2,)},
        'R':{(0, 1), (1, 2), (2, 0)},
        'S':{(0, 0), (1, 1), (2, 2)},
        'a':0,
        'b':1,
        'c':2,
        'f':{(i,):0 for i in domain},
        'g':{(i,):i for i in domain},
        'h':{(i, j):i for i in domain for j in domain},
        'j':{(i, j):j for i in domain for j in domain}
    }

    arities = {'P':1, 'Q':1, 'R':2, 'S':2, 'f':1, 'g':1, 'h':2, 'j':2}

    print('domain:', domain)
    print('assignment:', asgmnt)
    print('interpretation:')
    for i in intprt:
        print('%s: %s' % (i, intprt[i]))
    print()

    for i in range(100):
        f = pred.random_fml((2, 4), arities)
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

eval_test2()
