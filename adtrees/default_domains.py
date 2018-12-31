from adtrees.attribute_domain import AttrDomain
from adtrees.utils import combine_bundles, listunion, otimes, odot

minCost = AttrDomain(min, lambda x, y: x + y)

maxDamage = AttrDomain(max, lambda x, y: x + y)

minSkillLvl = AttrDomain(min, max)

minDiff = AttrDomain(min, max)

setSemSize = AttrDomain(lambda x, y: x + y, lambda x, y: x * y)

# set semantics
setSem = AttrDomain(listunion, combine_bundles)

# <-- for defense semantics
# attack strategies in trees with no repeated basic actions
attStrat = AttrDomain(listunion, otimes, lambda A, B: listunion(
    listunion(A, B), otimes(A, B)), listunion, otimes, listunion)

countStrats = AttrDomain(listunion, otimes, otimes, listunion, otimes, odot)
# -->
