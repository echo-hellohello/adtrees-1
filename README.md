# adtrees Python package

[![license shield][]](./LICENSE)
[![pypi package version][]](https://pypi.python.org/pypi/adtrees)
[![python supported shield][]](https://pypi.python.org/pypi/adtrees)

`adtrees` is a package facilitating usage of some methods for qualitative and quantitative evaluation of security using [attack trees](https://en.wikipedia.org/wiki/Attack_tree)
and [attack-defense trees](http://people.irisa.fr/Barbara.Kordy/papers/ADT12.pdf).

The package is intended to be used together with the [ADTool](https://satoss.uni.lu/members/piotr/adtool/), but this is not obligatory.

**Prerequisites**

Optimization problems on attack-defense trees are solved using *lp_solve*. For the installation of *lp_solve*, see [Using lpsolve from Python](http://lpsolve.sourceforge.net/5.5/Python.htm). General information on *lp_solve* can be found [here](http://lpsolve.sourceforge.net/5.5/).

No special prerequisites for the remaining functionalities of `adtrees`.

**Installation**

```
pip install adtrees
```

**Example**

```python
import adtrees as adt

# initialize attack(-defense) tree from an output file 'tree.xml' produced by the ADTool
T = adt.ADTree('tree.xml')

# create a basic assignment of cost for the basic actions of the defender in T
ba = adt.BasicAssignment()
for b in T.basic_actions('d'):
    ba[b] = 10

# create an instance of the 'maximal coverage' optimization problem
problem = adt.ADTilp(T, costassignment=ba, budget=100, problem='coverage')

# solve the problem
problem.solve()

# the optimal set of countermeasures and some additional information is displayed
```

For other functionalities and more details, refer to the walk-through examples in [examples folder](./examples).

**Easy usage: GUI is here!**

If you want to only analyze your attack or attack-defense tree using methods offered by the package, you can do it conveniently via a GUI. Simply type

```python
from adtrees import osead

osead()
```

*OSEAD* stands for "Optimal Strategies Extractor for Attack-Defense trees". To use it under Windows, you don't even need the package: just download the *OSEAD* tool from [here](https://people.irisa.fr/Wojciech.Widel/suftware/osead.zip.).



[license shield]: https://img.shields.io/github/license/wwidel/adtrees.svg?style=flat?color=green

[pypi package version]: https://img.shields.io/pypi/v/adtrees.svg

[python supported shield]: https://img.shields.io/pypi/pyversions/adtrees.svg
