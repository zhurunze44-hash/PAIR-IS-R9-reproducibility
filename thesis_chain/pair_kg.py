"""Full registered-reference local witness for a genuine PAIR-KG linear design.

This is intentionally SEPARATE from the PPI assay HC label adapter: Y2H
negative/positive labels do not imply a classical X_R, F_R reference design.
No historical native K562 source certification is claimed by this helper.
"""
from __future__ import annotations
from dataclasses import dataclass
from fractions import Fraction


def M(x,name):
    try:
        out=tuple(tuple(Fraction(a) for a in row) for row in x)
        if not out or not out[0] or any(len(row)!=len(out[0]) for row in out):
            raise ValueError(name+" must be rectangular and nonempty")
        return out
    except (TypeError,ZeroDivisionError) as e:
        raise ValueError(name+" has invalid entries") from e


def prod(A,B):
    if len(A[0])!=len(B):
        raise ValueError("matmul dimensions incompatible")
    return tuple(tuple(sum(A[i][k]*B[k][j] for k in range(len(B)))
                       for j in range(len(B[0]))) for i in range(len(A)))


@dataclass(frozen=True)
class LocalWitness:
    readout: Fraction
    reference_weights: tuple[Fraction,...]
    contrast_response: tuple[Fraction,...]
    reference_generalized_inverse_valid: bool
    estimable: bool
    declared_source_qualified: bool
    completion_bound: bool


def compile_linear_contrast(
    X_R, X_E, F_R, Y_R, Y_E, a,
    R_R=None, R_E=None, *, require_source=False
):
    """Construct and verify h = (a^T X_E) F_R, with X_R F_R X_R = X_R.

    Inexact floating-point matrices become exact rational representations
    of their INPUT byte values (Fraction(float)); for true numerical
    approximate input use a separate explicitly bounded tolerance gate.
    Here all inputs are expected to be exact integers or fractions.
    """
    XR=M(X_R,"X_R"); XE=M(X_E,"X_E"); FR=M(F_R,"F_R")
    nR=len(XR);nE=len(XE);p=len(XR[0])
    if len(XE[0])!=p or len(FR)!=p or len(FR[0])!=nR:
        raise ValueError("reference design / inverse shape")
    yr=M([[v] for v in Y_R],"Y_R")
    ye=M([[v] for v in Y_E],"Y_E")
    av=M([a],"contrast")
    if len(av[0])!=nE or len(yr)!=nR or len(ye)!=nE:
        raise ValueError("response or contrast wrong dimension")
    if prod(prod(XR,FR),XR)!=XR:
        raise ValueError("declared inverse fails X_R F_R X_R = X_R")
    coeff=prod(av,XE)
    h=prod(coeff,FR)
    if prod(h,XR)!=coeff:
        raise ValueError("query is not reference-estimable under declared X_R")
    if (R_R is None)!=(R_E is None):
        raise ValueError("source matrices must be jointly specified")
    qualified=False
    if R_R is not None:
        RR=M(R_R,"R_R");RE=M(R_E,"R_E")
        if len(RR)!=nR or len(RE)!=nE or len(RR[0])!=len(RE[0]):
            raise ValueError("source design dimensions")
        if prod(av,RE)!=prod(h,RR):
            raise ValueError("declared source-cancellation witness failed")
        qualified=True
    if require_source and not qualified:
        raise ValueError("source qualification required but not declared")
    z=prod(av,ye)[0][0]-prod(h,yr)[0][0]
    return LocalWitness(z,h[0],coeff[0],True,True,qualified,True)
