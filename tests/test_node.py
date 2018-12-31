from adtrees import ADNode


def test_initialize_node():
    n = ADNode(actor='a', label='string label')
    n = ADNode(actor='a', label=5)
    n = ADNode(actor='a', label=[1, 2])


def test_initialize_node_failed_actor():
    n = ADNode(actor='x')
    try:
        m = str(n)
        flag = False
    except AttributeError:
        flag = True
    assert flag == True


def test_initialize_node_failed_refinement():
    n = ADNode(actor='d', refinement='XOR')
    try:
        m = str(n)
        flag = False
    except AttributeError:
        flag = True
    assert flag == True


def test_refinement_non_refined():
    n = ADNode(actor='a', label='string label')
    assert n.ref == ''


def test_refinement_refined():
    n = ADNode(actor='a', label='string label', refinement='OR')
    assert n.ref == 'OR'


def test_string_label():
    n = ADNode(actor='a', label='string label')
    assert n.label == 'string label'


def test_nonstring_label():
    n = ADNode(actor='a', label=5)
    assert n.label == '5'


def test_isbasic():
    n1 = ADNode(actor='a', label='string label')
    n2 = ADNode(actor='a', label='string label', refinement='AND')
    assert n1.isbasic() == True
    assert n2.isbasic() == False


def test_repr():
    n1 = ADNode(actor='a', label='string label')
    n2 = ADNode(actor='a', label=4, refinement='OR')
    assert n1.__repr__() == '(a, string label, NonRef)'
    assert n2.__repr__() == '(a, 4, OR)'
