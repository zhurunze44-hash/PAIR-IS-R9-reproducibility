#!/usr/bin/env python3
"""Independent EXACT arithmetic checks for Paper2 R8 editorial theory.
No native research dataset is read. These are constructed algebraic tests, not biological experiments.
"""
from pathlib import Path
import json
from sympy import Matrix, Rational, eye, zeros

def vec(xs): return Matrix(xs)
def eq(A,B): return A==B

def score(a,XE,YR,YE,F,RR,RE):
    w=a.T*XE
    z=(a.T*YE-w*F*YR)[0]
    source=(a.T*RE-w*F*RR)
    return z, source

def is_col(X,V):
    if V.cols == 0: return True
    return Matrix.hstack(X,V).rank()==X.rank()

results={}
# Constructed mismatch in the R7 manuscript.
XR=vec([1,1]); XE=Matrix([[1]]); YR=vec([0,2]); YE=vec([3]); a=vec([1])
RR=vec([1,0]); RE=vec([1]); F1=Matrix([[1,0]]); F2=Matrix([[0,1]])
assert XR*F1*XR==XR and XR*F2*XR==XR
z1,j1=score(a,XE,YR,YE,F1,RR,RE); z2,j2=score(a,XE,YR,YE,F2,RR,RE)
assert (z1,z2,j1[0],j2[0])==(3,1,0,1)
results['completion_source_mismatch']={'z_F1':int(z1),'z_F2':int(z2),'J_F1':int(j1[0]),'J_F2':int(j2[0]),'type':'constructed_exact'}

# 2 x 2 strict additive contrast: w=0, hence F irrelevance for any F.
XE=Matrix([[1,1,1],[1,1,0],[1,0,1],[1,0,0]])
XR=XE.copy(); YE=vec([10,6,7,5]); YR=vec([4,7,8,4]); a=vec([1,-1,-1,1])
RR=vec([4,0,1,1]); RE=vec([2,2,2,2]); F_ols=(XR.T*XR).inv()*XR.T
v=vec([1,-1,-1,1]); assert XR.T*v==zeros(3,1)
F_alt=F_ols+vec([2,-1,4])*v.T
assert XR*F_ols*XR==XR and XR*F_alt*XR==XR
z1,j1=score(a,XE,YR,YE,F_ols,RR,RE); z2,j2=score(a,XE,YR,YE,F_alt,RR,RE)
assert a.T*XE==zeros(1,3)
assert z1==z2==2 and j1==j2==zeros(1,1)
results['strict_Q4_F_independence']={'w_zero':True,'z_both':int(z1),'declared_source_residual_both':0,'type':'constructed_exact'}
# Source gate can still bind if E source does not cancel directly.
RE2=vec([1,0,0,0]); z3,j3=score(a,XE,YR,YE,F_ols,RR,RE2)
assert j3[0]==1
results['strict_Q4_nonuniform_source']={'z':int(z3),'J':int(j3[0]),'source_refusal':True,'type':'constructed_exact'}

# Operator-independent example when Y_R and RR are in col(X_R).
XR=vec([1,1]); XE=Matrix([[1]]); YR=vec([2,2]); YE=vec([3]); a=vec([1]); RR=vec([1,1]); RE=vec([1]);
F1=Matrix([[1,0]]); F2=Matrix([[0,1]])
assert is_col(XR,Matrix.hstack(YR,RR))
z1,j1=score(a,XE,YR,YE,F1,RR,RE); z2,j2=score(a,XE,YR,YE,F2,RR,RE)
assert z1==z2==1 and j1==j2==zeros(1,1)
results['operator_robust_case']={'z_both':int(z1),'source_residual_both':0,'condition':True,'type':'constructed_exact'}

# Exhaust over integer-rational generalized-inverse family for 1-parameter reference.
XR=vec([1,1]); XE=Matrix([[1]]); a=vec([1]); YE=vec([3]);
for tag,YR,RR,RE,expected in [
    ('unbound_data',vec([0,2]),vec([1,0]),vec([1]),False),
    ('bound_column_data',vec([2,2]),vec([1,1]),vec([1]),True)]:
    V=Matrix.hstack(YR,RR)
    algebra=(a.T*XE==zeros(1,1) or is_col(XR,V))
    assert bool(algebra)==expected
    dat=[]
    for k in range(-4,5):
        F=Matrix([[Rational(k,2),1-Rational(k,2)]])
        assert XR*F*XR==XR
        z,j=score(a,XE,YR,YE,F,RR,RE)
        dat.append((str(z),str(j[0])))
    same=len(set(dat))==1
    assert same==expected
    results['completion_robust_theorem_'+tag]={'derived_criterion':bool(algebra),'grid_equal':same,'distinct_outputs':len(set(dat)),'type':'constructed_exact'}

# Scoring-task change without prediction advantage (R7 worked example).
y=vec([10,8]); pA=vec([0,-2]); pB=vec([9,9]);
Q=Matrix([[Rational(1,2),-Rational(1,2)],[-Rational(1,2),Rational(1,2)]])
full=lambda p: ((y-p).T*(y-p))[0]
projection=lambda p: ((Q*(y-p)).T*(Q*(y-p)))[0]
assert (full(pA),full(pB),projection(pA),projection(pB))==(200,2,0,2)
results['scoring_task_change']={'FULL_A':200,'FULL_B':2,'IDENT_A':0,'IDENT_B':2,'meaning':'different objectives, not predictive uplift','type':'constructed_exact'}

# Sympy synthetic structural check vs exact classical row-space for simple input.
XR=Matrix([[1,0],[1,0]]); XE=Matrix([[0,1],[0,1]])
nulls=XR.nullspace(); U=XE*Matrix.hstack(*nulls)
for a in [vec([1,0]),vec([0,1]),vec([1,-1])]:
    structural=(a.T*U==zeros(1,U.cols))
    classic=Matrix.vstack(XR,a.T*XE).rank()==XR.rank()
    assert structural==classic
results['exact_rowspace_classical_equivalence']={'tested_queries':3,'matching':3,'unique_algorithms_proven':0,'type':'constructed_exact'}

out=Path(__file__).with_name('constructed_theory_receipt.json')
out.write_text(json.dumps({'status':'PASS_CONSTRUCTED_ONLY','no_native_experimental_data':True,'not_a_performance_benchmark':True,'checks':results},ensure_ascii=False,indent=2),encoding='utf-8')
print(out)
print(json.dumps({'status':'PASS_CONSTRUCTED_ONLY','checks':list(results)},ensure_ascii=False))
