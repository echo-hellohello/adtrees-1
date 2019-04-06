from adtrees.adnode import ADNode
import xml.etree.cElementTree as ET


def file_to_dict(path):
    """
    Path to an ADTool .xml output file --> dictionary for the ADTree creation.
    """
    try:
        with open(path, 'rt') as f:
            tree = ET.parse(f)
    except FileNotFoundError:
        raise(
            "Couldn't load ADTree from {}\nThere is no such file or directory.".format(path))
        return
    realRoot = tree.getroot()[0]
    pt = 'a'  # the root is assummed to be of the attacker's type
    ETnodesLeft = [realRoot]
    ADNodesLeft = [getADNode(realRoot, pt)]
    # ETnodesLeft[i] corresponds to the ADNodesLeft[i]
    d = {ADNodesLeft[0]: []}

    while ADNodesLeft != []:
        # take the first of the nodes that are left
        currentET = ETnodesLeft[0]
        currentADN = ADNodesLeft[0]
        # take its children in the ET, turn them into ADNodes,
        # add them to the ADTree's dictionary and to the two lists
        # of nodes left to deal with
        pt = currentADN.type
        for child in currentET:
            if child.tag == 'node':
                ADchild = getADNode(child, pt)
                # modify the dictionary and the lists
                d[currentADN].append(ADchild)
                d[ADchild] = []
                ETnodesLeft.append(child)
                ADNodesLeft.append(ADchild)
        # current has beend dealt with
        ETnodesLeft.pop(0)
        ADNodesLeft.pop(0)
    return d


def getADNode(ETnode, pt):
    """
    pt = parent type, 'a' or 'd'
    """
    types = ['a', 'd']
    # todo: initial checks
    # the first child is the label, i.e., ETnode[0].tag = 'label'
    label = ETnode[0].text.replace('\n', ' ')
    # the first three children are either
    # label parameter
    # or
    # label parameter node
    # or
    # label node node
    # If any of the two first cases occurs, we are dealing with a non-refined
    # node.
    if len(ETnode.getchildren()) <= 2 or ETnode[1].tag == 'parameter':
        ref = None
    else:
        ref = ETnode.attrib['refinement']
        if ref == 'conjunctive':
            ref = 'AND'
        else:
            ref = 'OR'
    # type
    if 'switchRole' in ETnode.attrib:
        # this means that switchRole = "yes"; this node counters its parent
        type = types[(types.index(pt) + 1) % 2]
    else:
        type = pt
    return ADNode(actor=type, label=label, refinement=ref)


def getAssignment(path):
    """
    Path to an ADTool .xml output file --> dictionary containing the basic assignment.
    """
    try:
        with open(path, 'rt') as f:
            tree = ET.parse(f)
    except FileNotFoundError:
        print(
            "Couldn't load the basic assignment from {}\nThere is no such file or directory.".format(path))
        return
    realRoot = tree.getroot()[0]
    result = {}
    ETnodesLeft = [realRoot]
    while ETnodesLeft != []:
        currentET = ETnodesLeft[0]
        if len(currentET.getchildren()) > 1 and currentET[1].tag == 'parameter':
            label = str(currentET[0].text).replace('\n', ' ')
            if label not in result:
                val = currentET[1].text
                # val most probably looks like '10.0'
                result[label] = float(val)  # int(val.split('.')[0])
        for child in currentET:
            if child.tag == 'node':
                ETnodesLeft.append(child)
        ETnodesLeft.pop(0)
    return result
