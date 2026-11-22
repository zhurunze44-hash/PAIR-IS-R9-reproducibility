"""Original buyer and independent complement MILP must agree on tiny exact panels."""
import unittest
import numpy as np
from .core import hindsight_min_cost,statement
from .real_wmt22 import build,exact_cost

class ExactHumanMILPTests(unittest.TestCase):
    def test_shared_vs_separate_exact_trivial_no_loss(self):
        scores=np.array([[[2,1,0],[2,1,0]],[[2,0,1],[2,0,1]]],dtype=float)
        roster=["GPT4-5shot","B","C"]
        for shared in (True,False):
            c,a=build(roster,scores,shared)
            target="GPT4-5shot"; win=0
            oracle=hindsight_min_cost(c,a,"strict_model",target)
            minimum,groups,gap,A=exact_cost(c,scores,win)
            self.assertEqual(minimum,oracle["cost"])
            self.assertEqual(minimum,2 if shared else 4)
            self.assertLess(gap,1e-8)
            self.assertTrue(statement(c,a.buy(groups),"strict_model",target))
            for candidate_group in groups:
                smaller=tuple(g for g in groups if g!=candidate_group)
                self.assertFalse(statement(c,a.buy(smaller),"strict_model",target))

    def test_complement_nontrivial_tie_and_defeat(self):
        scores=np.array([[[2,0,1],[2,1,0],[0,1,0],[2,0,0]],
                         [[2,1,0],[1,1,0],[2,1,1],[2,0,1]]],dtype=float)
        roster=["GPT4-5shot","B","C"]
        for shared in (True,False):
            c,a=build(roster,scores,shared)
            full=a.buy(tuple(g.key for g in c.groups))
            self.assertTrue(statement(c,full,"strict_model","GPT4-5shot"))
            brute=hindsight_min_cost(c,a,"strict_model","GPT4-5shot")
            value,groups,gap,A=exact_cost(c,scores,0)
            self.assertEqual(value,brute["cost"])
            self.assertTrue(statement(c,a.buy(groups),"strict_model","GPT4-5shot"))
            self.assertLess(gap,1e-8)

if __name__=="__main__":
    unittest.main()
