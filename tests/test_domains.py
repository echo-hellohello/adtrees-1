from adtrees import BasicAssignment
from adtrees import AttrDomain
from gettree import get_tree

n = 15
T = get_tree(n)


def test_basic_assignment_initialization():
    ba = BasicAssignment()


def test_attr_domain_initialization():
    costdom = AttrDomain(min, lambda x, y: x + y)


def test_basic_assignment_set_values():
    ba = BasicAssignment()
    for b in T.basic_actions('a'):
        ba[b] = int(b)


def test_attr_domain_bottom_up():
    ba = BasicAssignment()
    costdom = AttrDomain(min, lambda x, y: x + y)
    for b in T.basic_actions('a'):
        ba[b] = int(b)
    for b in T.basic_actions('d'):
        ba[b] = 0
    ba[str(2 * n + 1)] = 2**30
    # one action of defender with +infty
    expected_min_cost = 1 + (2 * n + 3) + (2 * n + 4)
    actual_cost_bu = costdom.evaluateBU(T, ba)
    assert expected_min_cost == actual_cost_bu


def test_attr_domain_on_set_semantics():
    ba = BasicAssignment()
    costdom = AttrDomain(min, lambda x, y: x + y)
    for b in T.basic_actions('a'):
        ba[b] = int(b)
    for b in T.basic_actions('d'):
        ba[b] = 0
    ba[str(2 * n + 1)] = 2**30
    # one action of defender with +infty
    expected_min_cost = 1 + (2 * n + 3) + (2 * n + 4)
    actual_cost_ss = costdom.evaluateSS(T, ba)
    assert expected_min_cost == actual_cost_ss


def test_attr_domain_repeated_bottom_up():
    ba = BasicAssignment()
    costdom = AttrDomain(min, lambda x, y: x + y)
    for b in T.basic_actions('a'):
        ba[b] = int(b)
    for b in T.basic_actions('d'):
        ba[b] = 0
    ba[str(2 * n + 1)] = 2**30
    # one action of defender with +infty
    expected_min_cost = 1 + (2 * n + 3) + (2 * n + 4)
    actual_cost_rbu = costdom.evaluateRBU(T, ba, 0, 2**30)
    assert expected_min_cost == actual_cost_rbu
