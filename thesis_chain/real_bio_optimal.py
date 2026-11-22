"""Independent native-PPI exact purchase-cost validation.

Run in CI against PINNED public original ISMB R8 source and original HuRI/Y2H
inputs. This is NOT a claim of better online policy performance or new data.
Reformulates action-certification as exact covering MILP from the *typed*
contract, compares nominal minima with original R8 oracle and verifies every
nominal / one-group-fault selected witness with the separate core certifier.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp

from .core import (action_classes, robust_erasure, robust_one_cell_flip,
                   statement)
from .real_bio import build_contract, load_original


def find_minimum(X, y, win, rivals, fault_radius=0):
    """For a single binary HC label per purchased group.

    For rival b: initial lower bound L0 = sum_i min(0,w_a-w_b).
    Each bought true label gives nonnegative integer gain in {0,1}.
    For r arbitrary already purchased group changes, sharp condition
    L0 + gains @ x >= r+1, since each fault loses at most one unit.
    This reduction is NOT valid for grouped multi-label scores!
    """
    if fault_radius not in (0,1):
        raise ValueError("this producer supports only 0 or 1 unit faults")
    n=X.shape[0]
    D=np.stack([X[:,win].astype(np.int64)-X[:,b].astype(np.int64)
                for b in rivals],axis=0)
    initial=np.minimum(D,0).sum(axis=1)
    gains=D*y[np.newaxis,:]-np.minimum(D,0)
    if not np.all((gains==0)|(gains==1)):
        raise AssertionError("gain not single-label unit")
    constraint=LinearConstraint(gains.astype(float),
                                (fault_radius+1-initial).astype(float),
                                np.full(len(rivals),np.inf))
    out=milp(c=np.ones(n),integrality=np.ones(n,dtype=int),
             bounds=Bounds(np.zeros(n),np.ones(n)),
             constraints=constraint,
             options={"mip_rel_gap":0.0,"time_limit":60.0})
    if out.status==2:  # Infeasible even with complete public archive
        return None,[]
    if not out.success or out.status!=0 or out.mip_gap>1e-9:
        raise AssertionError(("MILP_not_proven_optimal",out.status,out.message))
    selected=np.flatnonzero(out.x>0.5).tolist()
    if len(selected)!=int(round(out.fun)):
        raise AssertionError("bad MILP objective/selected witness")
    return int(round(out.fun)),selected


def run(root:Path,tie_seed=0):
    original=load_original(root)
    panels,receipts=original.read_native()
    out=[]
    counts={"source_panels":len(panels),"strict_action_classes":0,
            "nominal_minima_original_equals_independent":0,
            "robust_single_group_feasible":0,
            "robust_single_group_impossible_even_full":0,
            "nominal_original_witness_valid":0,
            "nominal_independent_witness_valid":0,
            "robust_independent_witness_valid":0,
            "independent_oracle_exhaustive_small":0}
    for panel in panels:
        X=original.design(panel,tie_seed);y=panel["y"]
        contract,archive=build_contract(panel,X,y)
        classes=action_classes(contract)
        winners=[cl for cl in classes
                 if statement(contract,archive.buy(tuple(g.key for g in contract.groups)),
                              "strict_action",cl[0])]
        if len(winners)>1:
            raise AssertionError("two distinct strict action classes")
        if not winners:
            continue
        counts["strict_action_classes"]+=1
        win=contract.models.index(winners[0][0])
        rivals=[contract.models.index(cl[0]) for cl in classes if cl != winners[0]]
        native_cost,native_selected=original.offline_cover_oracle(X,y)
        our_cost,our_selected=find_minimum(X,y,win,rivals,0)
        if native_cost != our_cost:
            raise AssertionError(("native vs independent cost",panel["id"],native_cost,our_cost))
        counts["nominal_minima_original_equals_independent"]+=1
        for chosen,which in ((native_selected,"native"),(our_selected,"independent")):
            paid=tuple("query_%05d"%i for i in chosen)
            ev=archive.buy(paid)
            if not statement(contract,ev,"strict_action",winners[0][0]):
                raise AssertionError(("false_nominal_witness",panel["id"],which))
            counts["nominal_"+("original" if which=="native" else "independent")+"_witness_valid"]+=1
        robust_cost,robust_selected=find_minimum(X,y,win,rivals,1)
        full_keys=tuple(g.key for g in contract.groups)
        full_valid=robust_erasure(contract,archive.buy(full_keys),full_keys,
                                  "strict_action",winners[0][0],radius=1)
        if robust_cost is None:
            if full_valid:
                raise AssertionError(("robust supposedly infeasible but complete is robust",panel["id"]))
            counts["robust_single_group_impossible_even_full"]+=1
        else:
            paid=tuple("query_%05d"%i for i in robust_selected)
            e=archive.buy(paid)
            if not robust_erasure(contract,e,paid,"strict_action",winners[0][0],radius=1):
                raise AssertionError(("false_robust_witness",panel["id"]))
            # One purchased scalar binary flip and one arbitrary paid group
            # replacement are the same fault model ONLY for singleton groups.
            if not robust_one_cell_flip(contract,e,"strict_action",winners[0][0]):
                raise AssertionError(("single_cell_disagreement",panel["id"]))
            if not full_valid:
                raise AssertionError(("full board not robust although subset robust",panel["id"]))
            if robust_cost < our_cost:
                raise AssertionError(("robust cheaper than nominal",panel["id"]))
            counts["robust_single_group_feasible"]+=1
            counts["robust_independent_witness_valid"]+=1
        out.append({"panel":panel["id"],"eligible_slots":int(X.shape[0]),
                    "n_model_action_classes":len(classes),
                    "native_nominal_cost":native_cost,
                    "independent_nominal_cost":our_cost,
                    "independent_single_group_robust_cost":robust_cost,
                    "fullboard_single_group_robust":full_valid})
    if len(panels)!=71 or counts["strict_action_classes"]!=15:
        raise AssertionError(("original source panel/winner mismatch",counts))
    return {"status":"PASS_OR_RAISE","source":"SHA-pinned public HuRI/Y2H original R8",
            "eligibility_receipts":receipts["inputs"],
            "scope":"15 strict action winners, nominal exact ILP original vs independent, singleton-group robust exact ILP",
            "not_claimed":"The full Bio neural model or multi-stream ACL 21-board MILP is not replayed",
            "counts":counts,"panels":out}


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bio-root",required=True,type=Path)
    p.add_argument("--report",required=True,type=Path)
    args=p.parse_args()
    z=run(args.bio_root)
    args.report.parent.mkdir(exist_ok=True,parents=True)
    args.report.write_text(json.dumps(z,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in z.items() if k!="panels"},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
