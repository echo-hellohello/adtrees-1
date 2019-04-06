from adtrees.adtparser import file_to_dict
from adtrees.adnode import ADNode
from adtrees.default_domains import setSem, minSkillLvl
from adtrees.default_domains import attStrat
from adtrees.default_domains import countStrats
from adtrees.default_domains import suffWit
from adtrees.default_domains import satisfiability
from adtrees.basic_assignment import BasicAssignment
from adtrees.utils import minimal_lists


class ADTree:
    """
    Implementation of attack-defense trees.

    class ADTree(self, path, dictionary, attack_tree)

    Parameters
    ----------
    path: str, default ''
        Path to an .xml output file produced by ADTool. If provided, the tree is loaded from the file.
    dictionary : dict, empty by default
        Dictionary with keys being ADNodes and values being lists
        of ADNodes. Dictionary[node] is a list of children of the node.
    attack_tree : boolean, default False
        If True, then the tree generated is an attack tree, i.e., an
        attack-defense tree with all the nodes being of the same type.
        Some methods were designed for attack trees and not adtrees.

    Examples
    ----------
    >>> x = ADNode('a', 'break in', 'OR')
    >>> x1 = ADNode('a', 'break in through the back door')
    >>> x2 = ADNode('a', 'break in through one of the windows')
    >>> y1 = ADNode('d', 'install lock on the back door')
    >>> d = {x: [x1, x2], x1: [y1], x2: [], y1: []}
    >>> T1 = ADTree(d)
    >>> T1.output('tree.xml')
    >>> T2 = ADTree('tree.xml')
    """

    def __init__(self, path='', dictionary={}, attack_tree=False):
        """
        self.adterm
        self.attack
        self.basics
        self.dict
        self.root
        """
        super(ADTree, self).__init__()
        # check whether the parameters provided are OK.
        # attack_tree
        if attack_tree in [True, False]:
            self.attack = attack_tree
        else:
            print('Invalid value of attack_tree parameter.')
            help(ADTree)
            return
        # creating dictionary from ADTool's .xml file
        if type(path) == type('') and path[-4:] == '.xml':
            self.dict = file_to_dict(path)
            if self.dict == None:
                return
            # set root
            nodes_having_parents = []
            for key in self.dict:
                for node in self.dict[key]:
                    nodes_having_parents.append(node)
            # set root
            for node in self.dict:
                if node not in nodes_having_parents:
                    self.root = node
                    break
        # creating dictionary from a dictionary
        elif type(dictionary) == type({}) and len(dictionary) > 0:
            # tree is created from a dictionary.
            # check if the dictionary actually describes a tree
            keys = [i for i in dictionary.keys()]
            in_lists = [node for item in dictionary.values()
                        for node in item]
            # 1. every element that is in one of the lists is also a key
            #    of the dictionary; and it is an ADNode
            for item in in_lists:
                if type(item) != ADNode or item not in keys:
                    print(
                        'Either dictionary does not describe a tree or else not all of the elements are ADNodes.')
                    help(ADTree)
                    return
            # 2. there is exactly one element in the keys that is not in the lists,
            #   namely, the root of the tree.
            roots = [i for i in keys if i not in set(in_lists)]
            if len(roots) != 1:
                print('Invalid number of roots.')
                help(ADTree)
                return
            elif type(roots[0]) != ADNode:
                print('At least one of the dictionary keys is not an ADNode.')
                help(ADTree)
                return
            self.root = roots[0]
            # finally, create self.dict.
            self.dict = {}
            for key in keys:
                self.dict[key] = dictionary[key]
        else:
            self.attack = True
            self.root = ADNode(label='root')
            self.dict = {self.root: []}
        # set term
        self.adterm = self.adterm()
        # store the set of all nodes holding basic actions of the tree.
        self.basics = set(
            [node for node in self.dict.keys() if node.isbasic()])
        # DAGIFY
        # self.dagify()

    def adterm(self, node=None):
        """
        Given an ADTree T and one of its nodes, create an ADTerm that corresponds
        to the subtree of T rooted in the node.
        If no node passed, then the ADTerm created corresponds to T.
        """
        if node == None:
            node = self.root
        countered = self.countered(node)
        countermeasure = self.counter(node)
        if node.isbasic():
            # the node represents a basic action; has at most one child,
            # which is a countermeasure
            if not countered:
                # the node is a leaf of the tree
                return node.label
            else:
                return('C' + node.type + '(' + node.label + ',' + self.adterm(countermeasure) + ')')
        else:
            # else the node is refined and has children of the same type.
            if countered:
                result = 'C' + node.type + '(' + node.ref + node.type + '('
                for child in self.dict[node]:
                    if child != countermeasure:
                        result += self.adterm(child)
                        result += ','
                # put the countermeasure at the end
                result = result[:-1] + '),'
                result += self.adterm(countermeasure)
                result += ')'
                return result
            else:
                result = node.ref + node.type + '('
                for child in self.dict[node]:
                    result += self.adterm(child)
                    result += ','
                result = result[:-1] + ')'
                return result

    def basic_actions(self, actor=None):
        """
        Return the list of labels of basic actions of a given actor ('a', 'd' or None) in the tree.
        If no actor provided, return the list of all basic actions.
        """
        if actor not in ['a', 'd', None]:
            help(ADTree)
            return
        bas = []
        if actor == None:
            allowed = ['a', 'd']
        else:
            allowed = [actor]
        for node in self.basics:
            if node.type in allowed:
                if node.label not in bas:
                    bas.append(node.label)
        return bas

    def children(self, node):
        """
        Return list of the children of a node (including countermeasure).
        """
        return self.dict[node]

    def countered(self, node):
        if self.counter(node) != None:
            return True
        return False

    def counter(self, node):
        """
        Return a countermeasure to a given node, if there is one.
        False otherwise.

        Returns ADNode.
        """
        if node not in self.dict:
            print('Node provided does not belong to the tree.')
            print()
            help(ADTree.counter)
            return
        ntype = node.type
        for child in self.dict[node]:
            if child.type != ntype:
                return child
        return None

    # def dagify(self):
    #     """
    #     Turn tree into a DAG.
    #
    #     For now: it is assumed that the underlying tree is "well-formed", i.e.,
    #     that the result of dagification is indeed acyclic.
    #     """
    #     # no need if each of the labels appears once
    #     count = []
    #     repeated_labels = False
    #     for node in self.dict:
    #         if node.label not in count:
    #             count.append(node.label)
    #         else:
    #             # this label has been seen before
    #             repeated_labels = True
    #             break
    #     if not repeated_labels:
    #         return
    #     #
    #     new_nodes = {}
    #     new_dict = {}
    #     # iterate over nodes
    #     for node in self.dict:
    #         label = node.label
    #         # if no new node bearing the label exists, create it
    #         if label not in new_nodes:
    #             new_nodes[label] = node.copy()
    #         new_node = new_nodes[label]
    #         # add the node bearing the label to the new dictionary, if it is not in
    #         # there yet
    #         if new_node not in new_dict:
    #             new_dict[new_node] = []
    #         # add children
    #         for child in self.dict[node]:
    #             child_label = child.label
    #             if child_label not in new_nodes:
    #                 new_nodes[child_label] = child.copy()
    #             if new_nodes[child_label] not in new_dict[new_node]:
    #                 new_dict[new_node].append(new_nodes[child_label])
    #     self.dict = new_dict

    def parent(self, node):
        """
        Return parent node of a given node.
        """
        for candidate, children in self.dict.items():
            if node in children:
                return candidate
        return None

    def contains_clones(self):
        if self.root.type == 'a':
            # attacker is the proponent
            a_role = 'p'
            d_role = 'o'
        else:
            a_role = 'o'
            d_role = 'p'
        for b in self.basic_actions('a'):
            if self.isclone(b, a_role):
                return True
        for b in self.basic_actions('d'):
            if self.isclone(b, d_role):
                return True
        return False

    def isclone(self, label, actor='p'):
        """
        Return True iff there are more than one
        nodes (of the specified actor: proponent or opponent)
        holding a basic action that bear the same label 'label'.
        """
        if actor == 'p':
            actor = self.root.type
        else:
            if self.root.type == 'a':
                actor = 'd'
            else:
                actor = 'a'
        actorLabels = self.basic_actions(actor)
        if label not in actorLabels:
            return False
        counter = 0
        for node in self.basics:
            if node.type == actor and node.label == label:
                counter += 1
            if counter > 1:
                return True
        return False

    def clonesPartitioned(self):
        """
        Return two lists
        [labels of necessary clones], [labels of optional clones]
        as defined in
        "On quantitative analysis of attack–defense trees with repeated labels".
        """
        basics_prop = self.basic_actions('a')
        basics_opp = self.basic_actions('d')
        # create basic assignment
        ba = BasicAssignment()
        for b in basics_opp:
            ba[b] = 2
        for b in basics_prop:
            ba[b] = 0
        clones = [
            label for label in basics_prop if self.isclone(label)]
        necessary = []
        optional = []
        # do the bottom up for each of the clones
        for label in clones:
            ba[label] = 1
            if minSkillLvl.evaluateBU(self, ba) == 1:
                necessary.append(label)
            else:
                optional.append(label)
            ba[label] = 0
        return necessary, optional

    def order(self):
        """
        return the number of nodes in self.
        """
        return len(self.dict)

    def __xml__(self, node=None, counter=0):
        """
        Create contents of the output file created by output().
        Keep only the structure and labels of nodes holding basic actions.

        //Node treated as a countermeasure if counter = 1; technical parameter.
        """
        if node == None:
            node = self.root
        countered = self.countered(node)
        countermeasure = self.counter(node)

        if node.ref == 'AND':
            ref = '"conjunctive"'
        else:
            # in ADTool 2.2.2, default refinement for basic actions is
            # "disjunctive"
            ref = '"disjunctive"'

        if not counter:
            # if the node is not a countermeasure itself, no switching of
            # actors
            prefix = '\t<node refinement=' + ref + '>\n' + \
                '\t\t<label>' + node.label + '</label>\n\t'
        else:
            # if the node itself is a countermeasure, switch actors
            prefix = '\t<node refinement=' + ref + ' switchRole="yes">\n' + \
                '\t\t<label>' + node.label + '</label>\n\t'

        result = prefix
        for child in self.dict[node]:
            if child != countermeasure:
                result += self.__xml__(child)
        if countered:
            result += self.__xml__(countermeasure, 1)
        result += '</node>\n'
        return result

    def output(self, name=''):
        """
        Create an .xml file corresponding to self that will be accepted as input by ADTool.
        """
        if name == '':
            print('Provide a name for the output file.')
            return
        if name[-4:] != '.xml':
            name += '.xml'
        with open(name, 'w') as f:
            f.write("<?xml version='1.0'?>\n")
            f.write('<adtree>\n')
            f.write(self.__xml__(self.root))
            f.write('</adtree>')
        print('Tree structure written to "' +
              name + '", ready to be opened with ADTool!')
        return

    def set_semantics(self):
        """
        Return the set semantics of an attack(-defense) tree T, as formulated in
        "On quantitative analysis of attack–defense trees with repeated labels"
        by Kordy et al.

        Returns a list of two-element lists
            [[set, set], [set, set], ..., [set, set]],
        with each element of each of the lists being a set of basic actions.
        """
        ba = BasicAssignment()
        for label in self.basic_actions('a'):
            ba[label] = [[set([label]), set()]]
        for label in self.basic_actions('d'):
            ba[label] = [[set(), set([label])]]
        return setSem.evaluateBU(self, ba)

    def defense_semantics(self):
        """
        Return the defense semantics of an attack-defense tree T, as defined in
        "How well can I secure my system?".

        Returns a list of two-element lists
            [[set, set], [set, set], ..., [set, set]],
        with each element of each of the lists being a set of basic actions.
        """
        attackers_actions = self.basic_actions('a')
        defenders_actions = self.basic_actions('d')
        # step 1: create attack strategies
        if self.contains_clones():
            # variant 1: for trees containing repeated basic actions
            # substep 1: create witnesses
            ba = BasicAssignment()
            for b in attackers_actions:
                ba[b] = []
            for b in defenders_actions:
                ba[b] = [[b]]
            witnesses = suffWit.evaluateBU(self, ba)
            # substep 2: iterate over witnesses, get attack strategies
            # countering them
            AS = []
            for witness in witnesses:
                ba = BasicAssignment()
                for b in attackers_actions:
                    ba[b] = [[b]]
                for b in defenders_actions:
                    if b in witness:
                        ba[b] = []
                    else:
                        ba[b] = [[]]
                candidates = countStrats.evaluateBU(self, ba)
                # select the minimal ones
                for AS_countering_witness in minimal_lists(candidates):
                    if AS_countering_witness not in AS:
                        AS.append(AS_countering_witness)
        else:
            # variant 2: for trees containing no repeated basic actions (iFM)
            ba = BasicAssignment()
            for b in attackers_actions:
                ba[b] = [[b]]
            for b in defenders_actions:
                ba[b] = [[]]
            AS = attStrat.evaluateBU(self, ba)

        # At this point AS is the set of all attack strategies in the tree.
        # step 2: defense strategies countering attack strategies
        result = []
        # 2.1 swap actors
        proponent = 'd'
        # 2.2 create a basic assignment
        for b in self.basic_actions('d'):
            ba[b] = [[b]]
        # iterate
        for A in AS:
            # modify the basic assignment
            for b in attackers_actions:
                if b in A:
                    ba[b] = []
                else:
                    ba[b] = [[]]
            # do the bottom-up
            candidates = countStrats.evaluateBU(self, ba, proponent)
            # select the minimal ones
            for candidate in minimal_lists(candidates):
                result.append([set(A), set(candidate)])
        return result

    def root_always_achievable(self):
        ba = BasicAssignment()
        for b in self.basic_actions():
            ba[b] = 1
        return satisfiability.evaluateBU(self, ba) == 1

    def __repr__(self):
        return self.adterm
