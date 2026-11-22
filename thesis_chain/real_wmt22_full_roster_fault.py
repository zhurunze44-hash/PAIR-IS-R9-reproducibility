"""Full TWELVE-model real WMT22 independent ternary group-fault impossibility.

No 12-model MILP optimum asserted. This is an exact obstruction using the
complete published aligned human record: if the full-data strict common
winner has a pair margin 1, altering a paid positive vote in that pair
decreases the realized comparison margin by 2. Under monotone information
and arbitrary one-group replacement, no purchased subset can certify a
one-group-fault-robust strict winner for that fixed model.
"""
import argparse,json
from pathlib import Path
from .real_wmt22 import prepare,build,MODEL
from .core import Evidence,statement,pair_interval


def run(root):
    roster,scores,indices,pins,margins=prepare(root,max_models=None)
    if len(roster)!=12 or len(indices)!=207:
        raise AssertionError("not 12-model 207 matched real records")
    win=roster.index(MODEL)
    c,archive=build(roster,scores,shared=True)
    paid=tuple(g.key for g in c.groups)
    e=archive.buy(paid)
    if not statement(c,e,"strict_model",MODEL):
        raise AssertionError("full 12-model common winner false")
    p,b=min(margins,key=lambda pair:margins[pair])
    D=margins[p,b]
    if D!=1:
        raise AssertionError(("expected source-verified narrow full margin not one",D))
    candidate=next((i for i in range(len(indices))
                    if scores[p,i,win]>scores[p,i,b]),None)
    if candidate is None:
        raise AssertionError("cannot find a paid positive score comparison")
    a,bb=sorted((win,b))
    key=f"p{p}_i{candidate}_a{a}_b{bb}"
    before=e.values[key]
    flipped_vote = -1 if win==a else 1
    if before == flipped_vote:
        raise AssertionError("chosen vote is not a positive winning vote")
    changed=dict(e.values);changed[key]=flipped_vote
    edited=Evidence(changed)
    if statement(c,edited,"strict_model",MODEL):
        raise AssertionError("one group fault did not break the claimed winner")
    pair_before=pair_interval(c,e,f"P{p}",win,b)
    pair_after=pair_interval(c,edited,f"P{p}",win,b)
    if pair_before!=(1,1) or pair_after!=(-1,-1):
        raise AssertionError(("unexpected exact margin before/after",pair_before,pair_after))
    return {
        "status":"PASS_OR_RAISE",
        "scope":"full 12 models, both published WMT22 ESA-1/MQM-1 protocols, 207 source-aligned complete items",
        "winner":MODEL,
        "strict_common_full_archive":True,
        "minimum_full_pairwise_margin":D,
        "decisive_protocol":f"P{p}",
        "decisive_rival":roster[b],
        "one_paid_group_identity":f"item{candidate}",
        "changed_vote_slot":key,
        "original_pair_margin":pair_before[0],
        "post_one_group_legal_replacement_margin":pair_after[0],
        "robust_fullboard":False,
        "robust_any_subset_impossible":True,
        "proof":"Any subset certificate is weaker than the full archive. Arbitrary one-group replacement includes a group containing a paid winning vote. Changing that vote +1 to -1 creates a legal full-world pair margin -1; hence every purchased subset is non-robust.",
        "not_claimed":"full 12-model exact minimum nominal purchase cost; full private ACL2027 original dataset",
        "original_files":pins,
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--upstream-root",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()
    z=run(args.upstream_root)
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(z,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(z,ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
