from adtrees.linear_programming import ADTilp
from adtrees.default_domains import countStrats
from adtrees import BasicAssignment


def optimal_attacks(T, ba, domain, how_many=None, setsem=None, output=False):
    '''
    Return "how_many" attacks in tree "T" that are optimal with respect to the
    attribute domain "domain" and the basic assignment "ba".

    If how_many == None, then return ALL optimal attacks (and no other attacks). In particular, for a Pareto
    attribute domain, all of the Pareto optimal attacks are returned.

    Remark: if how_many is greater than the actual number of optimal attacks,
    the result will contain some suboptimal attacks.

    If output == False, return list of pairs of the form (set_of_actions_of_the_proponent, value).
    Otherwise, return a nicely formatted string.
    '''
    # heh
    k = how_many
    #
    # 1. create set semantics
    if setsem == None:
        setsem = T.set_semantics()
    # 2. compute the values of strategies, save the corresponding set of
    # actions of the proponent
    pairs = [(list(strat[0]), __strategy_value(strat, ba, domain))
             for strat in setsem]
    # deal with the trivial case
    if k != None and len(setsem) <= k:
        if output == False:
            return pairs
        else:
            # format as string
            result = "{} optimal attacks ('value: actions constituting the attack')\n".format(
                min(k, len(pairs)))
            for pair in pairs:
                new_line = "\t{}:".format(pair[1])
                pair[0].sort()
                for action in pair[0]:
                    new_line += " " + action.replace('\n', ' ') + ","
                new_line = new_line[:-1] + "\n\n"
                result += new_line
            return result
    # 3. sort strategies according to their values
    # 3.1 create a directed graph, where (i, j) is an arc iff
    #     strat=pairs[i][0] is preferable over strat=pairs[j][0]
    nb_pairs = len(pairs)
    preferences = {}
    # j in preferences[i] <=> j better than i
    for i in range(nb_pairs - 1):
        strat1 = pairs[i][0]
        val1 = pairs[i][1]
        worse_than_i = []
        for j in range(i + 1, nb_pairs):
            strat2 = pairs[j][0]
            val2 = pairs[j][1]
            if val1 != val2:
                index_of_preferable = __compare(domain, (val1, val2))
                if index_of_preferable == 0:
                    # i is better than j
                    if j not in preferences:
                        preferences[j] = set([i])
                    else:
                        preferences[j].add(i)
                elif index_of_preferable == 1:
                    # j is better than i
                    worse_than_i.append(j)
        if i not in preferences:
            preferences[i] = set(worse_than_i)
        else:
            preferences[i] = preferences[i].union(set(worse_than_i))
            # else index_of_preferable = 2, so neither is preferable; no arc added
    # 3.2 do the topological sorting of the graph; GENERATOR!
    indices_of_k_best = []
    to_be_added = k
    for item in __topological_sorting(preferences):
        if to_be_added == None:
            # get the whole first set returned by the topological sorting and
            # nothing else
            indices_of_k_best.extend(list(item))
            break
        indices_of_k_best.extend(list(item)[:to_be_added])
        to_be_added = k - len(indices_of_k_best)
        if to_be_added == 0:
            break

    k_best_strats = [pairs[i] for i in indices_of_k_best]

    if output == False:
        return k_best_strats
    else:
        if k != None:
            numero = min(k, len(k_best_strats))
        else:
            numero = len(k_best_strats)
        if numero == 1:
            result = "1 optimal attack ('value: actions constituting the attack')\n"
        else:
            result = "{} optimal attacks ('value: actions constituting the attack')\n".format(
                numero)
        for pair in k_best_strats:
            if type(pair[1]) == type([]):
                new_line = "\t{}:".format(pair[1][0])
            else:
                new_line = "\t{}:".format(pair[1])
            pair[0].sort()
            for action in pair[0]:
                new_line += " " + action.replace('\n', ' ') + ","
            new_line = new_line[:-1] + "\n\n"
            result += new_line
        return result


def optimal_countermeasures(T, ba, budget, problem="coverage", defsem=None, output=False):
    """
    sasasa
    """
    prob = ADTilp(T, ba, budget, problem, defsem)
    if problem == 'coverage':
        defs_to_deploy, number_of_prevented, number_of_preventable = prob.solve(
            verbose=False)
        ilp_result = [defs_to_deploy,
                      number_of_prevented, number_of_preventable]
    else:
        defs_to_deploy, number_of_prevented, number_of_preventable, min_invest = prob.solve(
            verbose=False)
        ilp_result = [defs_to_deploy, number_of_prevented,
                      number_of_preventable, min_invest]
    if output == False:
        return ilp_result
    else:
        # format as string
        attacker_always_wins = T.root_always_achievable()
        result = "Defender's budget: {}\n\n".format(budget)
        result += "No matter what the defender does, the attacker can achieve the root goal: {}\n\n".format(
            attacker_always_wins)

        display_def_actions = True

        if problem == 'coverage':
            result += "Under the given budget, {} attacks from the total of {} preventable attacks can be prevented.\n\n".format(
                number_of_prevented, number_of_preventable)
        else:
            if attacker_always_wins:
                min_invest_unprev = __min_cost_among_unpreventable(T, ba)
                if min_invest_unprev < min_invest:
                    result += "Given the current budget, defender cannot raise the minimal investment of the attacker into achieving the root goal, which is equal to {}.\n\n".format(
                        min_invest_unprev)
                    display_def_actions = False
                else:
                    result += "Under the given budget, the minimal investment of the attacker into achieving the root goal is {}.\n\n".format(
                        min_invest)
            else:
                result += "Under the given budget, the minimal investment of the attacker into achieving the root goal is {}.\n\n".format(
                    min_invest)
            #
        #
        if display_def_actions:
            temp = ''
            defender_cost = 0
            defs_to_deploy.sort()
            for item in defs_to_deploy:
                temp += "\t{}\n".format(item.replace('\n', ' '))
                defender_cost += ba[item]
            result += "This is achieved at the cost = {}, by implementing the following countermeasures:\n".format(
                defender_cost)
            result += temp
        return result


def __strategy_value(strategy, ba, domain):
    '''
    Value of a strategy (in the sense of the set semantics) 'strategy' wrt attribute domain 'domain'
    under the basic assignment 'ba'.

    It is assumed that the domain satisfies
        rp = ando = co,
        andp = oro = cp.
    '''
    # strategy = (P, O)
    # compute the value for the strategy
    # put the actions of both actors in one set
    actions = set(strategy[0]).union(set(strategy[1]))
    result = None
    for action in actions:
        if result == None:
            result = ba[action]
        else:
            result = domain.andp(result, ba[action])
    return result


def __compare(domain, values=(None, None)):
    '''
    Check which of the values is preferable.
    If any of them is preferable, return its index.
    Else return 2.
    '''
    v1, v2 = values
    orp_res = domain.orp(v1, v2)
    try:
        result = values.index(orp_res)
    except ValueError:
        result = 2
    # print("values are {}, {}, and the index of the preferable one is {}".format(
    #    v1, v2, result))
    return result


def __min_cost_among_unpreventable(T, ba):
    # 1. compute unpreventable attacks in T
    attackers_actions = T.basic_actions('a')
    defenders_actions = T.basic_actions('d')
    ba_for_unprev = BasicAssignment()
    for b in attackers_actions:
        ba_for_unprev[b] = [[b]]
    for b in defenders_actions:
        ba_for_unprev[b] = []
    unpreventable = countStrats.evaluateBU(T, ba_for_unprev)
    # 2. compute the minimal of their costs
    minimum = None
    for strat in unpreventable:
        strat_cost = 0
        for b in strat:
            strat_cost += ba[b]
        if minimum == None:
            minimum = strat_cost
        else:
            minimum = min(minimum, strat_cost)
    return minimum


def __topological_sorting(data):
    """
    Code by Sam Denton, taken from
        http://code.activestate.com/recipes/578272-topological-sort/

    Dependencies are expressed as a dictionary whose keys are items
    and whose values are a set of dependent items. Output is a list of
    sets in topological order. The first set consists of items with no
    dependencies, each subsequent set consists of items that depend upon
    items in the preceeding sets.

    >>> print '\\n'.join(repr(sorted(x)) for x in toposort2({
    ...     2: set([11]),
    ...     9: set([11,8]),
    ...     10: set([11,3]),
    ...     11: set([7,5]),
    ...     8: set([7,3]),
    ...     }) )
    [3, 5, 7]
    [8, 11]
    [2, 9, 10]

    """
    from functools import reduce

    # Ignore self dependencies.
    for k, v in data.items():
        v.discard(k)
    # Find all items that don't depend on anything.
    extra_items_in_deps = reduce(
        set.union, data.values()) - set(data.keys())
    # Add empty dependences where needed
    data.update({item: set() for item in extra_items_in_deps})
    while True:
        ordered = set(item for item, dep in data.items() if not dep)
        if not ordered:
            break
        yield ordered
        data = {item: (dep - ordered)
                for item, dep in data.items()
                if item not in ordered}
    assert not data, "Cyclic dependencies exist among these items:\n%s" % '\n'.join(
        repr(x) for x in data.items())
