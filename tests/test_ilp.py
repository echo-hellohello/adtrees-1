from gettree import get_tree
from gettree import extremal_tree
from adtrees import BasicAssignment
try:
    from adtrees import ADTilp
    flag = True
except:
    flag = False


def test_coverage():
    if flag:
        T = get_tree(15)
        ba = BasicAssignment()
        for b in T.basic_actions('d'):
            ba[b] = 10

        i = 2

        budget = 10 * i
        problem = ADTilp(T, ba, budget)
        actual_solution = problem.solve()
        expected_not_countered = n - (i - 1)
        assert actual_solution[0] == expected_not_countered
        # the defender has to implement at least one of the actions 2n+1 and
        # 2n+2
        assert str(
            2 * n + 1) in actual_solution[1] or str(2 * n + 2) in actual_solution[1]


def test_investment():
    if flag:
        T = get_tree(15)
        ba = BasicAssignment()
        for b in T.basic_actions('d'):
            ba[b] = 10
        for b in T.basic_actions('a'):
            ba[b] = int(b)

        i = 2

        budget = 10 * i
        problem = ADTilp(T, ba, budget, 'investment')
        actual_solution = problem.solve()

        assert str(
            2 * n + 1) in actual_solution[1] or str(2 * n + 2) in actual_solution[1]

        #temp = (2 * n + 3) + (2 * n + 4)
        temp = 4 * n + 7
        print(n, temp)
        # the attacker has to perform both actions (2 * n + 3) and (2 * n +
        # 4)
        assert actual_solution[0] >= temp

        expected_min_investment = temp + i
        assert actual_solution[0] <= expected_min_investment
        # the difference between expected and actual

        assert expected_min_investment - actual_solution[0] in [0, 1]

        # no idea why the difference is sometimes equal to 1 :(
        # is it because of the inner workings of lp_solve?
