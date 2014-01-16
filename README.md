Modal Logic
===========

We implement a Python class for basic Kripke frames and various methods to maniupulate them.

Some goals and todo's
---------------------
+ ~~debug make_tableau for one-place constants~~
+ ~~compute formula valuation at a word in a model~~
+ ~~generate submodel~~
+ ~~filtration (largest, smallest)~~
+ compute bisimularity of models/worlds at models
+ generate cannonical model from a set of formulas
	- determine consistency of formulas
	- create atoms from a set of formulas
+ ~~generate random frames~~
	- ~~Erdos Reyni random frames~~
+ display properties of a frame
	- transitive
	- symmetric (asymmetric, anti-symmetric)
	- reflexive
	- well-founded
	- tree
	- non-right branching
+ generate random frames for various modal logics (K, S4, S5, D, etc.)
+ compute modal equivalence
+ User interface
	- drawing of frames

notes
-----
+ Possible Tools for Drawing
    - Networkx: 
        1. Download the .egg file for your version of python [here] (https://pypi.python.org/pypi/networkx/). 
        2. Download easy_install
        3. Run `python3 -m easy_install networkx-x.x.x-pyx.x.egg` (be sure to us e the target version of python)
    - Matplotlib (dependency for drawing graphs with networkx, but also stand-alone):
        1. Download matplot lib from [here] (http://matplotlib.org/downloads.html).
        2. Unzip and enter the matplotlib directory
        3. Run `python3 setup.py build`
        4. Run `python3 setup.py install`
    - May want to use the [Ipython shell] (http://matplotlib.org/users/shell.html) for interactive graph drawing.
        - run Ipython in pylab mode `ipython3 --pylab`
    - Graphviz (matplotlib dependency, also stand-alone)
        1. install graphviz-dev
        2. Download pygraphviz from [here] (https://github.com/philipaxer/pygraphviz) (ported to python3).
        3. Run `python3 setup.py install` 
+ Consider pakaging with something like [this] (https://pypi.python.org/pypi/ncdistribute/).

