Modal Logic
===========

We implement a Python class for general Kripke frames with any number of n-ary modal operators and various methods to maniupulate them.

Some goals and todo's
---------------------
+ ~~debug make_tableau for one-place constants~~
+ ~~compute formula valuation at a word in a model~~
+ ~~generate submodel~~
+ unraveling
+ filtration (largest, smallest)
+ compute bisimularity of models/worlds at models
+ compute satisfaction of a formula by a frame
+ generate random frames
+ generate random frames for various modal logics (K, S4, S5, D, etc.)
+ compute modal equivalence
+ (graphical) drawing of frames

notes
-----
+ To install networkx: 
    1. Download the .egg file for your version of python [here] (https://pypi.python.org/pypi/networkx/). 
    2. Download easy_install
    3. Run `python3 -m easy_install networkx-x.x.x-pyx.x.egg` (be sure to us e the target version of python)
+ To install matplotlib (necessary for drawing graphs with networkx):
    1. Download matplot lib from [here] (http://matplotlib.org/downloads.html).
    2. Unzip and enter the matplotlib directory
    3. Run `python3 setup.py build`
    4. Run `python3 setup.py install`
+ May want to use the [Ipython shell] (http://matplotlib.org/users/shell.html) for interactive graph drawing.
    - run Ipython in pylab mode `ipython3 --pylab`
+ Running into problems with matplotlib and networkx... simpler may be to use graphviz (which I believe matplotlib actually uses)
    1. install graphviz-dev
    2. Download pygraphviz from [here] (https://github.com/philipaxer/pygraphviz).
    3. Run `python3 setup.py install` 
