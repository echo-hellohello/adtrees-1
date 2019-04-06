from adtrees.attribute_domain import AttrDomain
from adtrees.utils import combine_bundles, listunion, otimes, odot
from adtrees.utils import oplus, oplushat

satisfiability = AttrDomain(max, min, max, min, lambda x, y: min(
    x, (y + 1) % 2), lambda x, y: min(x, (y + 1) % 2))

minCost = AttrDomain(min, lambda x, y: x + y)

maxDamage = AttrDomain(max, lambda x, y: x + y)

minSkillLvl = AttrDomain(min, max)

minDiff = AttrDomain(min, max)

setSemSize = AttrDomain(lambda x, y: x + y, lambda x, y: x * y)

maxProb = AttrDomain(max, lambda x, y: x * y)

# set semantics
setSem = AttrDomain(listunion, combine_bundles)

# <-- for defense semantics
# attack strategies in trees with no repeated basic actions
attStrat = AttrDomain(listunion, otimes, oplushat,
                      listunion, otimes, listunion)

# witnesses for trees with repeated basic actions
suffWit = AttrDomain(oplushat, oplushat, oplushat, otimes, oplushat, oplus)

countStrats = AttrDomain(listunion, otimes, otimes, listunion, otimes, odot)
# -->
