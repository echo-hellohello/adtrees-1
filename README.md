**Prerequisites**

Requires *setuptools*, which can be installed using `pip install setuptools`.

Optional: *numpy*, *scipy*, *lp_solve* - needed for optimization problems. The first two
can be installed with:

```
pip install numpy
pip install scipy
```

For the installation of *lp_solve*, see [Using lpsolve from Python](https://lpsolve.sourceforge.net/5.5/Python.htm).
General information on *lp_solve* can be found [here](https://lpsolve.sourceforge.net/5.5/).

The package is intended to be used together with the [ADTool](https://satoss.uni.lu/members/piotr/adtool/).


**Installation**

```
pip install adtrees
```


**Examples**

```python
import adtrees as adt

# assuming that 'tree.xml' is an output file produced by ADTool
T = adt.ADTree('tree.xml')
```

For more advanced usage, refer to the walk through examples in [examples folder](../examples).
