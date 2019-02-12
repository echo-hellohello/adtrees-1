from adtrees import BasicAssignment
from adtrees import AttrDomain
from adtrees.default_domains import minCost
from tree_factory import attack_tree_structured
from tree_factory import post_tree
from random import randint


def test_rbu():
    '''
    Tree from the POST talk.
    '''
    T, ba = post_tree()
    # compute cost on set semantics
    costss = minCost.evaluateSS(T, ba)
    # compute cost using bottom-up
    costbu = minCost.evaluateBU(T, ba)
    # compute cost using repeated bottom-up
    costrbu = minCost.evaluateRBU(
        T, ba, neutralANDp=0, absorbingANDp=2**20)

    assert costbu == 35
    assert costss == 25
    assert costrbu == 25


def test_stress():
    for k in range(2, 6):
        T = attack_tree_structured(10, k)
        ba_cost = BasicAssignment()
        for i in range(10):
            # define the basic assignment
            for b in T.basic_actions('a'):
                ba_cost[b] = randint(1, 21)
            # compute cost on set semantics
            costss = minCost.evaluateSS(T, ba_cost)
            # compute cost using repeated bottom-up
            costrbu = minCost.evaluateRBU(
                T, ba_cost, neutralANDp=0, absorbingANDp=2**20)
            #
            assert costss == costrbu
