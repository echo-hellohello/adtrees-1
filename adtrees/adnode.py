class ADNode:
    """
    Representation of a node of an attack-defense tree. Building block for
    objects of the ADTree class.

    class ADNode(self, actor, label, refinement)

    Parameters
    ----------
    actor : {'a', 'd'}, default 'a'
        Value describing which actor's goal/basic action the node represents.
        'a' for a node of the attacker, 'd' for a node of the defender.
    label : string, default 'NoName'
        Name of a goal/basic action the node represents.
    refinement : {'AND', 'OR', None}, default None
        'AND' for a conjunctively refined node, 'OR' for a disjunctively refined
        node, None for a basic action.

    Examples
    ----------
    >>> x = ADNode('a', 'break in', 'OR')
    >>> x1 = ADNode('a', 'break in through the back door')
    >>> x2 = ADNode('a', 'break in through one of the windows')
    >>> y1 = ADNode('d', 'install lock on the back door')
    """

    def __init__(self, actor='a', label='NoName', refinement=None):
        """
        initialize self.

        type, label, ref

        """
        super(ADNode, self).__init__()
        # check whether the parameters provided are OK.
        # actor
        if actor not in ['a', 'd']:
            print('Invalid actor: {}'.format(actor))
            help(ADNode)
            return
        self.type = actor
        # label
        try:
            self.label = str(label)
        except:
            print('Invalid label.')
            help(ADNode)
            return

        # refinement
        if refinement in ['AND', 'OR']:
            self.ref = refinement
        elif refinement == None:
            self.ref = ''
        else:
            print('Invalid refinement: {}'.format(refinement))
            help(ADNode)
            return

    def copy(self):
        """
        Return a copy of the node.
        """
        return ADNode(self.type, self.label, self.ref)

    def isbasic(self):
        """
        True iff the node represents a basic action, i.e., if it is not
        refined.
        """
        return self.ref == ''

    def __repr__(self):
        """
        """
        if self.ref == '':
            return '({}, {}, {})'.format(self.type, self.label, 'NonRef')
        return '({}, {}, {})'.format(self.type, self.label, self.ref)
