"""Exact independent ternary pair-vote tests for the ACTUAL ACL proof alphabet.

A measured multi-model score vector yields pair votes in {-1,0,1}.
Unpurchased PAIR votes are independently completable under the explicitly
declared relaxation. This is NOT equivalent to completing one shared
transitive score vector; that scope distinction is a scientific requirement.
"""
import itertools,random,unittest
from .core import (Archive,Contract,Evidence,Group,Slot,action_classes,
                   hindsight_min_cost,no_common_strict_winner,pair_interval,
                   robust_erasure,robust_one_cell_flip,statement)

def build(scores):
    # scores[protocol][item][model]
    p=len(scores);n=len(scores[0]);m=len(scores[0][0])
    pairs=list(itertools.combinations(range(m),2))
    slots=[];groups=[];truth={}
    for ip in range(p):
        for i in range(n):
            keys=[]
            for a,b in pairs:
                key="v%d_%d_%d_%d"%(ip,i,a,b)
                keys.append(key)
                slots.append(Slot(key,"P%d"%ip,"independent_ternary_pair",(a,b)))
                truth[key]=int(scores[ip][i][a]>scores[ip][i][b])-int(scores[ip][i][a]<scores[ip][i][b])
            groups.append(Group("g%d_%d"%(ip,i),tuple(keys)))
    c=Contract("ACL-ternary-pair-v1","published human score-derived comparisons",
               "independent pair-vote winner",tuple("m%d"%i for i in range(m)),
               tuple("P%d"%ip for ip in range(p)),tuple(slots),tuple(groups))
    return c,Archive(c,truth)

def worlds(c,e):
    missing=[s for s in c.slots if s.key not in e.values]
    for vals in itertools.product((-1,0,1),repeat=len(missing)):
        w=dict(e.values);w.update(zip((s.key for s in missing),vals))
        yield w

def margin(c,w,p,a,b):
    return sum((v if (a,b)==slot.actions else -v if (b,a)==slot.actions else 0)
               for slot in c.slots if slot.protocol==p
               for v in [w[slot.key]])

def exact_brute(c,e,kind,model=None):
    if kind=="strict_model":
        a=c.models.index(model)
        return all(all(margin(c,w,p,a,b)>0 for p in c.protocols
                       for b in range(len(c.models)) if b!=a) for w in worlds(c,e))
    if kind=="no_common":
        return all(not any(all(margin(c,w,p,a,b)>0 for p in c.protocols
                           for b in range(len(c.models)) if b!=a)
                           for a in range(len(c.models))) for w in worlds(c,e))
    raise ValueError(kind)

class ACLTernaryTests(unittest.TestCase):
    def test_full_exhaustive_worlds_and_proposition(self):
        random.seed(1230)
        for m in (2,3):
            for _ in range(20):
                s=[[[random.randrange(3) for j in range(m)]] for p in range(2)]
                c,arch=build(s)
                e=arch.buy(tuple(g.key for g in c.groups if random.randrange(2)))
                for p in c.protocols:
                    for a,b in itertools.combinations(range(m),2):
                        vals=[margin(c,w,p,a,b) for w in worlds(c,e)]
                        self.assertEqual(pair_interval(c,e,p,a,b),(min(vals),max(vals)))
                self.assertEqual(no_common_strict_winner(c,e),
                                 exact_brute(c,e,"no_common"))
                for mname in c.models:
                    self.assertEqual(statement(c,e,"strict_model",mname),
                                     exact_brute(c,e,"strict_model",mname))

    def test_complete_item_group_is_multiple_pair_votes(self):
        c,arch=build([[[2,1,0]],[[0,1,2]]])
        self.assertEqual(len(c.groups),2)
        self.assertEqual(len(c.groups[0].slots),3)
        e=arch.buy((c.groups[0].key,))
        self.assertEqual(len(e.values),3)
        self.assertEqual(pair_interval(c,e,"P0",0,1),(1,1))
        self.assertEqual(pair_interval(c,e,"P1",0,1),(-1,1))
        with self.assertRaises(ValueError):
            robust_one_cell_flip(c,e,"no_common")

    def test_no_common_minimum_and_group_fault(self):
        c,a=build([[[0,0],[0,0]],[[0,0],[0,0]]])
        self.assertEqual(hindsight_min_cost(c,a,"no_common")["cost"],2)
        self.assertEqual(hindsight_min_cost(c,a,"no_common",group_fault=1)["cost"],4)

    def test_group_erasure_equals_all_ternary_replacements(self):
        c,a=build([[[1,0,0]],[[0,1,0]]])
        for mask in range(4):
            chosen=tuple(g.key for i,g in enumerate(c.groups) if mask>>i&1)
            e=a.buy(chosen)
            ans=robust_erasure(c,e,chosen,"no_common",radius=1)
            brute=statement(c,e,"no_common")
            for key in chosen:
                slotkeys=c.group_map[key].slots
                for vals in itertools.product((-1,0,1),repeat=len(slotkeys)):
                    d=dict(e.values);d.update(zip(slotkeys,vals))
                    brute=brute and statement(c,Evidence(d),"no_common")
            self.assertEqual(ans,brute)

    def test_pair_vote_independence_does_not_mean_transitive_scores(self):
        c,arch=build([[[2,1,0]]])
        e=Evidence({"v0_0_0_1":1,  # a>b
                    "v0_0_0_2":-1, # c>a
                    "v0_0_1_2":1}) # b>c: directed cycle
        self.assertTrue(statement(c,e,"no_common"))
        # This is intentionally LEGAL ONLY under independent pair-vote
        # completion, not as a realizable three-score ranking.

    def test_invalid_ternary_rejected(self):
        c,a=build([[[2,1,0]]])
        with self.assertRaises(ValueError):
            statement(c,Evidence({"v0_0_0_1":5}),"no_common")
        with self.assertRaises(ValueError):
            Contract("v","s","t",("a","b","c"),("P",),
                     (Slot("s","P","independent_ternary_pair",(2,0)),),
                     (Group("g",("s",)),))
if __name__=="__main__":
    unittest.main()
