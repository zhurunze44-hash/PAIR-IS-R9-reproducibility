"""Thesis method chain: PAIR-style evidence contract -> exact finite-board certificate
-> paid evidence/cell- or group-fault robustness.

This is a NEW integration adapter, not original PAIR or DecisionTransport code.
Scopes: additive binary shared-label actions (PPI) and independent binary
per-model human scores (ACL-style). No stochastic generalization guarantees.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from fractions import Fraction
from typing import Mapping

BINARY = (0, 1)


@dataclass(frozen=True)
class Slot:
    key: str
    protocol: str
    kind: str
    actions: tuple[int, ...] = ()

    def __post_init__(self):
        if not self.key or not self.protocol:
            raise ValueError("slot identity and protocol required")
        if self.kind not in ("shared_binary", "independent_binary"):
            raise ValueError("unsupported completion contract")


@dataclass(frozen=True)
class Group:
    key: str
    slots: tuple[str, ...]
    price: int = 1


@dataclass(frozen=True)
class Contract:
    """A versioned PAIR-Eval-style comparison contract.

    This is NOT a claim that a PPI HC label has a PAIR-KG reference matrix.
    Source qualification, scoring and missing-label semantics are independent
    gates and may not be silently substituted.
    """
    version: str
    source: str
    target: str
    models: tuple[str, ...]
    protocols: tuple[str, ...]
    slots: tuple[Slot, ...]
    groups: tuple[Group, ...]

    def __post_init__(self):
        if not self.version or not self.source or not self.target:
            raise ValueError("version, source, target required")
        if len(self.models) < 2 or len(set(self.models)) != len(self.models):
            raise ValueError("at least two uniquely named models required")
        if not self.protocols or len(set(self.protocols)) != len(self.protocols):
            raise ValueError("unique protocols required")
        ids = [s.key for s in self.slots]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError("unique nonempty evidence slots required")
        if len(set(g.key for g in self.groups)) != len(self.groups):
            raise ValueError("unique purchase groups required")
        seen = []
        for s in self.slots:
            if s.protocol not in self.protocols:
                raise ValueError("unknown protocol in slot")
            if s.kind == "shared_binary" and (
                    len(s.actions) != len(self.models) or
                    any(v not in BINARY for v in s.actions)):
                raise ValueError("shared-label action vectors must be binary")
            if s.kind == "independent_binary" and s.actions:
                raise ValueError("independent scores must not carry action vectors")
        for g in self.groups:
            if not g.key or not g.slots or g.price < 0:
                raise ValueError("bad group id/price/contents")
            seen.extend(g.slots)
        if sorted(seen) != sorted(ids):
            raise ValueError("each slot must belong to exactly one group")

    @property
    def slot_map(self):
        return {s.key: s for s in self.slots}

    @property
    def group_map(self):
        return {g.key: g for g in self.groups}


@dataclass(frozen=True)
class Evidence:
    """Only purchased labels; no true labels for unpurchased slots."""
    values: Mapping[str, object]

    def remove_groups(self, contract: Contract, group_keys):
        drop = {s for k in group_keys for s in contract.group_map[k].slots}
        return Evidence({k: v for k, v in self.values.items() if k not in drop})


class Archive:
    """Full frozen archive accessible to hindsight evaluator, NOT the certifier."""
    def __init__(self, contract: Contract, truth: Mapping[str, object]):
        if set(truth) != set(contract.slot_map):
            raise ValueError("full frozen archive must match eligible slots exactly")
        for key, value in truth.items():
            s = contract.slot_map[key]
            if s.kind == "shared_binary":
                if type(value) is not int or value not in BINARY:
                    raise ValueError("unqualified/unknown cannot be treated as HC negative")
            else:
                if not isinstance(value, (tuple, list)) or len(value) != len(contract.models):
                    raise ValueError("wrong human score vector")
                if any(type(t) is not int or t not in BINARY for t in value):
                    raise ValueError("human score outside declared alphabet")
        self._contract = contract
        self._truth = {k: (tuple(v) if isinstance(v, list) else v) for k, v in truth.items()}

    def buy(self, purchased):
        selected = set(purchased)
        if not selected <= set(self._contract.group_map):
            raise ValueError("unknown purchase group")
        slots = {s for key in selected for s in self._contract.group_map[key].slots}
        return Evidence({k: self._truth[k] for k in slots})


def pair_reference_witness(x_ref, x_eval, contrast, h, y_ref, y_eval,
                           r_ref=None, r_eval=None):
    """Exact rational PAIR-KG-style local reference/source witness check.

    This operation applies to a genuine additive reference design; it is
    separate from constructing an assay-qualified PPI evaluation contract.
    """
    F = lambda x: Fraction(x)
    xr = [[F(v) for v in row] for row in x_ref]
    xe = [[F(v) for v in row] for row in x_eval]
    a = [F(v) for v in contrast]
    hh = [F(v) for v in h]
    yr = [F(v) for v in y_ref]
    ye = [F(v) for v in y_eval]
    if not xr or not xe or len(a) != len(xe) or len(hh) != len(xr):
        raise ValueError("reference witness shape")
    if len(xr) != len(yr) or len(xe) != len(ye):
        raise ValueError("response shape")
    if len({len(row) for row in xr + xe}) != 1:
        raise ValueError("different design widths")
    for j in range(len(xr[0])):
        if sum(a[i] * xe[i][j] for i in range(len(xe))) != sum(
                hh[i] * xr[i][j] for i in range(len(xr))):
            raise ValueError("reference qualification failed")
    if (r_ref is None) != (r_eval is None):
        raise ValueError("source maps must be supplied together")
    if r_ref is not None:
        rr = [[F(v) for v in row] for row in r_ref]
        re = [[F(v) for v in row] for row in r_eval]
        if len(rr) != len(xr) or len(re) != len(xe):
            raise ValueError("source row shape")
        if len({len(row) for row in rr + re}) != 1:
            raise ValueError("source widths")
        for j in range(len(rr[0])):
            if sum(a[i] * re[i][j] for i in range(len(re))) != sum(
                    hh[i] * rr[i][j] for i in range(len(rr))):
                raise ValueError("declared-source cancellation failed")
    return sum(a[i] * ye[i] for i in range(len(a))) - sum(
        hh[i] * yr[i] for i in range(len(hh)))


def _check_evidence(contract: Contract, evidence: Evidence):
    if not set(evidence.values) <= set(contract.slot_map):
        raise ValueError("foreign evidence slot")


def pair_interval(contract: Contract, evidence: Evidence,
                  protocol: str, a: int, b: int):
    """Sharp contrast interval for the declared independent binary completions.

    The SAME unknown PPI label is shared across all models' action scores;
    a human-score slot has independently completable model cells.
    """
    _check_evidence(contract, evidence)
    if protocol not in contract.protocols or a == b:
        raise ValueError("unknown protocol or self comparison")
    lo = hi = 0
    for slot in contract.slots:
        if slot.protocol != protocol:
            continue
        if slot.key in evidence.values:
            v = evidence.values[slot.key]
            if slot.kind == "shared_binary":
                d = slot.actions[a] - slot.actions[b]
                lo += d * v
                hi += d * v
            else:
                d = v[a] - v[b]
                lo += d
                hi += d
        elif slot.kind == "shared_binary":
            d = slot.actions[a] - slot.actions[b]
            lo += min(0, d)
            hi += max(0, d)
        else:
            lo -= 1
            hi += 1
    return lo, hi


def strict_common_winner(contract: Contract, evidence: Evidence, model: str):
    """Model is strictly better than every competitor in every protocol,
    for all legal completion worlds."""
    a = contract.models.index(model)
    return all(pair_interval(contract, evidence, p, a, b)[0] > 0
               for p in contract.protocols for b in range(len(contract.models)) if a != b)


def action_classes(contract: Contract):
    """Identical frozen actions are one action, not two distinct competitors."""
    if any(s.kind != "shared_binary" for s in contract.slots):
        raise ValueError("action equivalence only for shared-label contracts")
    classes = {}
    for a, name in enumerate(contract.models):
        sig = tuple(s.actions[a] for s in contract.slots)
        classes.setdefault(sig, []).append(name)
    return tuple(tuple(group) for group in classes.values())


def strict_action_winner(contract: Contract, evidence: Evidence, model: str):
    classes = action_classes(contract)
    if len(classes) < 2:
        return False
    rep = next((cl[0] for cl in classes if model in cl), None)
    if rep is None:
        raise ValueError("unknown model")
    a = contract.models.index(rep)
    return all(pair_interval(contract, evidence, p, a, contract.models.index(cl[0]))[0] > 0
               for p in contract.protocols for cl in classes if cl[0] != rep)


def no_common_strict_winner(contract: Contract, evidence: Evidence):
    """Exact when all slots are independent per-model binary ratings.

    Not a valid exact equivalence for arbitrary coupled pairwise votes or
    shared-label PPI actions, so we reject those contracts here.
    """
    if any(s.kind != "independent_binary" for s in contract.slots):
        raise ValueError("no-common characterization requires independent score cells")
    for a in range(len(contract.models)):
        for_p = any(all(pair_interval(contract, evidence, p, a, b)[1] > 0
                        for b in range(len(contract.models)) if b != a)
                    for p in contract.protocols)
        # If a can win in EVERY protocol, a may be a common strict winner.
        if all(all(pair_interval(contract, evidence, p, a, b)[1] > 0
                   for b in range(len(contract.models)) if b != a)
               for p in contract.protocols):
            return False
    return True


def statement(contract: Contract, evidence: Evidence, kind: str, model=None):
    if kind == "strict_model":
        return strict_common_winner(contract, evidence, model)
    if kind == "strict_action":
        return strict_action_winner(contract, evidence, model)
    if kind == "no_common":
        return no_common_strict_winner(contract, evidence)
    raise ValueError("unknown statement")


def robust_erasure(contract: Contract, evidence: Evidence, paid, kind, model=None, radius=1):
    """Exact group-replacement robustness = all erasure subsets survive.

    True for *arbitrary replacement of all cells in up to r already paid
    groups* when legal completions factor over group cells. Cost not refunded.
    """
    paid = tuple(paid)
    if not statement(contract, evidence, kind, model):
        return False
    for n in range(1, min(radius, len(paid)) + 1):
        for removed in combinations(paid, n):
            if not statement(contract, evidence.remove_groups(contract, removed), kind, model):
                return False
    return True


def robust_one_cell_flip(contract: Contract, evidence: Evidence, kind, model=None):
    """Exact at most one already purchased binary scalar flip, not one group."""
    if not statement(contract, evidence, kind, model):
        return False
    for key, val in evidence.values.items():
        if type(val) is int:
            cand = [1 - val]
        else:
            cand = [tuple(1 - x if j == i else x for j, x in enumerate(val))
                    for i in range(len(val))]
        for alt in cand:
            vals = dict(evidence.values)
            vals[key] = alt
            if not statement(contract, Evidence(vals), kind, model):
                return False
    return True


def hindsight_min_cost(contract: Contract, archive: Archive, kind: str, model=None,
                       group_fault=0, cell_flip=0, max_groups=16):
    """Global exact enumeration for SMALL boards; refuses larger problems.

    Uses the full fixed archive only for the retrospective purchased labels.
    This is not an online acquisition algorithm or proof of any rate gain.
    """
    if len(contract.groups) > max_groups:
        raise ValueError("large-board exact solving requires an MILP/DP backend")
    if group_fault and cell_flip:
        raise ValueError("combine faults only under a separately declared contract")
    options = []
    for n in range(len(contract.groups) + 1):
        for chosen in combinations(contract.groups, n):
            paid = tuple(g.key for g in chosen)
            cost = sum(g.price for g in chosen)
            options.append((cost, paid))
    for cost, paid in sorted(options, key=lambda x: (x[0], len(x[1]), x[1])):
        ev = archive.buy(paid)
        if group_fault:
            ok = robust_erasure(contract, ev, paid, kind, model, radius=group_fault)
        elif cell_flip:
            if cell_flip != 1:
                raise ValueError("only one-cell flip implemented")
            ok = robust_one_cell_flip(contract, ev, kind, model)
        else:
            ok = statement(contract, ev, kind, model)
        if ok:
            return {"cost": cost, "paid": paid, "certificate": True,
                    "group_fault": group_fault, "cell_flip": cell_flip}
    return {"cost": None, "paid": (), "certificate": False,
            "group_fault": group_fault, "cell_flip": cell_flip}


def online_replay(contract: Contract, archive: Archive, order, kind, model=None):
    """Deterministic prefix replay using only the prefix-disclosed evidence."""
    paid = []
    for g in order:
        if g in paid or g not in contract.group_map:
            raise ValueError("nonunique or unknown group in purchase sequence")
        paid.append(g)
        e = archive.buy(paid)
        if statement(contract, e, kind, model):
            return {"cost": sum(contract.group_map[k].price for k in paid),
                    "paid": tuple(paid), "certificate": True}
    return {"cost": sum(contract.group_map[k].price for k in paid),
            "paid": tuple(paid), "certificate": False}
