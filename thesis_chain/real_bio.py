"""Real-data interface verification on frozen, SHA-pinned HuRI/Y2H PPI source.

Requirements: checked-out public ISMB structural release and its two original
public inputs. NO private P3 checkpoints, labels or unconsented publications.
This compares the exact original R8 certifier against thesis_chain.core,
not merely the same result printed twice.
"""
import argparse
import importlib.util
import json
from pathlib import Path
from .core import Contract,Slot,Group,Archive,statement,pair_interval


def load_original(bio_root: Path):
    path=bio_root/"ISMB"/"r8"/"analysis"/"strict_winner_experiment"/"reanalyze_strict_winners.py"
    if not path.exists():
        raise FileNotFoundError(path)
    spec=importlib.util.spec_from_file_location("original_paper3_r8",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_contract(panel, X, y):
    n,m=X.shape
    slots=tuple(Slot("cand_%05d"%i,"frozen_Y2H","shared_binary",
                     tuple(int(v) for v in X[i])) for i in range(n))
    groups=tuple(Group("query_%05d"%i,("cand_%05d"%i,)) for i in range(n))
    contract=Contract("R8-frozen-huri-y2h", "pinned_HuRI_Y2H_structural",
                      "HC@10 frozen nominations",tuple(("AA","CN","RA","Jaccard","DegreeProduct")),
                      ("frozen_Y2H",),slots,groups)
    archive=Archive(contract,{"cand_%05d"%i:int(y[i]) for i in range(n)})
    return contract,archive


def execute(bio_root: Path, tie_seed=0):
    orig=load_original(bio_root)
    panels,meta=orig.read_native()
    if len(panels)!=71:
        raise AssertionError("native panel count mismatch")
    examined=0;checks=0;max_abs_error=0
    observed_cases=(0,3,10,"full")
    per_panel=[]
    for panel in panels:
        X=orig.design(panel,tie_seed)
        y=panel["y"]
        contract,archive=build_contract(panel,X,y)
        panel_checks=0
        for budget in observed_cases:
            n=X.shape[0]
            # Fixed public sequential order: it is a *test of the certifier*,
            # NOT a claim of a policy gain; original and adapter see same prefix.
            shown=range(n) if budget=="full" else range(min(n,budget))
            obs={int(i):int(y[i]) for i in shown}
            e=archive.buy(tuple("query_%05d"%i for i in shown))
            result=orig.certify(X,obs)
            for j,name in enumerate(contract.models):
                got=statement(contract,e,"strict_model",name)
                if got!=bool(j in result["strict_model"]):
                    raise AssertionError(("model",panel["id"],budget,name,got))
                ag=statement(contract,e,"strict_action",name)
                cl=result["groups"]
                want=bool(any(j in member for kk,member in enumerate(cl) if kk in result["strict_action"]))
                if ag !=want:
                    raise AssertionError(("action",panel["id"],budget,name,ag,want))
                panel_checks+=2
            for a in range(len(contract.models)):
                for b in range(len(contract.models)):
                    if a==b:continue
                    l,u=pair_interval(contract,e,"frozen_Y2H",a,b)
                    oldl,oldu=int(result["low"][a,b]),int(result["up"][a,b])
                    if (l,u)!=(oldl,oldu):
                        raise AssertionError(("pair",panel["id"],budget,a,b,l,u,oldl,oldu))
                    panel_checks+=2
        per_panel.append({"panel":panel["id"],"checks":panel_checks})
        checks+=panel_checks;examined+=1
    report={"status":"PASS_OR_RAISE","scope":"original real public 71 Y2H panels structural scores; no native neural producers",
            "public_input_receipts":meta.get("inputs"),"panels":examined,
            "certifier_comparisons":checks,"tie_seed":tie_seed,
            "observation_budgets":[0,3,10,"full"],"per_panel":per_panel,
            "original_certifier":"ISMB/r8/analysis/strict_winner_experiment/reanalyze_strict_winners.py",
            "adapter_certifier":"thesis_chain/core.py",
            "different_frozen_inputs":False,
            "no_new_qualifying_reference_geometry":True,
            "no_online_policy_gain_claim":True}
    return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--bio-root",type=Path,required=True)
    parser.add_argument("--report",type=Path)
    args=parser.parse_args()
    report=execute(args.bio_root)
    summary={k:v for k,v in report.items() if k!="per_panel"}
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")

if __name__=="__main__":
    main()
