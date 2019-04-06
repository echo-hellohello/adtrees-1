from adtrees.attribute_domain import AttrDomain
from adtrees.utils import listunion


class ParetoDomain(AttrDomain):
    """
    Implementation of Pareto attribute domains for AND-OR-C attack-defense trees,
    as defined in
    "Efficient attack–defense tree analysis using Pareto attribute domains".

    class ParetoDomain(self, minplus, minmax)

    Creates Pareto attribute domain induced by
    'minplus' domains of type (min, +, +, min, +, min),
    'minmax' domains of type (min, max, max, min, max, min)
    and
    'prob' domains of type (max, *, *, max, *, max)

    Parameters
    ----------
    minplus : non-negative integer, default 0
    minmax : non-negative integer, default 0
    prob : non-negative integer, default 0

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

    def __init__(self, minplus=0, minmax=0, prob=0):
        super(ParetoDomain, self).__init__(
            addSetsCreator(m=minplus, n=minmax), mulSetsCreator(m=minplus, n=minmax, k=prob))
        self.pareto = 1


def mulPoints(a, b, m, n, k):
    """
    cost, cost, ... cost, skill, skill, ...., skill, prob, ..., prob
    m ~cost domains, n ~skill domains, k ~skill domains

    >>> a = [x, y, z]
    >>> b = [x', y', z']
    >>> m = 1
    >>> n = 2
    >>> k = 0
    >>> mulPoints(a, b, m, n, k)
    [x + x', max(y, y'), max(z, z')]
    """
    result = [a[i] + b[i] for i in range(m)]
    for i in range(m, m + n):
        result.append(max(a[i], b[i]))
    for i in range(m + n, m + n + k):
        result.append(a[i] * b[i])
    return result


def dominatedBy(a, b, j):
    """
    true iff point a is dominated by point b

    for the first j coordinates, smaller is better
    for the remaining coordinates, bigger is better
    """
    #assert len(a) == len(b)
    for i in range(j):
        if b[i] > a[i]:
            return False
    for i in range(j, len(a)):
        if b[i] < a[i]:
            return False
    return True


def paretoFrontierNaive(A, j):
    """
    for the first j coordinates, smaller is better
    for the remaining coordinates, bigger is better

    try to optimize
    have a look at http://oco-carbon.com/metrics/find-pareto-frontiers-in-python/
    also plotting
    """
    result = []
    for a in A:
        isParetoPoint = True
        for b in A:
            if b != a and dominatedBy(a, b, j):
                isParetoPoint = False
                break

        if isParetoPoint:
            result.append(a)
    return result


def mulSetsCreator(m, n, k):
    def mulSets(A, B):
        return paretoFrontierNaive([mulPoints(a, b, m, n, k) for a in A for b in B], j=m + n)
    return mulSets


def addSetsCreator(m, n):
    """
    for the first j coordinates, smaller is better
    for the remaining coordinates, bigger is better
    """
    def addSets(A, B):
        return paretoFrontierNaive(listunion(A, B), j=m + n)
    return addSets
