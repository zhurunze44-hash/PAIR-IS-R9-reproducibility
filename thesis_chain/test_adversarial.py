"""Adversarial misuse checks: pass only if the integration bridge rejects invalid claims."""
import unittest
from .test_chain import bio, human
from .core import (Archive, Contract, Evidence, Group, Slot, hindsight_min_cost,
                   online_replay, pair_interval, robust_erasure, statement)

class NegativeEvidenceTests(unittest.TestCase):
    def test_forbid_forged_out_of_alphabet_positive(self):
        c,_=bio([(1,0)],[1])
        with self.assertRaises(ValueError):
            statement(c,Evidence({"s0":100}),"strict_model","m0")
        with self.assertRaises(ValueError):
            statement(c,Evidence({"s0":-1}),"strict_model","m0")
        with self.assertRaises(ValueError):
            statement(c,Evidence({"s0":"1"}),"strict_model","m0")

    def test_forbid_malformed_human_score_vectors(self):
        c,_=human([[[1,0]],[[0,1]]])
        for forged in ((1,0,0),(1,),("1",0),(1,3),False):
            with self.subTest(forged=forged):
                with self.assertRaises(ValueError):
                    statement(c,Evidence({"s0_0":forged}),"no_common")
    def test_wrong_purchase_claim_rejected(self):
        c,archive=bio([(1,0),(1,0)],[1,1])
        e=archive.buy(("g0","g1"))
        with self.assertRaises(ValueError):
            robust_erasure(c,e,("g0",),"strict_model","m0",radius=1)
        with self.assertRaises(ValueError):
            robust_erasure(c,e,(),"strict_model","m0",radius=1)
        with self.assertRaises(ValueError):
            robust_erasure(c,e,("g0","g0","g1"),"strict_model","m0",radius=1)
        with self.assertRaises(ValueError):
            robust_erasure(c,e,("not-a-group",),"strict_model","m0",radius=1)
    def test_unpaid_partial_bundle_rejected(self):
        c=Contract("v","public","binary",("a","b"),("P",),
                   (Slot("s1","P","shared_binary",(1,0)),
                    Slot("s2","P","shared_binary",(1,0))),
                   (Group("bundle",("s1","s2")),))
        e=Evidence({"s1":1})
        with self.assertRaises(ValueError):
            robust_erasure(c,e,("bundle",),"strict_model","a",radius=1)
    def test_bad_fault_radius_rejected(self):
        c,a=bio([(1,0)],[1]);e=a.buy(("g0",))
        for radius in (-1,1.5,False):
            with self.subTest(radius=radius):
                with self.assertRaises(ValueError):
                    robust_erasure(c,e,("g0",),"strict_model","m0",radius=radius)
        with self.assertRaises(ValueError):
            hindsight_min_cost(c,a,"strict_model","m0",group_fault=-1)
        with self.assertRaises(ValueError):
            hindsight_min_cost(c,a,"strict_model","m0",cell_flip=-1)
    def test_bad_indices_or_prices_rejected(self):
        c,a=bio([(1,0)],[1])
        e=a.buy(())
        for u,v in ((-1,1),(0,-1),(0,2),(False,1)):
            with self.assertRaises(ValueError):
                pair_interval(c,e,"PPI",u,v)
        with self.assertRaises(ValueError):
            Contract("v","src","t",("a","b"),("P",),
                     (Slot("s","P","shared_binary",(1,0)),),
                     (Group("g",("s",),price=-1),))
        with self.assertRaises(ValueError):
            Contract("v","src","t",("a","b"),("P",),
                     (Slot("s","P","shared_binary",(1,0)),),
                     (Group("g",("s",),price=1.5),))
    def test_mismatched_archive_binding(self):
        c,a=bio([(1,0)],[1])
        bad=Contract("different-version",c.source,c.target,c.models,c.protocols,c.slots,c.groups)
        with self.assertRaises(ValueError):
            hindsight_min_cost(bad,a,"strict_model","m0")
        with self.assertRaises(ValueError):
            online_replay(bad,a,("g0",),"strict_model","m0")
    def test_prefix_semantics_cannot_use_unseen_suffix(self):
        c,a=bio([(1,0),(0,1),(1,0),(0,1)],[1,0,1,0])
        future=Archive(c,{"s0":1,"s1":0,"s2":0,"s3":1})
        # Same acquired prefix, different future labels: all decisions equal.
        for length in (0,1,2):
            selected=tuple("g%d"%i for i in range(length))
            e1=a.buy(selected);e2=future.buy(selected)
            self.assertEqual(dict(e1.values),dict(e2.values))
            self.assertEqual(statement(c,e1,"strict_model","m0"),
                             statement(c,e2,"strict_model","m0"))

if __name__=="__main__":
    unittest.main()
