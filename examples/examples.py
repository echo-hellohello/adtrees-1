import adtrees as adt


def ex_handmade():
    '''
    How to create an ADTree when not using ADTool. And how to produce an .xml file storing the structure of the tree
    that will be accepted as input by ADTool.
    '''
    # create some nodes
    root = adt.ADNode(actor='a', label='Crack password', refinement='OR')
    n1 = adt.ADNode(label='Brute force attack')
    n2 = adt.ADNode(label='Guess')
    # put them into a dictionary storing the tree structure
    # {node: [children of the node], ...}
    d = {root: [n1, n2], n1: [], n2: []}
    # initialize tree using the dictionary
    T = adt.ADTree(dictionary=d)
    # the tree is T = ORp(Brute force attack, Guess).
    # print the adterm corresponding to T
    print(T)
    # create an .xml file that can be opened in ADTool in order to visualize T
    T.output('handmade.xml')
    return


def ex_basic():
    '''
    Some basic properties of ADTrees.
    '''
    # load tree from an .xml file produced by ADTool
    path = 'tree_ex.xml'
    T = adt.ADTree(path)
    # basic stuff: displaying adterm, size of a tree, its root node
    print('Going to see some basic properties of the tree\n{}, from tree_ex.png.\n'.format(T))
    print('There are {} nodes in the tree.'.format(T.order()))
    print('The root node of the tree is {}.\n'.format(T.root))
    # countermeasures
    if T.countered(T.root):
        print('There is a countermeasure attached to the root node. The countermeasure is {}.\n'.format(
            T.counter(T.root)))
    else:
        print('There is no countermeasure attached to the root node.\n')
    # basic actions
    print('The basic actions of the attacker in the tree are {}.'.format(
        T.basic_actions('a')))
    print('The basic actions of the defender are {}.'.format(
        T.basic_actions('d')))
    # checking if there are repeated basic actions in a tree and if a given
    # basic actions is a clone
    if T.contains_clones():
        print('There are repeated basic actions in the tree.')
        repeated_basics = [b for b in T.basic_actions() if T.isclone(b)]
        print('These are {}.\n'.format(repeated_basics))
    else:
        print('There are no repeated basic actions in the tree.\n')
    return


def ex_semantics():
    '''
    Set and defense semantics for ADTrees.
    '''
    path = 'tree_ex.xml'
    T = adt.ADTree(path)
    print(T)
    # creating set semantics
    print('\nThe set semantics of the tree from tree_ex.png file is the following.')
    for strategy in T.set_semantics():
        print(strategy)
    # creating defense semantics
    print('\nThe defense semantics of the tree is the following.')
    for strategy in T.defense_semantics():
        print(strategy)
    print("\nUps, there are repeated basic actions in the tree! Let's try with another tree, the one from optimization.png.\n")
    path = 'optimization.xml'
    T = adt.ADTree(path)
    print(T)
    # defense semantics
    print('\nThe defense semantics of the tree is the following.')
    for strategy in T.defense_semantics():
        print(strategy)
    return


def ex_cost():
    '''
    Usage of BasicAssignment(), AttrDomain() and an ilustration of three ways of computing the minimal cost of an attack in an ADTree.
    '''
    # Step 1: load a tree
    path = 'tree_ex.xml'
    # could have been:
    # path = 'tree_ex_cost.xml'
    # giving the same result.
    T = adt.ADTree(path)

    # Step 2: create a basic assignment
    # way 1: load it from an .xml file
    ba = adt.BasicAssignment('tree_ex_cost.xml')
    # but the ADTool's .xml output file for the 'minimal cost of an attack for the proponent' attribute domain
    # does not contain values assigned to the basic actions of the proponent.
    # we will modify them, under the assumption that the defender implements
    # actions x, y and z, and does not implement any of v, w (see
    # 'tree_ex.png' or 'tree_ex_cost.png').
    implemented = ['x', 'y', 'z']
    for b in implemented:
        ba[b] = 2**30  # modelling +infty
    for b in [d for d in T.basic_actions('d') if d not in implemented]:
        ba[b] = 0
    # store the modified basic assignment in a .txt file
    ba.output('new_ba.txt')
    # so it can be later reused with
    # ba = adt.BasicAssignment('new_ba.txt')

    # Step 3: select domain
    mincost = adt.default_domains.minCost
    # alternatively:
    # mincost = adt.AttrDomain(min, lambda x, y: x + y)
    # some other standard domains are defined in 'default_domains'

    # Step 4: compute!
    # observe that, other than a tree and a basic assignment, the repeated bottom-up procedure needs to be provided with the neutral and the absorbing element
    # for the operation performed at AND nodes of the proponent
    print('The minimal cost of an attack in the tree from tree_ex.png, namely, \n{},\nunder the basic assignment \n{}\nis:\n\n'.format(T, ba))
    print('{} - when computed using the bottom-up evaluation,'.format(mincost.evaluateBU(T, ba)))
    print('{} - when computed using the evaluation on the set semantics,'.format(mincost.evaluateSS(T, ba)))
    print('{} - when computed using the repeated bottom-up evaluation.'.format(
        mincost.evaluateRBU(T, ba, 0, 2**30)))

    print('\nExplanation: there are repeated basic actions in the tree, so the bottom-up fails.\nComputation on the set semantics returns the correct result.\nRepeated bottom-up can not be applied in this case, since the basic assignment does not satisfy necessary conditions.')
    print('\n\nHowever, under the assumption that the opponent/defender executes all of their actions, you get:\n')
    for b in T.basic_actions('d'):
        ba[b] = 2**30
    print('{} - when computed using the bottom-up evaluation,'.format(mincost.evaluateBU(T, ba)))
    print('{} - when computed using the evaluation on the set semantics,'.format(mincost.evaluateSS(T, ba)))
    print('{} - when computed using the repeated bottom-up evaluation.'.format(
        mincost.evaluateRBU(T, ba, 0, 2**30)))
    return


def ex_pareto():
    '''
    How to create and use Pareto attribute domains.
    '''
    # Step 1: load a tree
    T = adt.ADTree('tree_ex.xml')
    # Step 2: create a Pareto attribute domain
    pd = adt.ParetoDomain(1, 2)
    # ParetoDomain(m, k) is a Pareto domain induced by m (min, +)-domains and k (min, max)-domains.
    # Step 3: load a basic assignment
    ba = adt.BasicAssignment('ba_pareto.txt')
    # Step 4: compute!
    print('The optimal values of attacks in \n{}\nunder the basic assignment \n{}\nare:\n\n'.format(T, ba))
    print('{} - when computed using the bottom-up evaluation,'.format(pd.evaluateBU(T, ba)))
    print('{} - when computed using the evaluation on the set semantics,'.format(pd.evaluateSS(T, ba)))
    print('{} - when computed using the repeated bottom-up evaluation.'.format(
        pd.evaluateRBU(T, ba, [[0, 0, 0]], [[2**30, 2**30, 2**30]])))

    # alternative way of defining a basic assignment
    ba = adt.BasicAssignment()
    for b in T.basic_actions('d'):
        ba[b] = [[2**30, 2**30, 2**30]]  # the absorbing element
    for b in ['a', 'b', 'd']:
        ba[b] = [[15, 0, 1]]
    for b in ['c', 'e']:
        ba[b] = [[10, 1, 2]]
    return


def ex_optimization():
    '''
    Defining and solving optimization problems for ADTrees ('coverage' and 'minimal investment of the attacker' problems).
    '''
    # Step 1: load a tree
    T = adt.ADTree('optimization.xml')
    # Step 2: assign cost values to the actions of the defender, set
    # defender's budget
    ba = adt.BasicAssignment()
    for b in T.basic_actions('d'):
        ba[b] = 10
    budget = 15
    # Step 3: define the problem
    # coverage
    problem = adt.ADTilp(T, costassignment=ba, budget=budget,
                         problem='coverage', defsem=None)
    # if the defense semantics is not passed as 'defsem' argument, it is
    # computed when the problem is initialized.
    # solve the coverage problem
    problem.solve()

    # maximizing the minimal investment of the attacker
    # requires assignment of costs to the actions of the attacker
    for b in ['a', 'b', 'c', 'd']:
        ba[b] = 100
    ba['e'] = 10
    # four expensive actions, each constituting an attack strategy; one cheap
    # attack strategy
    problem = adt.ADTilp(T, costassignment=ba, budget=budget,
                         problem='investment', defsem=None)
    problem.solve()
    # result is displayed: only the cheap attack is prevented
    return


def main():
    print('Example 1: ex_handmade\n')
    ex_handmade()
    input('\npress enter to continue\n')

    print('Example 2: ex_basic\n')
    ex_basic()
    input('\npress enter to continue\n')

    print('Example 3: ex_semantics\n')
    ex_semantics()
    input('\npress enter to continue\n')

    print('Example 4: ex_cost\n')
    ex_cost()
    input('\npress enter to continue\n')

    print('Example 5: ex_pareto\n')
    ex_pareto()
    input('\npress enter to continue\n')

    print('Example 6: ex_optimization\n')
    ex_optimization()

if __name__ == '__main__':
    main()
