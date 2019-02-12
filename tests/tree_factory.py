from adtrees import ADNode, ADTree
from adtrees import BasicAssignment


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


def attack_tree_structured(m, k=0, dic=0):
    '''
    int m >= 2
    int k <= m

    Return attack tree ANDp(ORp(b1, b2), ..., ORp(b_{2*m-1}, b_{2*m})), with
        2*m leaf nodes,
        k <= m repeated basic actions, and
        3*m + 1 nodes.

    If dic == 1, then return dictionary holding the structure of the tree, and not tree itself.

    Remark: if k=0, then the size of the set semantics of the tree is 2**m.
    '''
    root = ADNode('a', 'root', 'AND')
    dict = {root: []}
    new_leaf = 1
    for i in range(m):
        # create new nodes
        ornode = ADNode('a', 'ref_' + str(i + 1), 'OR')
        leftchild = ADNode('a', new_leaf)
        rightchild = ADNode('a', new_leaf + 1)
        # update dictionary
        dict[root].append(ornode)
        dict[ornode] = [leftchild, rightchild]
        dict[leftchild] = []
        dict[rightchild] = []
        # update the label of the next leaf node
        if new_leaf < k:
            new_leaf += 1
        else:
            new_leaf += 2

    if dic:
        return dict
    else:
        return ADTree(dictionary=dict)


def attack_defense_tree_structured(m, k=0):
    '''
    int m >= 2
    int k <= m

    Return attack-defense tree
    ANDp(ORp(Cp(b1, Co(b_{2*m+1}, b_{4*m+1})), Cp(b2, Co(b_{2*m+2}, b_{4*m+2}))), ..., ORp(Cp(b_{2*m-1}, Co(b_{4*m-1}, b_{6*m+1})), Cp(b_{2*m}, Co(b_{4*m}, b_{6*m}))),
    with
        7*m + 1 nodes,
        6*m nodes holding basic actions, and
        k <= 2*m repeated basic actions of the proponent.


    Remark: if k=0, then the size of the set semantics of the tree is 2**(2 * m).
    '''
    d = attack_tree_structured(m, k, dic=1)
    basics = [node for node in d if d[node] == []]
    for node in basics:
        counternode = ADNode('d', int(node.label) + 2 * m)
        countercounter = ADNode('a', int(node.label) + 4 * m)
        d[node].append(counternode)
        d[counternode] = [countercounter]
        d[countercounter] = []
    return ADTree(dictionary=d)


def attack_tree_semantics_faster(m):
    '''
    m >= 2

    Return attack tree
    ANDp(T, ORp(b_{13}, b_{13}, ..., b_{12 + m},b_{12 + m})),
    where
    T = ANDp(ORp(b1, b2), ..., ORp(b_11, b_12})),
    i.e., T is a tree obtained by calling attack_tree_structured(6, 0).

    The tree created has
        2*m + 21 nodes,
        2*m + 12 nodes holding basic actions,
        m repeated basic actions of the proponent, and
        set semantics of size 64*m.

    Therefore, the repeated bottom-up procedure is expected to terminate in time
    O((2*m + 21) * 2**m)).
    '''
    T = attack_tree_structured(6)
    new_root = ADNode('a', 'new_root', 'AND')
    new_ref = ADNode('a', 'ref_7', 'OR')
    d = T.dict
    d[new_root] = [T.root, new_ref]
    d[new_ref] = [ADNode('a', 12 + i)
                  for i in range(1, m + 1) for j in range(2)]
    for child in d[new_ref]:
        d[child] = []
    return ADTree(dictionary=d)


def post_tree():
    '''
    Tree from the POST talk, together with the basic assignment of cost.
    '''
    root = ADNode('a', 'root', 'AND')
    leftchild = ADNode('a', 'left', 'OR')
    midchild = ADNode('a', 'mid', 'OR')
    rightchild = ADNode('a', 'c')

    d = {root: [leftchild, midchild, rightchild]}
    d[leftchild] = [ADNode('a', 'a'), ADNode('a', 'b')]
    for node in d[leftchild]:
        d[node] = []
    d[rightchild] = []

    lastref = ADNode('a', 'ref', 'AND')
    lastnonref = ADNode('a', 'b')
    d[midchild] = [lastref, lastnonref]
    d[lastnonref] = []
    d[lastref] = [ADNode('a', 'd'), ADNode('a', 'c')]
    for node in d[lastref]:
        d[node] = []

    T = ADTree(dictionary=d)

    ba = BasicAssignment()
    ba['a'] = 10
    ba['b'] = 16
    ba['c'] = 10
    ba['d'] = 5

    return (T, ba)


if __name__ == '__main__':
    pass
