from adtrees import ADNode
from adtrees import ADTree


def get_tree(n):
    '''
    Return ADTree
    T = Ca(ORa(Ca(1, n+1), Ca(2, n+2), ..., Ca(n, n+n)), Cd(ORd(2n+1, 2n+2), ANDa(2n+3, 2n+4)))
    '''
    # T = Ca(ORa(Ca(1, n+1), Ca(2, n+2), ..., Ca(n, n+n)), Cd(ORd(2n+1, 2n+2),
    # ANDa(2n+3, 2n+4)))
    root = ADNode('a', 'root', 'OR')
    tree_dict = {root: []}
    for i in range(1, n + 1):
        child = ADNode('a', i)
        child_counter = ADNode('d', n + i)
        tree_dict[root].append(child)
        tree_dict[child] = [child_counter]
        tree_dict[child_counter] = []
    root_counter = ADNode('d', 'X', 'OR')
    tree_dict[root].append(root_counter)
    tree_dict[root_counter] = []
    for i in range(1, 3):
        child = ADNode('d', 2 * n + i)
        tree_dict[root_counter].append(child)
        tree_dict[child] = []
    count_count = ADNode('a', 'Y', 'AND')
    tree_dict[root_counter].append(count_count)
    tree_dict[count_count] = []
    for i in range(3, 5):
        child = ADNode('a', 2 * n + i)
        tree_dict[count_count].append(child)
        tree_dict[child] = []
    return ADTree(dictionary=tree_dict)


def extremal_tree(m):
    '''
    Return ADTree
    T = ANDp(ORp(Cp(1, Co(m+1, 2*m+1)), Cp(2, Co(m+2, 2*m+2))), ..., ORp(Cp(m-1, Co(2*m-1, 3*m+1)), Cp(m, Co(2*m, 3*m))))
    '''
    root = ADNode('a', 'root', 'AND')
    tree_dict = {root: []}
    for i in range(1, m + 1, 2):
        child = ADNode('a', 'labb' + str(i), 'OR')
        child1 = ADNode('a', i)
        child2 = ADNode('a', i + 1)
        child1_counter = ADNode('d', m + i)
        child2_counter = ADNode('d', m + i + 1)
        child1_counter_counter = ADNode('a', 2 * m + i)
        child2_counter_counter = ADNode('a', 2 * m + i + 1)
        tree_dict[root].append(child)
        tree_dict[child] = [child1, child2]
        tree_dict[child1] = [child1_counter]
        tree_dict[child2] = [child2_counter]
        tree_dict[child1_counter] = [child1_counter_counter]
        tree_dict[child2_counter] = [child2_counter_counter]
        tree_dict[child1_counter_counter] = []
        tree_dict[child2_counter_counter] = []
    return ADTree(dictionary=tree_dict)
