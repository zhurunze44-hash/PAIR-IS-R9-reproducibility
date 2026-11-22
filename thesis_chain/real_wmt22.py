"""Independent real-human WMT22 en-de two-protocol ACL ternary audit.

Uses two officially released human score streams from an ACL 2025 public
repository: ESA-1 and MQM-1, 207 fully aligned segments and 12 systems
(excluding reference). NOT the WMT24 447-segment primary experiment.
All data are fetched from source during CI, with pinned Git code/source IDs.
No third-party ratings are committed to this repository.
"""
import argparse,collections,hashlib,itertools,json
from pathlib import Path
import numpy as np
from scipy.optimize import milp,Bounds,LinearConstraint
from .core import Contract,Slot,Group,Archive,Evidence,statement,pair_interval

EXPECTED_GIT_BLOBS={
    "en-de.ESA-1.seg.score":"d4b9bbd8b1d4e60ade00d7ffc7c57ddbe3410b01",
    "en-de.MQM-1.seg.score":"1ad64fb1f91f14c83f05b9e745ca19bd0c77423a",
}
MODEL="GPT4-5shot"

def source_bytes_check(path):
    b=path.read_bytes()
    actual=hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()
    if actual != EXPECTED_GIT_BLOBS[path.name]:
        raise AssertionError(("upstream source changed",path.name,actual))
    return {"git_blob_sha1":actual,"sha256":hashlib.sha256(b).hexdigest(),
            "bytes":len(b)}

def parse(path):
    d=collections.defaultdict(list)
    for line in path.read_text(encoding="utf-8").splitlines():
        p=line.strip().split()
        if len(p)!=2:raise ValueError(("malformed human score line",path.name,line[:60]))
        model,val=p
        d[model].append(None if val=="None" else float(val))
    if len(d)!=13 or set(map(len,d.values()))!={557}:
        raise AssertionError(("official format unexpected",path.name,
                              len(d),{k:len(v) for k,v in d.items()}))
    return d

def prepare(root):
    base=root/"data"/"annotations"/"wmt22"/"en-de"
    files=[base/name for name in EXPECTED_GIT_BLOBS]
    pins={p.name:source_bytes_check(p) for p in files}
    data=[parse(p) for p in files]
    roster=sorted(set(data[0]) & set(data[1]) - {"refA"})
    if len(roster)!=12 or MODEL not in roster:
        raise AssertionError(("frozen model roster mismatch",roster))
    if set(data[0])!=set(data[1]):
        raise AssertionError("protocol roster changed")
    shared_indices=[i for i in range(557)
                    if all(data[p][m][i] is not None
                           for p in range(2) for m in roster)]
    if len(shared_indices)!=207:
        raise AssertionError(("aligned common complete items mismatch",len(shared_indices)))
    scores=np.array([[[data[p][m][i] for m in roster] for i in shared_indices]
                     for p in range(2)])
    n=len(shared_indices);m=len(roster);w=roster.index(MODEL)
    # Ternary winner margin under two *measured* human protocols.
    margins={}
    for p in range(2):
        for a in range(m):
            if a==w:continue
            v=np.sign(scores[p,:,w]-scores[p,:,a]).astype(int)
            margins[(p,a)]=int(np.sum(v))
    if min(margins.values())<=0:
        raise AssertionError(("common strict winner unexpectedly absent",min(margins.values())))
    return roster,scores,shared_indices,pins,margins

def build(roster,scores,shared):
    n=scores.shape[1];m=len(roster)
    pairs=tuple(itertools.combinations(range(m),2))
    slots=[];truth={}
    bucket=collections.defaultdict(list)
    for p in range(2):
        for i in range(n):
            for a,b in pairs:
                key=f"p{p}_i{i}_a{a}_b{b}"
                slots.append(Slot(key,f"P{p}","independent_ternary_pair",(a,b)))
                truth[key]=int(scores[p,i,a]>scores[p,i,b])-int(scores[p,i,a]<scores[p,i,b])
                bucket[(p,i)].append(key)
    if shared:
        groups=tuple(Group(f"item{i}",tuple(bucket[(p,i)][j]
                     for p in range(2) for j in range(len(pairs))),1) for i in range(n))
    else:
        groups=tuple(Group(f"p{p}_item{i}",tuple(bucket[(p,i)]),1)
                     for p in range(2) for i in range(n))
    c=Contract("frozen-WMT22-ESA1-MQM1",
               "SapienzaNLP/ACL2025 human parity public scores",
               "strict Condorcet winner over independent ternary pair completions",
               tuple(roster),("P0","P1"),tuple(slots),groups)
    return c,Archive(c,truth)

def cost_matrix(c,scores,win):
    n=scores.shape[1];m=scores.shape[2]
    rivals=[j for j in range(m) if j!=win]
    matrix=np.zeros((2*len(rivals),len(c.groups)))
    rowlabels=[]
    for p in range(2):
        for rr,b in enumerate(rivals):
            row=p*len(rivals)+rr
            rowlabels.append((p,b))
            d=np.sign(scores[p,:,win]-scores[p,:,b]).astype(int)
            gains=(d+1).astype(float)
            for i in range(n):
                key=f"item{i}" if len(c.groups)==n else f"p{p}_item{i}"
                index=list(c.group_map).index(key)
                matrix[row,index]=gains[i]
    return matrix,rowlabels

def exact_cost(c,scores,win):
    A,rows=cost_matrix(c,scores,win)
    n=scores.shape[1]
    out=milp(c=np.array([g.price for g in c.groups],dtype=float),
             integrality=np.ones(len(c.groups),dtype=int),
             bounds=Bounds(np.zeros(len(c.groups)),np.ones(len(c.groups))),
             constraints=LinearConstraint(A,np.full(len(rows),n+1.0),
                                          np.full(len(rows),np.inf)),
             options={"mip_rel_gap":0.0,"time_limit":120.0})
    if not out.success or out.status!=0 or out.mip_gap>1e-8:
        raise AssertionError(("real WMT exact solver not globally certified",
                              out.status,out.message,getattr(out,"mip_gap",None)))
    selected=tuple(g.key for g,x in zip(c.groups,out.x) if x>0.5)
    cost=int(round(float(out.fun)))
    if len(selected)!=cost:
        raise AssertionError("unit-cost gap")
    if not np.all(A @ np.array([int(g.key in selected) for g in c.groups])
                  >=n+1-1e-8):
        raise AssertionError("numerical witness fails direct linear check")
    return cost,selected,float(out.mip_gap),A

def chronological(c,a,scores,win):
    A,rows=cost_matrix(c,scores,win)
    n=scores.shape[1];totals=np.zeros(len(rows))
    chosen=[]
    for j,g in enumerate(c.groups):
        totals+=A[:,j];chosen.append(g.key)
        if np.all(totals>=n+1):
            e=a.buy(chosen)
            if not statement(c,e,"strict_model",MODEL):
                raise AssertionError("algebraic prefix claim not certified")
            if statement(c,a.buy(chosen[:-1]),"strict_model",MODEL):
                raise AssertionError("prefix not earliest")
            return len(chosen)
    raise AssertionError("full original scores did not reach strict winner")

def run(root):
    roster,scores,shared_indices,pins,margins=prepare(root)
    win=roster.index(MODEL)
    result={"status":"PASS_OR_RAISE","scope":"official released WMT22 en-de ESA-1 vs MQM-1, NOT WMT24/21 frozen ACL targets",
            "upstream_git_repo":"SapienzaNLP/human-parity-mt-eval",
            "upstream_commit":"542fafa2a69d4434413a6cc53bacca6956382da5",
            "source_files":pins,"eligible_aligned_segments":len(shared_indices),
            "model_roster":roster,"strict_common_model":MODEL,
            "full_pairwise_min_margin":min(margins.values()),
            "billing_contracts":{}}
    for shared in (True,False):
        c,a=build(roster,scores,shared)
        full=a.buy(tuple(g.key for g in c.groups))
        if not statement(c,full,"strict_model",MODEL):
            raise AssertionError(("false full strict winner",shared))
        if statement(c,full,"no_common"):
            raise AssertionError(("mis-certified no common winner",shared))
        cost,chosen,gap,A=exact_cost(c,scores,win)
        ev=a.buy(chosen)
        if not statement(c,ev,"strict_model",MODEL):
            raise AssertionError(("false optimal witness",shared))
        chronological_cost=chronological(c,a,scores,win)
        if chronological_cost<cost:
            raise AssertionError("online fixed-order cost beat certified hindsight optimum")
        # A score-tie or barely positive full margin defeats one group
        # robustness under the independent ternary pair completion.
        cand=None
        for (p,b),D in margins.items():
            if D<=1:
                d=np.sign(scores[p,:,win]-scores[p,:,b]).astype(int)
                index=next((i for i,x in enumerate(d) if x==1),None)
                if index is not None:
                    cand=f"item{index}" if shared else f"p{p}_item{index}"
                    break
        if cand is not None:
            remaining=[g.key for g in c.groups if g.key!=cand]
            if statement(c,a.buy(remaining),"strict_model",MODEL):
                raise AssertionError(("fault witness contradicted",cand))
        result["billing_contracts"]["shared" if shared else "separate"]={
            "price":cost,"mip_gap":gap,"optimal_group_count":len(chosen),
            "chronological_first_certificate_group_count":chronological_cost,
            "number_of_available_groups":len(c.groups),
            "observed_vote_cells":len(c.slots),
            "one_group_fault_counterexample":cand,
            "robust_fullboard_if_candidate_exists":False if cand else None}
    q=result["billing_contracts"]
    if not (q["shared"]["price"] <= q["separate"]["price"] <= 2*q["shared"]["price"]):
        raise AssertionError("separate/shared price theorem failed")
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--upstream-root",required=True,type=Path)
    ap.add_argument("--report",required=True,type=Path)
    args=ap.parse_args()
    result=run(args.upstream_root)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))

if __name__=="__main__":
    main()
