from adtrees.attribute_domain import AttrDomain
from adtrees.utils import listunion


class ParetoDomain(AttrDomain):
    """
    Implementation of Pareto attribute domains for AND-OR-C attack-defense trees,
    as defined in
    "Efficient attack–defense tree analysis using Pareto attribute domains".

    class ParetoDomain(self, minplus, minmax)

    Creates Pareto attribute domain induced by
    'minplus' domains of type (min, +, +, min, +, min)
    and
    'minmax' domains of type (min, max, max, min, max, min)

    Parameters
    ----------
    minplus : non-negative integer, default 0
    minmax : non-negative integer, default 0

    Examples
    ----------
    >>> from adtrees import ADNode, ADTree, BasicAssignment, ParetoDomain
    >>> root = ADNode('a', 'root', 'AND')
    >>> child1 = ADNode('a', label='a')
    >>> child2 = ADNode('a', refinement = 'OR')
    >>> child21 = ADNode('a', label = 'b')
    >>> child22 = ADNode('a', label = 'c')
    >>> T = ADTree(dictionary = {root: [child1, child2], child1: [], child2: [child21, child22], child21: [], child22: []})
    >>> pd = ParetoDomain(1, 2)
    >>> ba = BasicAssignment()
    >>> ba['a'] = [[10, 0, 0]]
    >>> ba['b'] = [[5, 1, 0]]
    >>> ba['c'] = [[3, 0, 1]]
    >>> pd.evaluateBU(T, ba)
    [[15, 1, 0], [13, 0, 1]]
    """

    def __init__(self, minplus=0, minmax=0):
        super(ParetoDomain, self).__init__(
            addSets, mulSetsCreator(m=minplus, n=minmax))


def mulPoints(a, b, m, n):
    """
    cost, cost, ... cost, skill, skill, ...., skill
    m ~cost domains, n ~skill domains

    >>> a = [x, y, z]
    >>> b = [x', y', z']
    >>> m = 1
    >>> n = 2
    >>> mulPoints(a, b, m, n)
    [x + x', max(y, y'), max(z, z')]
    """
    result = [a[i] + b[i] for i in range(m)]
    for i in range(m, m + n):
        result.append(max(a[i], b[i]))
    return result


def dominatedBy(a, b):
    """
    true iff point a is dominated by point b
    """
    #assert len(a) == len(b)
    for i in range(len(a)):
        if b[i] > a[i]:
            return False
    return True


def paretoFrontierNaive(A):
    """
    try to optimize
    have a look at http://oco-carbon.com/metrics/find-pareto-frontiers-in-python/
    also plotting!
    """
    result = []
    for a in A:
        isParetoPoint = True
        for b in A:
            if b != a and dominatedBy(a, b):
                isParetoPoint = False
                break

        if isParetoPoint:
            result.append(a)
    return result


def mulSetsCreator(m, n):
    def mulSets(A, B):
        return paretoFrontierNaive([mulPoints(a, b, m, n) for a in A for b in B])
    return mulSets


def addSets(A, B):
    return paretoFrontierNaive(listunion(A, B))
