"""Constructed finite-world correctness tests for the thesis bridge."""
import itertools, random, unittest
from .core import (Contract, Group, Slot, Evidence, Archive, action_classes,
                   pair_reference_witness, pair_interval, statement, hindsight_min_cost,
                   online_replay, robust_erasure, robust_one_cell_flip)

def bio(actions, labels):
    slots=tuple(Slot("s%d"%i, "PPI", "shared_binary", tuple(a)) for i,a in enumerate(actions))
    groups=tuple(Group("g%d"%i,("s%d"%i,)) for i in range(len(slots)))
    c=Contract("v1","pinned synthetic assay","HC top-k",tuple("m%d"%i for i in range(len(actions[0]))),("PPI",),slots,groups)
    return c,Archive(c,{"s%d"%i:z for i,z in enumerate(labels)})

def human(scores):
    n=len(scores[0]);m=len(scores[0][0]);p=len(scores)
    slots=tuple(Slot("s%d_%d"%(j,i),"P%d"%j,"independent_binary") for j in range(p) for i in range(n))
    groups=tuple(Group("g%d_%d"%(j,i),("s%d_%d"%(j,i),)) for j in range(p) for i in range(n))
    c=Contract("v1","human synthetic","strict sum",tuple("m%d"%i for i in range(m)),
               tuple("P%d"%i for i in range(p)),slots,groups)
    return c,Archive(c,{"s%d_%d"%(j,i):tuple(scores[j][i]) for j in range(p) for i in range(n)})

def worlds(c,e):
    miss=[s for s in c.slots if s.key not in e.values]
    domains=[(0,1) if s.kind=="shared_binary" else tuple(itertools.product((0,1),repeat=len(c.models))) for s in miss]
    for values in itertools.product(*domains):
        d=dict(e.values);d.update({s.key:v for s,v in zip(miss,values)})
        yield d

def contrast(c,d,p,a,b):
    return sum((s.actions[a]-s.actions[b])*d[s.key] if s.kind=="shared_binary" else
               d[s.key][a]-d[s.key][b] for s in c.slots if s.protocol==p)

def expected(c,e,kind,model=None):
    ws=list(worlds(c,e))
    if kind=="strict_model":
        a=c.models.index(model)
        return all(all(contrast(c,w,p,a,b)>0 for p in c.protocols for b in range(len(c.models)) if a!=b) for w in ws)
    if kind=="strict_action":
        classes=action_classes(c)
        if len(classes)<2:return False
        a=c.models.index(next(cl[0] for cl in classes if model in cl))
        others=[c.models.index(cl[0]) for cl in classes if model not in cl]
        return all(all(contrast(c,w,p,a,b)>0 for p in c.protocols for b in others) for w in ws)
    if kind=="no_common":
        return all(not any(all(contrast(c,w,p,a,b)>0 for p in c.protocols
                               for b in range(len(c.models)) if b!=a)
                               for a in range(len(c.models))) for w in ws)
    raise ValueError(kind)

class Tests(unittest.TestCase):
    def test_pair_reference(self):
        x=[[1,1,1],[1,1,0],[1,0,1],[1,0,0]]
        self.assertEqual(pair_reference_witness(x,x,[1,-1,-1,1],[0]*4,
                                               [4,7,8,4],[10,6,7,5]),2)
        with self.assertRaises(ValueError):
            pair_reference_witness(x,x,[1,0,0,0],[0]*4,[4,7,8,4],[10,6,7,5])
    def test_eligibility(self):
        c,a=bio([(1,0)],[1])
        with self.assertRaises(ValueError):Archive(c,{"s0":None})
        with self.assertRaises(ValueError):
            Contract("v1","source","t",("A","B"),("P",),
                     (Slot("a","P","shared_binary",(1,0)),),(Group("g",("b",)),))
    def test_actions(self):
        c,a=bio([(1,1,0),(1,1,0),(0,0,1)],[1,1,0])
        e=a.buy(("g0","g1","g2"))
        self.assertEqual(action_classes(c),(("m0","m1"),("m2",)))
        self.assertFalse(statement(c,e,"strict_model","m0"))
        self.assertTrue(statement(c,e,"strict_action","m0"))
    def test_bio_worlds(self):
        random.seed(713)
        for n in (1,2,3):
            for _ in range(30):
                acts=[tuple(random.randrange(2) for j in range(3)) for i in range(n)]
                c,a=bio(acts,[random.randrange(2) for i in range(n)])
                e=a.buy(tuple("g%d"%i for i in range(n) if random.randrange(2)))
                for x,y in itertools.combinations(range(3),2):
                    vals=[contrast(c,w,"PPI",x,y) for w in worlds(c,e)]
                    self.assertEqual(pair_interval(c,e,"PPI",x,y),(min(vals),max(vals)))
                for m in c.models:
                    for kind in ("strict_model","strict_action"):
                        self.assertEqual(statement(c,e,kind,m),expected(c,e,kind,m))
    def test_human_worlds(self):
        random.seed(714)
        for n in (1,2):
            for _ in range(30):
                scores=[[[random.randrange(2) for k in range(3)] for i in range(n)] for j in range(2)]
                c,a=human(scores)
                e=a.buy(tuple(g.key for g in c.groups if random.randrange(2)))
                for x,y in itertools.combinations(range(3),2):
                    vals=[contrast(c,w,"P0",x,y) for w in worlds(c,e)]
                    self.assertEqual(pair_interval(c,e,"P0",x,y),(min(vals),max(vals)))
                self.assertEqual(statement(c,e,"no_common"),expected(c,e,"no_common"))
                for m in c.models:
                    self.assertEqual(statement(c,e,"strict_model",m),expected(c,e,"strict_model",m))
    def test_cost(self):
        for n in (1,2):
            c,a=human([[[0,0,0,0] for i in range(n)] for j in range(2)])
            self.assertEqual(hindsight_min_cost(c,a,"no_common")["cost"],n)
            self.assertEqual(hindsight_min_cost(c,a,"no_common",cell_flip=1)["cost"],2*n)
            self.assertEqual(hindsight_min_cost(c,a,"no_common",group_fault=1)["cost"],2*n)
    def test_online(self):
        c,a=bio([(1,0),(0,1),(1,0),(0,1)],[1,0,1,0])
        optimum=hindsight_min_cost(c,a,"strict_model","m0")
        online=online_replay(c,a,("g1","g3","g0","g2"),"strict_model","m0")
        self.assertTrue(optimum["certificate"])
        self.assertTrue(online["certificate"])
        self.assertGreaterEqual(online["cost"],optimum["cost"])
    def test_group_erasure_is_replacement(self):
        c,a=human([[[1,0],[1,0]],[[1,0],[1,0]]])
        for mask in range(1<<len(c.groups)):
            paid=tuple(g.key for i,g in enumerate(c.groups) if mask>>i&1)
            e=a.buy(paid)
            for kind,model in (("strict_model","m0"),("no_common",None)):
                exact=statement(c,e,kind,model)
                for key,value in e.values.items():
                    for v in itertools.product((0,1),repeat=2):
                        new=dict(e.values);new[key]=v
                        exact=exact and statement(c,Evidence(new),kind,model)
                self.assertEqual(robust_erasure(c,e,paid,kind,model),exact)

if __name__=="__main__":
    unittest.main()
