from adtrees import BasicAssignment
from adtrees import ParetoDomain
from tree_factory import attack_defense_tree_structured

m = 6
T = attack_defense_tree_structured(m // 2)


def test_extremal_tree():
    ba = BasicAssignment()
    pd = ParetoDomain(m)  # m minimal cost domains
    neutral = [[0 for j in range(m)]]
    absorbing = [[2**30 for j in range(m)]]
    for i in range(1, m + 1):
        ba[str(i)] = [[0 for j in range(m)]]
        ba[str(i)][0][i - 1] = 1
        # defender
        ba[str(m + i)] = absorbing
        # leafs of the attacker
        ba[str(2 * m + i)] = neutral
    #  evaluate
    # 2**m elements in the set semantics
    # half of them are of the form (P, emptyset), each P is unique
    # => 2**(m/2) Pareto optimal strategies, under the above assignment
    res1 = pd.evaluateBU(T, ba)
    res2 = pd.evaluateSS(T, ba)
    res3 = pd.evaluateRBU(T, ba, neutral, absorbing)

    assert len(res1) == 2**(m / 2)
    assert res1 == res2
    assert res2 == res3
