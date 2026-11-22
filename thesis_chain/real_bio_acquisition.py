"""True end-to-end original public PPI data -> strict certificate -> paid prefix.

A deterministic public candidate ordering is used. It is not a new adaptive
policy and is not an optimal acquisition claim. Uses the SAME certifier as
thesis_chain.real_bio and small-board price demonstrator.
"""
import argparse, json
from pathlib import Path
from .real_bio import load_original, build_contract
from .core import statement, online_replay, robust_erasure


def execute(root: Path, tie_seed=0):
    native=load_original(root)
    panels,meta=native.read_native()
    counters={"panels":0,"strict_model_winners":0,"strict_action_winners":0,
              "verified_prefix_certificates":0,"verified_group_robust_prefixes":0,
              "fullboard_group_robust_winners":0,"total_prefix_spend":0}
    details=[]
    for panel in panels:
        X=native.design(panel,tie_seed);c,archive=build_contract(panel,X,panel["y"])
        full_paid=tuple(g.key for g in c.groups)
        all_labels=archive.buy(full_paid)
        model_winners=[m for m in c.models if statement(c,all_labels,"strict_model",m)]
        action_winners=[m for m in c.models if statement(c,all_labels,"strict_action",m)]
        counters["panels"]+=1;counters["strict_model_winners"]+=len(model_winners)
        counters["strict_action_winners"]+=len(action_winners)
        # This is a fixed, pre-label purchase order from the frozen source
        # candidate index, with no access to labels before purchase.
        records=[]
        for kind,winners in (("strict_model",model_winners),("strict_action",action_winners)):
            for model in winners:
                r=online_replay(c,archive,full_paid,kind,model)
                if not r["certificate"]:
                    raise AssertionError(("certified full board but online missed it",panel["id"],kind,model))
                subset=archive.buy(r["paid"])
                if not statement(c,subset,kind,model):
                    raise AssertionError(("invalid early certificate",panel["id"],kind,model))
                # Verify no earlier prefix would have certified. This checks
                # actual stopping and non-anticipating paid-prefix evidence.
                if r["paid"]:
                    earlier=archive.buy(r["paid"][:-1])
                    if statement(c,earlier,kind,model):
                        raise AssertionError(("stopped after first certificate",panel["id"],kind,model))
                group_robust=robust_erasure(c,subset,r["paid"],kind,model,1)
                if group_robust:
                    counters["verified_group_robust_prefixes"]+=1
                full_robust=robust_erasure(c,all_labels,full_paid,kind,model,1)
                if full_robust:
                    counters["fullboard_group_robust_winners"]+=1
                counters["verified_prefix_certificates"]+=1
                counters["total_prefix_spend"]+=r["cost"]
                records.append({"kind":kind,"winner":model,"first_certificate_paid":r["cost"],
                                "total_eligible_groups":len(full_paid),
                                "one_group_robust_at_prefix":group_robust,
                                "one_group_robust_fullboard":full_robust})
        details.append({"panel":panel["id"],"group_count":len(full_paid),"records":records})
    if counters["panels"]!=71:
        raise AssertionError(counters["panels"])
    return {"status":"PASS_OR_RAISE","scope":"pinned real public PPI structural-score panels",
            "label_source":"official published two files pinned by Git SHA and SHA256",
            "price_contract":"one candidate-label group costs one; shared across models",
            "purchase_rule":"fixed eligible candidate order, not adaptive",
            "count_basis":"model identities counted separately from action classes",
            "no_retrospective_optimality_claim":True,
            "no_prospective_data_claim":True,
            "counts":counters,"panels":details}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--bio-root",type=Path,required=True)
    ap.add_argument("--report",type=Path,required=True)
    args=ap.parse_args()
    report=execute(args.bio_root)
    args.report.parent.mkdir(exist_ok=True,parents=True)
    args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps({k:v for k,v in report.items() if k!="panels"},ensure_ascii=False,indent=2))
if __name__=="__main__":
    main()
