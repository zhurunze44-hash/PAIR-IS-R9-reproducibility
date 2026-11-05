#!/usr/bin/env python3
"""Unit tests using synthetic numbers only; never a native data certificate."""
import importlib.util, tempfile
from pathlib import Path
import numpy as np
m=Path(__file__).with_name('G0_G2_native_fair_baseline.py')
spec=importlib.util.spec_from_file_location('g0g2',m)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp)/'constructed.npz'
    XR=np.array([[1,1,1],[1,1,0],[1,0,1],[1,0,0]],float)
    YE=np.array([10,6,7,5],float)
    YR=np.array([4,7,8,4],float)
    XE=XR.copy()
    a=np.array([1,-1,-1,1],float)
    F=np.linalg.pinv(XR)
    rr=np.array([[4],[0],[1],[1]],float)
    re=np.ones((4,1))*2
    np.savez(p,XR=XR,XE=XE,F=F,YR=YR,YE=YE,a=a,RR=rr,RE=re,
             ref_ids=np.array(['r1','r2','r3','r4']),eval_ids=np.array(['e1','e2','e3','e4']),
             source_ids=np.array(['shared_control']))
    row={"query_id":"SYNTHETIC_Q4","query_type":"CONSTRUCTED_Q4",
         "reference_row_ids":['r1','r2','r3','r4'],
         "request_row_ids":['e1','e2','e3','e4'],
         "ordered_source_ids":['shared_control'],
         "historical_status":"CONSTRUCTED_ACCEPTED",
         "original_status_to_standard":{"CONSTRUCTED_ACCEPTED":"QUALIFIED"},
         "historical_value":2.0}
    got=mod.compute_one(p,row,{"absolute":1e-9,"relative":1e-9})
    assert got['computed_status']=='QUALIFIED' and got['a_XE_inf']<1e-10
    assert got['source_residual_inf']<1e-10 and got['value_classical']==2.
    # Correctly refuse malformed ordered sources.
    bad={**row,"ordered_source_ids":['NOT_THE_ACTUAL_SOURCE']}
    try:mod.compute_one(p,bad,{"absolute":1e-9,"relative":1e-9})
    except ValueError as e:assert "identit" in str(e).lower()
    else:raise AssertionError("Source identity mismatch not detected")
    # Correctly refuse a deliberately wrong historical numerical label.
    bad={**row,"historical_value":200.0}
    try:mod.compute_one(p,bad,{"absolute":1e-9,"relative":1e-9})
    except ValueError as e:assert "value disagrees" in str(e)
    else:raise AssertionError("Wrong producer result not detected")
print('PASS_CONSTRUCTED_ONLY: legal Q4 + source-ID mismatch + historical-value mismatch')
