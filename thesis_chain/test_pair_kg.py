"""Registered inverse and declared-source proof obligations."""
import unittest
from fractions import Fraction
from .pair_kg import compile_linear_contrast as compile

class RegisteredReferenceTests(unittest.TestCase):
    def setUp(self):
        self.XR=[[1],[1]]
        self.XE=[[1]]
        self.F1=[[1,0]]
        self.F2=[[0,1]]
        self.RR=[[1],[1]]
        self.RE=[[1]]

    def test_registered_completion_and_source_both_hold(self):
        a=compile(self.XR,self.XE,self.F1,[2,2],[3],[1],
                  self.RR,self.RE,require_source=True)
        b=compile(self.XR,self.XE,self.F2,[2,2],[3],[1],
                  self.RR,self.RE,require_source=True)
        self.assertEqual(a.readout,Fraction(1))
        self.assertEqual(a.readout,b.readout)
        self.assertTrue(a.declared_source_qualified)
        self.assertEqual(a.reference_weights,(Fraction(1),Fraction(0)))
        self.assertEqual(b.reference_weights,(Fraction(0),Fraction(1)))

    def test_completion_bound_not_automatically_completion_invariant(self):
        a=compile(self.XR,self.XE,self.F1,[2,5],[3],[1])
        b=compile(self.XR,self.XE,self.F2,[2,5],[3],[1])
        self.assertEqual(a.readout,Fraction(1))
        self.assertEqual(b.readout,Fraction(-2))
        self.assertNotEqual(a.readout,b.readout)
        self.assertFalse(a.declared_source_qualified)

    def test_reject_invalid_registered_inverse(self):
        with self.assertRaises(ValueError):
            compile(self.XR,self.XE,[[1,1]],[2,2],[3],[1])
    def test_reject_unestimable_query(self):
        with self.assertRaises(ValueError):
            compile([[1,0],[1,0]],[[0,1]],[[1,0],[0,0]],[2,2],[3],[1])
    def test_reject_ungrounded_source(self):
        with self.assertRaises(ValueError):
            compile(self.XR,self.XE,self.F2,[2,2],[3],[1],
                    [[1],[0]],self.RE,require_source=True)
        with self.assertRaises(ValueError):
            compile(self.XR,self.XE,self.F1,[2,2],[3],[1],require_source=True)
    def test_reject_missing_source_map_half(self):
        with self.assertRaises(ValueError):
            compile(self.XR,self.XE,self.F1,[2,2],[3],[1],R_R=self.RR)
    def test_refuse_nonrectangular_shapes(self):
        with self.assertRaises(ValueError):
            compile([[1],[1,0]],self.XE,self.F1,[2,2],[3],[1])
        with self.assertRaises(ValueError):
            compile(self.XR,self.XE,[[1,0,1]],[2,2],[3],[1])

if __name__=="__main__":
    unittest.main()
