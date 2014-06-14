import prop, pred

import util

def benchmark_prover(prover, fmls):
    import cProfile
    cProfile.runctx('for f in fmls: prover(f)', globals(), locals())

def benchmark_provers(provers, fmls):
    for prover in provers:
        print('%s:\n' % prover.__name__)
        benchmark_prover(prover, fmls)

def test_prover(prover, fml_to_str, tests):
    for test in tests:
        fml = test[0]
        truthval = test[1]
        if prover(fml) == truthval:
            print('good:', fml_to_str(fml))
        else:
            print('fail:', fml_to_str(fml))

def test_provers(provers, fml_to_str, tests):
    for p in provers:
        print('%s:' % p.__name__)
        test_prover(p, fml_to_str, tests)
        print()

# Check if provers return the same result for every formula.
def compare_provers(provers, fml_to_str, fmls):
    results = dict()
    for f in fmls:
        for p in provers:
            results[p.__name__] = p(f)
        if any(results[p] != results[provers[0].__name__] for p in results):
            print('fail:', fml_to_str(f))
            for p in results:
                print('%s: %s' % (p, results[p]))
            print()

# Perhaps it is a good idea to put every useful test in a separate function.
# Then we can just call the test function we are interested in and leave the
# rest untouched.


# takes a container of forumlas sigma and a formula phi and checks if
# phi is entailed by sigma using the desired proof method 
def check_entailment(sigma, phi, proof_method, gdepth):
    f = ('arrow', ('and', list(sigma)), phi)
    # The tableaux proof method needs an additional argument.
    return proof_method(f, gdepth)


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
        f_cnf = prop.cnf(f)
        f_dnf = prop.dnf(f)
        print('formula:         ', prop.fml_to_str(f))
        print('cnf:             ', prop.fml_to_str(f_cnf))
        print('dnf:             ', prop.fml_to_str(f_dnf))
        print('random valuation:', prop.evaluate(f, val))
        print('contradiction:   ', prop.is_contr(f))
        print('validity:        ', prop.is_valid(f))
        print('cnf equivalent:  ', prop.are_equiv(f, f_cnf))
        print('dnf equivalent:  ', prop.are_equiv(f, f_dnf))
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

def test_unification():
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

def run_resolve(sigma):
    for f in sigma:
        prop.resolve(f)

#res_test_sigma = [prop.cnf(prop.random_fml((1,8))) for i in range(10000)]
def test7():
    import timeit
    import cProfile

    print(cProfile.run('run_resolve(res_test_sigma)'))

def test_prop_tableaux():
    tests = [
        (prop.parse("pV~p"), True),
        (prop.parse("p->p"), True),
        # Fitting, p. 44 (fig. 3.2)
        (prop.parse("(p->(q->r))->((pVs)->((q->r)Vs))"), True),
        # Fitting, p. 46 (fig. 3.3) 
        (prop.parse("(p&(q->(rVs)))->(pVq)"), True),
        # Fitting, p. 46 (exc. 3.1.1)
        (prop.parse("((p->q)&(q->r))->~(~r&p)"), True),
        (prop.parse("(~p->q)->((p->q)->q)"), True),
        (prop.parse("((p->q)->p)->p"), True),
        (prop.parse("~(~(p&p)&p)"), True),
        (prop.parse("~~(~(pVq)V(pVq))"), True),
        (prop.parse("((((a->b)->(~c->~d))->c)->e)->((e->a)->(d->a))"), True)
    ]
    provers = [prop.tableau, prop.tableau_dnf, prop.resolve_cnf, prop.resolve]

    test_provers(provers, prop.fml_to_str, tests)

    fmls = [prop.random_fml((1, 17)) for i in range(1000)]
    compare_provers(provers, prop.fml_to_str, fmls)

def benchmark_prop_tableaux():
    provers = [prop.tableau, prop.tableau_dnf]
    nfmls = 200

    fmls = [prop.random_fml((16, 17)) for i in range(nfmls)]
    print('proving random formulas')
    print('-----------------------\n')
    benchmark_provers(provers, fmls)

    f = prop.random_fml((16, 17))
    fmls = [('or', [f, ('not', f)]) for i in range(nfmls)]
    print('proving a complex f V ~f')
    print('------------------------\n')
    benchmark_provers(provers, fmls)

def test_pred_tableaux():
    sigma = [pred.random_fml((2, 4)) for i in range(1000)]
    for f in sigma:
        print(pred.fml_to_str(f))
        print(pred.tableau(f))
        print()

def preds_random():
    for i in range(1000000):
        sigma = pred.random_fml_list(
                {'P':1, 'Q':1, 'R':2},
                {},
                set(),
                (3,5), (3,5)
            )

        n = 1
        for phi in sigma[1:]:
            print(n, pred.fml_to_str(phi))
            n += 1
        print('|-', pred.fml_to_str(sigma[0]))
        if pred.tableau(('arrow', ('and', sigma[1:]), sigma[0])):
            print("theorem")
            break;
        print()

def axioms():
    irr = ('all', {'x'}, ('not', ('R', ['x', 'x'])))
    ref = ('all', {'x'}, ('R', ['x', 'x']))
    asym = ('all', {'x', 'y'}, ('arrow', ('R', ['x','y']), ('not', ('R', ['y', 'x']))))
    sym = ('all', {'x', 'y'}, ('arrow', ('R', ['x','y']), ('R', ['y', 'x'])))
    tr = ('all', {'x', 'y', 'z'}, ('arrow', ('and', [('R', ['x','y']), ('R', ['y', 'z'])]), ('R', ['x','z'])))
    con = ('all', {'x', 'y'}, ('or', [('R', ['x','y']), ('R', ['y','x'])]))
    io = ('all', {'x0','x1','x2','x3'}, ('arrow', ('and', [('R', ['x0','x1']), ('R', ['x2','x3'])]), ('or', [('R', ['x0','x3']), ('R', ['x2','x1'])])))
    ser = ('all', {'x'}, ('exists', {'y'}, ('R', ['x','y']))) 
    smtr = ('all', {'x0','x1','x2','x3'}, ('arrow', ('and', [('R', ['x0','x1']), ('R', ['x1','x2'])]), ('or', [('R', ['x1', 'x3']), ('R', ['x3', 'x2'])])))
    # s1 is tautological
    # s2 is the same as irreflexive
    s3 = ('all', {'x0','x1','x2','x3'}, ('arrow', ('and', [('R', ['x0','x1']), ('not', ('R',['x1','x2'])), ('not', ('R', ['x2','x1'])), ('R', ['x2','x3'])]), ('R', ['x0','x3'])))
    s4 = ('all', {'x0','x1','x2','x3'}, ('arrow', ('and', [('R', ['x0','x1']), ('R',['x1','x2']), ('not', ('R', ['x1','x3'])), ('not', ('R', ['x3','x1']))]), ('or', [('R', ['x0','x3']), ('R', ['x3','x0']), ('R', ['x2','x3']), ('R', ['x3','x2'])])))

    axioms = {
        'irreflexive': irr,
        'reflexive': ref,
        'asymmetric': asym,
        'symmetric': sym,
        'transitive': tr,
        'connected': con,
        'interval': io,
        'serial': ser,
        'semi-transitive': smtr,
        's3': s3,
        's4': s4
    }

    return axioms


def theories():

    a = axioms()

    spo = [a['irreflexive'], a['transitive']]
    sto = spo + [a['connected']]
    io = [a['irreflexive'], a['interval']]
    pro = [a['reflexive'], a['transitive']]
    seo1 = [a['irreflexive'], a['interval'], a['semi-transitive']]
    seo2 = [a['irreflexive'], a['s3'], a['s4']] # see R.v. Rooij Notes on Orders and Measurements

    theories = {
        'Strict Partial Order': spo,
        'Strict Total Order': sto,
        'Interval Order':  io,
        'Pre-order': pro,
        'Semi-order1': seo1,
        'Semi-order2': seo2
    }
    return theories
    

def print_theories():
    for theory in theories():
        print(theory)
        n = 0
        for axiom in theories()[theory]:
            n += 1
            print('\t', n, pred.fml_to_str(axiom))
        print()

def test8():
    phi = ('all', {'x', 'y', 'z'}, ('arrow', ('and', [('R', ['x','y']), ('R', ['y', 'z'])]),
                                        ('not', ('R', ['z', 'x']))))
    print(check_entailment(theories()['Strict Partial Order'], phi, pred.tableau, 1))

def totp_exercises():
    a = axioms()
    t = theories()

    print_theories()

    print('transitive, symmetric, serial |- reflexive')
    print(check_entailment([a['transitive'], a['symmetric'], a['serial']], a['reflexive'], pred.tableau, 1))
    print()

    print('Strict Partial Order |- asymmetric')
    print(check_entailment(t['Strict Partial Order'], a['asymmetric'], pred.tableau, 1))
    print()

    print('asymmetric |- irreflexive')
    print(check_entailment([a['asymmetric']], a['irreflexive'], pred.tableau, 1))
    print()

    print('Semi-order 1 |- Semi-order 2')
    print(check_entailment(t['Semi-order1'], ('and', t['Semi-order2']), pred.tableau, 2))
    print('Semi-order 2 |- Semi-order 1')
    print(check_entailment(t['Semi-order2'], ('and', t['Semi-order1']), pred.tableau, 2))
    print()

def test_pred_tableaux_2():
    fmls = [
        #
        # From the Fitting book
        #

        # Figure 6.1 (p. 138)
        ('arrow',
            ('all', {'x'},
                ('or', [
                    ('P', ['x']),
                    ('Q', ['x'])])),
            ('or', [
                ('exists', {'x'}, ('P', ['x'])),
                ('all', {'x'}, ('Q', ['x']))])),

        # Exercise 6.1.1 (pp. 139-140) (not all are theorems)
        ('arrow',
            ('exists', {'x'},
                ('all', {'y'},
                    ('R', ['x', 'y']))),
            ('all', {'y'},
                ('exists', 'x',
                    ('R', ['x', 'y'])))),
        ('arrow',
            ('all', {'x'},
                ('exists', {'y'},
                    ('R', ['x', 'y']))),
            ('exists', {'y'},
                ('all', 'x',
                    ('R', ['x', 'y'])))),
        ('exists', {'x'},
            ('arrow',
                ('P', ['x']),
                ('all', {'x'}, ('P', ['x'])))),
        ('arrow',
            ('exists', {'x'},
                ('or', [
                    ('P', ['x']),
                    ('Q', ['x'])])),
            ('or', [
                ('exists', {'x'}, ('P', ['x'])),
                ('exists', {'x'}, ('Q', ['x']))])),
        ('arrow',
            ('exists', {'x'},
                ('and', [
                    ('P', ['x']),
                    ('Q', ['x'])])),
            ('and', [
                ('exists', {'x'}, ('P', ['x'])),
                ('exists', {'x'}, ('Q', ['x']))])),
        ('arrow',
            ('and', [
                ('exists', {'x'}, ('P', ['x'])),
                ('all', {'x'}, ('Q', ['x']))]),
            ('exists', {'x'}, ('and', [('P', ['x']), ('Q', ['x'])]))),
        ('all', {'x'},
            ('exists', {'y'},
                ('all', {'z'},
                    ('exists', {'w'},
                        ('or', [
                            ('R', ['x', 'y']),
                            ('not', ('R', ['w', 'z']))]))))),
        ('arrow',
            ('all', {'x'}, ('Q', ['x'])),
            ('exists', {'x'},
                ('all', {'y'},
                    ('or', [
                        ('not', ('P', ['y'])),
                        ('and', [
                            ('P', ['x']),
                            ('Q', ['x'])
                        ])])))),

        # Exercise 6.1.2 (p. 140)
        ('arrow',
            ('and', [
                ('all', {'x', 'y', 'z'},
                    ('arrow',
                        ('and', [
                            ('R', ['x', 'y']),
                            ('R', ['y', 'z'])]),
                        ('R', ['x', 'z']))),
                ('all', {'x', 'y'},
                    ('arrow',
                        ('R', ['x', 'y']),
                        ('R', ['y', 'x']))),
                ('all', {'x'}, ('exists', {'y'}, ('R', ['x', 'y'])))
            ]),
            ('all', {'x'}, ('R', ['x', 'x']))),

        # Exercise 6.1.3 (p. 140)
        ('exists', {'x'},
            ('all', {'y'},
                ('all', {'z'},
                    ('arrow',
                        ('arrow',
                            ('P', ['y']),
                            ('Q', ['z'])),
                        ('arrow',
                            ('P', ['x']),
                            ('Q', ['x'])))))),
        ('exists', {'x'},
            ('all', {'y'},
                ('all', {'z'},
                    ('arrow',
                        ('or', [
                            ('P', ['y']),
                            ('Q', ['z'])]),
                        ('or', [
                            ('P', ['x']),
                            ('Q', ['x'])]))))),
        ('exists', {'x'},
            ('all', {'y'},
                ('all', {'z'},
                    ('all', {'w'},
                        ('arrow',
                            ('or', [
                                ('P', ['y']),
                                ('Q', ['z']),
                                ('R', ['w'])]),
                            ('or', [
                                ('P', ['x']),
                                ('Q', ['x']),
                                ('R', ['x'])])))))),

        # Example (p. 141)
        ('arrow',
            ('all', {'x'},
                ('or', [
                    ('P', ['x']),
                    ('Q', ['x'])])),
            ('or', [
                ('exists', {'x'}, ('P', ['x'])),
                ('all',    {'x'}, ('Q', ['x']))])),

        # Exercise 7.4.1 (p. 169)
        ('arrow',
            ('exists', {'x'}, ('all',    {'y'}, ('R', ['x', 'y']))),
            ('all',    {'y'}, ('exists', {'x'}, ('R', ['x', 'y'])))),
        ('exists', {'x'},
            ('arrow',
                ('P', ['x']),
                ('all', {'x'}, ('P', ['x'])))),
        ('arrow',
            ('all', {'x'},
                ('all', {'y'},
                    ('and', [
                        ('P', ['x']),
                        ('P', ['y'])]))),
            ('exists', {'x'},
                ('exists', {'y'},
                    ('or', [
                        ('P', ['x']),
                        ('P', ['y'])])))),
        ('arrow',
            ('all', {'x'},
                ('all', {'y'},
                    ('and', [
                        ('P', ['x']),
                        ('P', ['y'])]))),
            ('all', {'x'},
                ('all', {'y'},
                    ('or', [
                        ('P', ['x']),
                        ('P', ['y'])])))),
        ('all', {'x'},
            ('exists', {'y'},
                ('all', {'z'},
                    ('exists', {'w'},
                        ('or', [
                            ('R', ['x', 'y']),
                            ('not', ('R', ['w', 'z']))]))))),

        # Example (p. 184)
        ('arrow',
            ('exists', {'w'},
                ('all', {'x'},
                    ('R', ['x', 'w', ('f', ['x', 'w'])]))),
            ('exists', {'w'},
                ('all', {'x'},
                    ('exists', {'y'},
                        ('R', ['x', 'w', 'y']))))),

        #
        # Other tests
        #

        # Reflexitivity, symmetry, transitivitiy.
        ('all', {'x'}, ('R', ['x', 'x'])),
        ('all', {'x', 'y'}, ('arrow', ('R', ['x', 'y']), ('R', ['y', 'x']))),
        ('all', {'x', 'y', 'z'},
            ('arrow',
                ('and', [('R', ['x', 'y']), ('R', ['y', 'z'])]),
                ('R', ['x', 'z']))),

        ('arrow',
            ('all', {'x'}, ('or', [('P', ['x']), ('Q', ['x'])])),
            ('or', [('all', {'x'}, ('P', ['x'])), ('all', {'x'}, ('Q', ['x']))])
        )
    ]


    for f in fmls:
        print(pred.fml_to_str(f))
        print(pred.tableau(f, 16))
        print()

# http://www.cs.miami.edu/~tptp/cgi-bin/SeeTPTP?Category=Problems&Domain=PUZ&File=PUZ031+2.p
#
# In order for this to work, the pred() function needs to be adapted: change the line
#   return f[0] in 'PQRS'
# to
#   return f[0][0] in 'PQRS'
def schubert_steamroller():
    wolf_type         = ('exists', {'x'}, ('Pwolf',         ['x']))
    fox_type          = ('exists', {'x'}, ('Pfox',          ['x']))
    bird_type         = ('exists', {'x'}, ('Pbird',         ['x']))
    caterpillar_type  = ('exists', {'x'}, ('Pcaterpillar',  ['x']))
    snail_type        = ('exists', {'x'}, ('Psnail',        ['x']))

    pel47_1_1 = ('all', {'x'}, ('arrow', ('Pwolf',        ['x']), ('Panimal', ['x'])))
    pel47_2_1 = ('all', {'x'}, ('arrow', ('Pfox',         ['x']), ('Panimal', ['x'])))
    pel47_3_1 = ('all', {'x'}, ('arrow', ('Pbird',        ['x']), ('Panimal', ['x'])))
    pel47_4_1 = ('all', {'x'}, ('arrow', ('Pcaterpillar', ['x']), ('Panimal', ['x'])))
    pel47_4_2 = ('all', {'x'}, ('arrow', ('Psnail',       ['x']), ('Panimal', ['x'])))

    grain_type = ('exists', {'x'}, ('Pgrain', ['x']))

    pel47_7 = ('all', {'x'},
        ('arrow',
            ('Panimal', ['x']),
            ('or', [
                ('all', {'y'},  ('arrow', ('Pplant', ['y']), ('Peats', ['x', 'y']))),
                ('all', {'y1'},
                    ('arrow',
                        ('and', [
                            ('Panimal', ['y1']),
                            ('Pmuch_smaller', ['y1', 'x']),
                            ('exists', {'z'}, ('and', [('Pplant', ['z']), ('Peats', ['y1', 'z'])]))
                        ]),
                        ('Peats', ['x', 'y1'])
                    )
                )
            ])
        )
    )

    pel47_8 = ('all', {'x', 'y'},
        ('arrow',
            ('and', [('Pbird', ['y']), ('Psnail', ['x'])]),
            ('Pmuch_smaller', ['x', 'y'])
        )
    )

    pel47_8a = ('all', {'x', 'y'},
        ('arrow',
            ('and', [('Pbird', ['y'], ('Pcaterpillar', ['x']))]),
            ('Pmuch_smaller', ['x', 'y'])
        )
    )

    pel47_9 = ('all', {'x', 'y'},
        ('arrow',
            ('and', [('Pbird', ['x'], ('Pwolf', ['y']))]),
            ('Pmuch_smaller', ['x', 'y'])
        )
    )

    pel47_10 = ('all', {'x', 'y'},
        ('arrow',
            ('and', [('Pfox', ['x'], ('Pwolf', ['y']))]),
            ('Pmuch_smaller', ['x', 'y'])
        )
    )

    pel47_11 = ('all', {'x', 'y'},
        ('arrow',
            ('and', [('Pwolf', ['x'], ('Pfox', ['y']))]),
            ('not', ('Peats', ['x', 'y']))
        )
    )

    pel47_11a = ('all', {'x', 'y'},
        ('arrow',
            ('and', [('Pwolf', ['x'], ('Pgrain', ['y']))]),
            ('not', ('Peats', ['x', 'y']))
        )
    )

    pel47_12 = ('all', {'x', 'y'},
        ('arrow',
            ('and', [('Pbird', ['x'], ('Pcaterpillar', ['y']))]),
            ('Peats', ['x', 'y'])
        )
    )

    pel47_13 = ('all', {'x', 'y'},
        ('arrow',
            ('and', [('Pbird', ['x'], ('Psnail', ['y']))]),
            ('not', ('Peats', ['x', 'y']))
        )
    )

    pel47_14 = ('all', {'x'},
        ('arrow',
            ('Pcaterpillar', ['x']),
            ('exists', {'y'},
                ('and', [
                    ('Pplant', ['y']),
                    ('Peats', ['x', 'y'])
                ])
            )
        )
    )

    pel47_14a = ('all', {'x'},
        ('arrow',
            ('Psnail', ['x']),
            ('exists', {'y'},
                ('and', [
                    ('Pplant', ['y']),
                    ('Peats', ['x', 'y'])
                ])
            )
        )
    )

    conjecture = ('exists', {'x', 'y'},
        ('and', [
            ('Panimal', ['x']),
            ('Panimal', ['y']),
            ('exists', {'z'},
                ('and', [
                    ('Pgrain', ['z']),
                    ('Peats', ['y', 'z']),
                    ('Peats', ['x', 'y'])
                ])
            )
        ])
    )

    premises = [wolf_type, fox_type, bird_type, caterpillar_type, snail_type,
        pel47_1_1, pel47_2_1, pel47_3_1, pel47_4_1, pel47_4_2, grain_type,
        pel47_7, pel47_8, pel47_8a, pel47_9, pel47_10, pel47_11, pel47_11a,
        pel47_12, pel47_13, pel47_14, pel47_14a]

    fml = ('arrow', ('and', premises), conjecture)

    for f in premises:
        print(pred.fml_to_str(f))
    print(pred.fml_to_str(conjecture))

    print()
    print(pred.tableau(fml, 0))

def demonstrate_bug():
    a = axioms()

    print('transitive, symmetric, serial |- reflexive')
    for gdepth in range(22):
        print('Attempting proof with gdepth', gdepth, ':')
        print(check_entailment([a['transitive'], a['symmetric'], a['serial']], a['reflexive'], pred.tableau, gdepth))
        print()


util.debug = 0

demonstrate_bug()


