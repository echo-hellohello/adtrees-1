`adtrees` implements some methods for qualitative and quantitative evaluation of security using [attack trees](https://en.wikipedia.org/wiki/Attack_tree)
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
