from tree_factory import get_tree
from tree_factory import attack_defense_tree_structured

n = 15
m = 6
T = get_tree(n)
T2 = attack_defense_tree_structured(m)


def test_contains_clones_no_clones():
    assert T.contains_clones() == False


def test_order():
    assert T.order() == 2 * n + 7


def test_basic_actions_size():
    assert len(T.basic_actions()) == 2 * n + 4


def test_basic_actions_content():
    actual = [int(i) for i in T.basic_actions()]
    actual.sort()
    expected = [i for i in range(1, 2 * n + 5)]
    assert actual == expected


def test_basic_actions_content_d():
    actual = [int(i) for i in T.basic_actions('d')]
    actual.sort()
    expected = [i for i in range(n + 1, 2 * n + 3)]
    assert actual == expected


def test_basic_actions_content_a():
    actual = [int(i) for i in T.basic_actions('a')]
    actual.sort()
    expected = [i for i in range(1, n + 1)]
    expected.append(2 * n + 3)
    expected.append(2 * n + 4)
    assert actual == expected


def test_children():
    root = T.root
    children = T.children(root)
    actual_labels = [child.label for child in children if child.type == 'a']
    expected_labels = [str(i) for i in range(1, n + 1)]
    actual_labels.sort()
    expected_labels.sort()
    assert actual_labels == expected_labels


def test_countermered():
    assert T.countered(T.root) == True


def test_countermeasure():
    assert T.counter(T.root).label == 'X'


def test_set_semantics():
    expected_set_semantics = [[set([str(i)]), set(
        [str(n + i), str(2 * n + 1), str(2 * n + 2)])] for i in range(1, n + 1)]
    also = [[set([str(i), str(2 * n + 3), str(2 * n + 4)]),
             set([str(n + i)])] for i in range(1, n + 1)]
    expected_set_semantics.extend(also)
    actual_set_semantics = T.set_semantics()
    for item in actual_set_semantics:
        assert item in expected_set_semantics
        assert actual_set_semantics.count(item) == 1
    for item in expected_set_semantics:
        assert item in actual_set_semantics


def test_def_semantics():
    expected_def_sem = []
    for i in range(1, n + 1):
        expected_def_sem.append([set([str(i)]), set([str(n + i)])])
        expected_def_sem.append([set([str(i)]), set([str(2 * n + 1)])])
        expected_def_sem.append([set([str(i)]), set([str(2 * n + 2)])])
        expected_def_sem.append(
            [set([str(i), str(2 * n + 3), str(2 * n + 4)]), set([str(n + i)])])
    actual_def_sem = T.defense_semantics()
    for item in actual_def_sem:
        assert item in expected_def_sem
        assert actual_def_sem.count(item) == 1
    for item in expected_def_sem:
        assert item in actual_def_sem


def test_extremal_tree_set_semantics():
    set_sem = T2.set_semantics()
    expected_set_sem_size = 2**(2 * m)
    actual_set_sem_size = len(set_sem)
    assert expected_set_sem_size == actual_set_sem_size


def test_extremal_tree_def_semantics():
    def_sem = T2.defense_semantics()
    expected_def_sem_size = (2 * m) * 2**(2 * m - 2)
    actual_def_sem_size = len(def_sem)
    assert expected_def_sem_size == actual_def_sem_size
