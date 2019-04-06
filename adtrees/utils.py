def powerset(seq):
    """
    Returns all the subsets of this set. This is a generator.

    Code by Rory McCann:
    https://www.technomancy.org/python/powerset-generator-python/
    """
    if len(seq) == 0:
        yield []
    elif len(seq) == 1:
        yield seq
        yield []
    else:
        for item in powerset(seq[1:]):
            yield [seq[0]] + item
            yield item


def combine_bundles(A, B):
    """
    Needed for set semantics.
    A = [[set, set], [set, set], ..., [set, set]]
    B = [[set, set], [set, set], ..., [set, set]]
    result
    """
    if len(A) > 0 and len(B) > 0:
        res = []
        for a in A:
            for b in B:
                candidate = [a[0].union(b[0]), a[1].union(b[1])]
                if candidate not in res:
                    res.append(candidate)
        # return [[a[0].union(b[0]), a[1].union(b[1])] for a in A for b in B]
        return res
    elif len(A) > len(B):
        return A
    elif len(B) != 0:
        return B
    else:
        return []


def listunion(A, B):
    """
    Needed for set semantics.
    """
    res = [x for x in A]
    for x in B:
        if x not in res:
            res.append(x)
    return res


def otimes(A, B):
    """
    """
    return [listunion(a, b) for a in A for b in B]


def odot(A, B):
    if A == [[]] or B == [[]]:
        return [[]]
    else:
        return listunion(A, B)


def oplus(A, B):
    return listunion(A, otimes(A, B))


def oplushat(A, B):
    return listunion(listunion(A, B), otimes(A, B))


def minimal_lists(L):
    '''
    Given list L of lists
        L = [L1, L2, L3, ..., Ln],
    return the minimal (inclusion-wise) lists from L.

    This is a generator.
    '''
    total = len(L)
    # select the minimal ones
    if total == 1:
        yield L[0]
    else:
        for i in range(total):
            candidate = L[i]
            minimal = True
            for j in range(total):
                if candidate == L[j]:
                    pass
                elif set(candidate).intersection(L[j]) == set(L[j]):
                    minimal = False
                    break
            if minimal:
                yield candidate

# GUI stuff follows


def read_val_from_grid(frame, row, column):
    '''
    An adaptation of https://stackoverflow.com/a/31034127

    Edit: If you wanted to get the values from the grid, you have to use the grid's children.

    Where you can call the function and it will return the child. To get the value of the entry, you can use:
        find_in_grid(root, i+1, j).get()
    '''
    for child in frame.children.values():
        info = child.grid_info()
        #
        try:
            x = (info['row'] == row) and (info['column'] == column)
            if x:
                return float(child.get())
        except KeyError:
            pass
    return None


def get_widget_from_grid(frame, row, column):
    '''
    An adaptation of https://stackoverflow.com/a/31034127

    Edit: If you wanted to get the values from the grid, you have to use the grid's children.

    Where you can call the function and it will return the child. To get the value of the entry, you can use:
        find_in_grid(root, i+1, j).get()
    '''
    for child in frame.children.values():
        info = child.grid_info()
        #
        try:
            x = (info['row'] == row) and (info['column'] == column)
            if x:
                return child
        except KeyError:
            pass
    return None
