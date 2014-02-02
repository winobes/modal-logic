import prop, pred

# Perhaps it is a good idea to put every useful test in a separate function.
# Then we can just call the test function we are interested in and leave the
# rest untouched.

def model_checking():
    fml_strs = [
                '~ExPx->Ax~Px',
                'Ax~Px->~ExPx',
                '~AxPx->Ex~Px',
                'Ex~Px->~AxPx',
                'Ax(Px&Qx)->(AxPx&AxQx)',
                '(Ax(Px->Qx)&ExPx)->ExQx'
                '(~Ex((Sx&Qx)&Px) & Ax(Sx->Qx) & Ax(Qx->Px)) -> ~ExSx'
                ]
              
    sigma = [pred.parse(phi) for phi in fml_strs]
    for phi in sigma:
        print(pred.fml_to_str(phi))
        print("Found countermodel:", pred.check_models(phi, 5, 1000))
        print() 

def random_model_checking():
    sigma = [pred.random_fml((1,5)) for i in range(1000)]
    i = 0
    for phi in sigma:
        if pred.check_models(phi, 3, 50) == None:
            print("Theorem:", pred.fml_to_str(phi))
            i += 1
    print("%", i/2, "theorems")

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
        'a':{():0},
        'b':{():1},
        'c':{():2},
        'd':{():0},
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

def test3():
    for i in range(10):
        f = pred.random_fml((1, 5))
        g = pred.skolemize(f)
        h = ('and', [('arrow', f, g), ('arrow', g, f)])
        print(pred.fml_to_str(f))
        print(pred.fml_to_str(pred.skolemize(f)))
        a = pred.check_models(h, 10, 1000)
        #if not a == None:
            #print(a)
            #print(f)
        #print()
#
def test4():
    f = ('exists', {'y'}, ('R', ['y']))
    print(pred.fml_to_str(f))
    g = pred.skolemize(f)
    print(pred.fml_to_str(g))
    h = ('and', [('arrow', f, g), ('arrow', g, f)])
    print("intpretation:", pred.check_models(h, 2, 100)[0])
    print("assignment  :", pred.check_models(h, 2, 100)[1])
    
def test5():
    f = ('or', [
        ('exists', {'z','y'}, ('not', ('S', ['y', ('c',[]) ]))), 
        ('exists', {'z'}, ('Q', [(('g',['x','z'])), ('d', []), 'y']))
        ])    
    print(pred.fml_to_str(f))
    print(pred.fml_to_str(pred.skolemize(f)))

def test6():
    tests = [
        (['x'],                                   ['x']),
        (['x'],                                   ['y']),
        (['x'],                                   [('f', ['x'])]),
        (['x'],                                   [('f', ['y'])]),
        ([('f', ['x'])],                          ['y']),
        ([('f', ['x'])],                          [('g', ['y'])]),
        ([('f', ['x'])],                          [('f', ['y'])]),
        ([('f', ['x', 'y'])],                     [('f', ['y', 'z'])]),
        ([('f', ['x', ('g', ['z']), 'z'])],       [('f', [('g', ['y']), 'y', 'z'])]),
        ([('f', ['x', ('g', ['z']), ('a', [])])], [('f', [('g', ['y']), 'y', 'z'])]),
        ([('f', [('g', ['z']), ('a', [])])],      [('f', ['y', 'z'])]),
        ([('f', [('g', ['x']), 'x'])],            [('f', ['y', ('a', [])])]),
        (['x', ('a', [])],                        ['y', 'x'])
    ]

    for terms in tests:
        subst = pred.unify_termlists(terms[0], terms[1])
        print('term 1: ', pred.termlist_to_str(terms[0]))
        print('term 2: ', pred.termlist_to_str(terms[1]))
        print('subst:  ', pred.subst_to_str(subst))
        if subst != None:
            print('result: ', pred.termlist_to_str(pred.subst_termlist(subst, terms[0])))
        print()

def cnf_report_1(starting_atomics, dnf = False):
    # tests when cnf reaches Python's recursion limit (default 1000)
    # cnf reaches recursion limit at around 35-45 atoms
    # reaces limit at 4-5 atoms if they start in DNF 
    # could not find break point for cnf_tt
        n_atomics = starting_atomics 
        cnf_number = n_atomics 
        cnf_done = False
        while True:
            try:    
                f = prop.random_fml((n_atomics, n_atomics+1)) 
                if dnf: f = prop.dnf_tt(f)
                print(n_atomics)
                print('f:', prop.fml_to_str(f), '\n')
                h = prop.cnf_tt(f)
                if not cnf_done:
                    g = prop.cnf(f)
                    print('cnf:', prop.fml_to_str(g), '\n')
                print('cnf_tt:', prop.fml_to_str(h), '\n')
                print('\n-----------------------------------\n')
                n_atomics += 1
                if n_atomics >= 1000: break
            except RuntimeError:
                if cnf_done:
                    break
                cnf_done = True
                cnf_number = n_atomics
        print('Done.')
        print('cnf', cnf_number)
        print('cnf_tt', n_atomics)

def cnf_report_2(n_formulas, n_atomics, n_distinct_atoms, dnf = False):
    import time
    # measures the time it takes to convert n_formulas
    # to CNF
    sigma = [prop.random_fml((n_atomics, n_atomics+1), n_distinct_atoms) for i in range(n_formulas)]
    sigma_1 = [prop.dnf_tt(f) for f in sigma]
    if dnf: sigma = sigma_1

    time_cnf = time.time()
    for f in sigma:
        g = prop.cnf(f)
    time_cnf = time.time() - time_cnf

    time_cnf_tt = time.time()
    for f in sigma:
        g = prop.cnf_tt(f)
    time_cnf_tt = time.time() - time_cnf_tt

    return (time_cnf - time_cnf_tt)

def cnf_report_3():
    import sys
    import csv
    
    sys.setrecursionlimit(50000)
    report = [[cnf_report_2(50, tot_atoms+1, dif_atoms+1, dnf = True) for dif_atoms in range(10)] for tot_atoms in range(5)]

    print(report)

    with open('report.csv', 'w', newline='') as csvfile:
        reportwriter = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in report: reportwriter.writerow(row)

test6()
