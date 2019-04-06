from adtrees.basic_assignment import BasicAssignment
from adtrees.utils import powerset


class AttrDomain:
    """
    Implementation of an attribute domain for AND-OR-C attack-defense trees.

    class AttrDomain(self, orp, andp, oro, ando, cp, co)

    Parameters
    ----------
    orp, andp : binary functions defined for the same type of arguments.
                Operations to be performed at ORp, ANDp

    andp, oro, ando, cp, co : binary functions defined for the same type of arguments, default None.
             Operations to be performed at ORo, ANDo, Cp, Cp nodes, respectively.

    pareto : 1 if the domain is a Pareto domain, 0 otherwise

    If only orp and andp provided, it is assummed that the domain satisfies
    orp = ando = co,
    andp = oro = cp.

    Examples
    ----------
    >>> from adtrees import ADNode, ADTree, BasicAssignment, AttrDomain
    >>> root = ADNode('a', 'root', 'AND')
    >>> child1 = ADNode('a', label='a')
    >>> child2 = ADNode('a', label = 'b')
    >>> T = ADTree(dictionary = {root: [child1, child2], child1: [], child2: []})
    >>> minCostofAttack = AttrDomain(min, lambda x, y: x + y)
    >>> ba = BasicAssignment()
    >>> ba[a] = 10
    >>> ba[b] = 5
    >>> minCostofAttack.evaluateBU(T, b)
    15
    """

    def __init__(self, orp, andp, oro=None, ando=None, cp=None, co=None):
        self.orp = orp
        self.andp = andp
        if None in [oro, ando, cp, co]:
            self.oro = andp
            self.cp = andp
            self.ando = orp
            self.co = orp
            # domain of the type (x, y, y, x, y, x)
            self.type = 1
        else:
            self.oro = oro
            self.ando = ando
            self.cp = cp
            self.co = co
            # general domain
            self.type = -1
        self.pareto = 0

    def evaluateBU(self, T, ba, proponent=None):
        """
        Compute the value of the attribute modeled with the 'self' domain
        in the tree 'T', under the basic assignment 'ba', using
        the bottom-up evaluation.

        'proponent' is an optional argument, not intended for usage.
        (used for switching actors in some other functions)
        """
        # initial checks; make sure that every basic action is assigned a
        # value
        for label in T.basic_actions():
            if label not in ba:
                print('Cannot perform the attribute evaluation: the action "' +
                      label + '" has no value assigned.')
                return
        root = T.root
        if proponent == None:
            proponent = root.type
        elif proponent not in ['a', 'd']:
            print('Proponent should be one of the actors.')
            return
        opponent = ['a', 'd'][(['a', 'd'].index(proponent) + 1) % 2]
        return self.__bottomup(T, T.root, ba, proponent, opponent)

    def evaluateSS(self, T, ba, setsem=None):
        """
        Compute the value of the attribute modeled with the 'self' domain
        in the tree 'T', under the basic assignment 'ba', using
        the evaluation on the set semantics.

        The set semantics will be created if not provided as 'setsem'.
        """
        for label in T.basic_actions():
            if label not in ba:
                print('Cannot perform the attribute evaluation: the action "' +
                      label + '" has no value assigned.')
                return

        if setsem != None:
            setSemantics = setsem
        else:
            setSemantics = T.set_semantics()

        # a starting point.
        result = None

        for pair in setSemantics:
            # pair = (P, O)
            Pval = None
            # compute ANDp(ba(b)) over b in P
            for b in pair[0]:
                # to have a starting point, set the result to be equal to the value
                # assigned to one of the elements of P.
                if Pval == None:
                    Pval = ba[b]
                else:
                    Pval = self.andp(Pval, ba[b])
            # compute ORo(ba(b)) over b in O
            Oval = None
            if pair[1] != set():
                for b in pair[1]:
                    if Oval == None:
                        Oval = ba[b]
                    else:
                        Oval = self.oro(Oval, ba[b])
            # combine the values for the pair
            if Oval == None:
                pairval = Pval
            else:
                pairval = self.cp(Pval, Oval)
            # combine with the result
            if result == None:
                result = pairval
            else:
                result = self.orp(result, pairval)

        return result

    def evaluateRBU(self, T, ba, neutralANDp, absorbingANDp):
        """
        Compute the value of the attribute modeled with the 'self' domain
        in the tree 'T', under the basic assignment 'ba', using
        the repeated bottom-up evaluation.

        Suitable for non-increasing attribute domains and trees containing repeated basic actions.

        The neutral and the absorbing element for the domain's operation 'andp' need to be provided.
        """
        if self.type != 1:
            print('The repeated bottom-up evaluation can not be applied for this domain.')
            return
        for label in T.basic_actions():
            if label not in ba:
                print('Cannot perform the attribute evaluation: the action "' +
                      label + '" has no value assigned.')
        # if not T.contains_clones():
        #    return self.evaluateBU(T, ba)
        proponent = T.root.type
        result = None
        necClones, optClones = T.clonesPartitioned()
        temp_ba = BasicAssignment()
        # copy the old values
        for label in ba:
            temp_ba[label] = ba[label]
        # modify the values for necessary clones
        for label in necClones:
            temp_ba[label] = neutralANDp
        # iterate over subsets of optional clones
        for C in powerset(optClones):
            optminusC = []
            for label in optClones:
                if label in C:
                    temp_ba[label] = absorbingANDp
                else:
                    temp_ba[label] = neutralANDp
                    optminusC.append(label)
            # do the bottom-up
            itresult = self.evaluateBU(T, temp_ba, proponent)
            # modify
            for label in optminusC:
                itresult = self.andp(itresult, ba[label])
            # modify
            if result == None:
                result = itresult
            else:
                result = self.orp(result, itresult)
        # take the orginal values of the necessary clones into account
        for label in necClones:
            result = self.andp(result, ba[label])
        return result

    def __bottomup(self, T, node, ba, proponent, opponent):
        """
        Value of the attribute obtained at 'node' of adtree 'T' when using the
        bottom-up procedure under the basic assignment 'ba'.

        proponent in {'a', 'd'}.
        """
        # counter
        countered = T.countered(node)
        counter_node = T.counter(node)
        if countered:
            counter_val = self.__bottomup(
                T, counter_node, ba, proponent, opponent)
        #  basic action
        if node.ref == '':
            if countered:
                if node.type == proponent:
                    # countered basic action of the proponent
                    return self.cp(ba[node.label], counter_val)
                else:
                    # countered basic action of the opponent
                    return self.co(ba[node.label], counter_val)
            else:
                return ba[node.label]

        # else refined
        # select operator to be used for combining the values
        if node.type == proponent:
            if node.ref == 'OR':
                op_children = self.orp
            else:
                # node.ref = 'AND'
                op_children = self.andp
            if countered:
                op_counter = self.cp
        else:
            # node.type = 'd'
            if node.ref == 'OR':
                op_children = self.oro
            else:
                # node.ref = 'AND'
                op_children = self.ando
            if countered:
                op_counter = self.co
        # combine the values
        if countered:
            children = [c for c in T.children(node) if c != counter_node]
        else:
            children = T.children(node)

        result = self.__bottomup(T, children[0], ba, proponent, opponent)

        for i in range(1, len(children)):
            result = op_children(result, self.__bottomup(
                T, children[i], ba, proponent, opponent))

        if countered:
            result = op_counter(result, counter_val)
        return result

    def __bottomup_parallelized(self, T, node, ba, proponent, opponent):
        """
        Value of the attribute obtained at 'node' of adtree 'T' when using the
        bottom-up procedure under the basic assignment 'ba'.

        proponent in {'a', 'd'}.
        """
        # counter
        countered = T.countered(node)
        counter_node = T.counter(node)
        if countered:
            counter_val = self.__bottomup_parallelized(
                T, counter_node, ba, proponent, opponent)
        #  basic action
        if node.ref == '':
            if countered:
                if node.type == proponent:
                    # countered basic action of the proponent
                    return self.cp(ba[node.label], counter_val)
                else:
                    # countered basic action of the opponent
                    return self.co(ba[node.label], counter_val)
            else:
                return ba[node.label]

        # else refined
        # select operator to be used for combining the values computed for
        # children
        if node.type == proponent:
            if node.ref == 'OR':
                op_children = self.orp
            else:
                # node.ref = 'AND'
                op_children = self.andp
            if countered:
                op_counter = self.cp
        else:
            # node.type = 'd'
            if node.ref == 'OR':
                op_children = self.oro
            else:
                # node.ref = 'AND'
                op_children = self.ando
            if countered:
                op_counter = self.co

        # compute values at children, combine
        children = T.children(node)
        if counter_node in children:
            children.remove(counter_node)

        result = self.__bottomup_parallelized(
            T, children[0], ba, proponent, opponent)

        l = len(children)
        for i in range(1, l - 1, 2):
            pool = Pool(processes=2)
            args = [(T, children[i], ba, proponent, opponent),
                    (T, children[i + 1], ba, proponent, opponent)]
            results = pool.map(self.__bottomup_parallelized, args)

            for r in results:
                result = op_children(result, r)

        if l % 2 == 0:
            result = op_children(result, self.__bottomup_parallelized(
                T, children[-1], ba, proponent, opponent))

        if countered:
            result = op_counter(result, counter_val)

        return result
