#!/usr/bin/env python3
"""Deterministic state helper for the Solaris Codex skill.

Maintains .solaris/plan.json using only the Python standard library.
It validates mission dependencies and guards obvious concurrent write-scope
collisions. It is intentionally small: Codex remains the orchestrator.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import sys
from pathlib import Path
from typing import Any

STATE_DIR = Path(".solaris")
PLAN = STATE_DIR / "plan.json"
VALID_STATUS = {"pending", "running", "passed", "failed", "blocked"}
VALID_RISK = {"normal", "high-uncertainty"}
VALID_EFFORT = {"high", "max"}


def die(msg: str, code: int = 2) -> None:
    print(f"ERROR: {msg}", file=sys.stderr)
    raise SystemExit(code)


def load() -> dict[str, Any]:
    if not PLAN.exists():
        die(f"{PLAN} does not exist; run init first")
    try:
        data = json.loads(PLAN.read_text(encoding="utf-8"))
    except Exception as exc:
        die(f"cannot parse {PLAN}: {exc}")
    if not isinstance(data, dict):
        die("plan root must be a JSON object")
    return data


def save(data: dict[str, Any]) -> None:
    """Atomically replace the plan so interrupted writes do not corrupt it."""
    STATE_DIR.mkdir(exist_ok=True)
    tmp = PLAN.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    os.replace(tmp, PLAN)


def mission_map(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    missions = data.get("missions", [])
    if not isinstance(missions, list):
        die("'missions' must be a list")
    out: dict[str, dict[str, Any]] = {}
    for mission in missions:
        if not isinstance(mission, dict) or not isinstance(mission.get("id"), str):
            die("every mission must be an object with string 'id'")
        mid = mission["id"].strip()
        if not mid:
            die("mission id cannot be empty")
        if mid in out:
            die(f"duplicate mission id: {mid}")
        out[mid] = mission
    return out


def static_prefix(pattern: str) -> str:
    """Return the literal prefix before the first common glob metacharacter."""
    cut = len(pattern)
    for ch in "*?[":
        pos = pattern.find(ch)
        if pos >= 0:
            cut = min(cut, pos)
    return pattern[:cut].rstrip("/")


def path_prefix_overlap(a: str, b: str) -> bool:
    """Conservatively detect obvious path/glob ownership overlap."""
    aa = static_prefix(a)
    bb = static_prefix(b)
    if not aa or not bb:
        return True
    return aa == bb or aa.startswith(bb + "/") or bb.startswith(aa + "/")


def validate(data: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if data.get("version") != 1:
        problems.append("plan version must be 1")
    if not isinstance(data.get("goal"), str) or not data.get("goal", "").strip():
        problems.append("plan goal must be a non-empty string")
    gates = data.get("global_gates", [])
    if not isinstance(gates, list) or not all(isinstance(x, str) for x in gates):
        problems.append("global_gates must be a list of strings")

    mm = mission_map(data)
    for mid, mission in mm.items():
        status = mission.get("status", "pending")
        if status not in VALID_STATUS:
            problems.append(f"{mid}: invalid status {status!r}")

        for field in ("title", "outcome"):
            if not isinstance(mission.get(field), str) or not mission.get(field, "").strip():
                problems.append(f"{mid}: {field} must be a non-empty string")

        deps = mission.get("depends_on", [])
        if not isinstance(deps, list) or not all(isinstance(x, str) for x in deps):
            problems.append(f"{mid}: depends_on must be a list of strings")
            deps = []
        for dep in deps:
            if dep not in mm:
                problems.append(f"{mid}: unknown dependency {dep!r}")
            if dep == mid:
                problems.append(f"{mid}: self dependency")

        ws = mission.get("write_scope", [])
        if not isinstance(ws, list) or not all(isinstance(x, str) and x.strip() for x in ws):
            problems.append(f"{mid}: write_scope must be a list of non-empty strings")

        risk = mission.get("risk", "normal")
        if risk not in VALID_RISK:
            problems.append(f"{mid}: risk must be one of {sorted(VALID_RISK)}")

        effort = mission.get("worker_effort", "high")
        if effort not in VALID_EFFORT:
            problems.append(f"{mid}: worker_effort must be high or max")

        acceptance = mission.get("acceptance", [])
        if not isinstance(acceptance, list) or not all(isinstance(x, str) for x in acceptance):
            problems.append(f"{mid}: acceptance must be a list of strings")

        targeted = mission.get("targeted_gates", [])
        if not isinstance(targeted, list) or not all(isinstance(x, str) for x in targeted):
            problems.append(f"{mid}: targeted_gates must be a list of strings")

    visiting: set[str] = set()
    done: set[str] = set()

    def dfs(mid: str, stack: list[str]) -> None:
        if mid in done:
            return
        if mid in visiting:
            problems.append("dependency cycle: " + " -> ".join(stack + [mid]))
            return
        visiting.add(mid)
        for dep in mm[mid].get("depends_on", []):
            if dep in mm:
                dfs(dep, stack + [mid])
        visiting.remove(mid)
        done.add(mid)

    for mid in mm:
        dfs(mid, [])

    running = [(mid, m) for mid, m in mm.items() if m.get("status") == "running"]
    for i, (aid, a) in enumerate(running):
        for bid, b in running[i + 1 :]:
            for ap in a.get("write_scope", []):
                for bp in b.get("write_scope", []):
                    if path_prefix_overlap(ap, bp):
                        problems.append(
                            f"running write-scope overlap: {aid}:{ap} <-> {bid}:{bp}"
                        )
    return problems


def ready(data: dict[str, Any]) -> list[dict[str, Any]]:
    mm = mission_map(data)
    out: list[dict[str, Any]] = []
    running = [m for m in mm.values() if m.get("status") == "running"]

    for mission in mm.values():
        if mission.get("status", "pending") != "pending":
            continue
        if any(mm.get(dep, {}).get("status") != "passed" for dep in mission.get("depends_on", [])):
            continue

        collision = any(
            path_prefix_overlap(candidate, active)
            for r in running
            for candidate in mission.get("write_scope", [])
            for active in r.get("write_scope", [])
        )
        if not collision:
            out.append(mission)
    return out


def validated_save(data: dict[str, Any]) -> None:
    problems = validate(data)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        raise SystemExit(1)
    save(data)


def cmd_init(args: argparse.Namespace) -> None:
    if PLAN.exists() and not args.force:
        die(f"{PLAN} already exists; pass --force to replace it")
    data = {"version": 1, "goal": args.goal, "global_gates": [], "missions": []}
    validated_save(data)
    print(PLAN)


def cmd_validate(_: argparse.Namespace) -> None:
    problems = validate(load())
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}")
        raise SystemExit(1)
    print("OK")


def cmd_ready(_: argparse.Namespace) -> None:
    data = load()
    problems = validate(data)
    if problems:
        for problem in problems:
            print(f"FAIL: {problem}", file=sys.stderr)
        raise SystemExit(1)
    missions = ready(data)
    if not missions:
        print("NONE")
        return
    for mission in missions:
        print(f"{mission['id']}\t{mission.get('worker_effort','high')}\t{mission.get('title','')}")


def cmd_status(_: argparse.Namespace) -> None:
    mm = mission_map(load())
    if not mm:
        print("No missions.")
        return
    for mid, mission in mm.items():
        deps = ",".join(mission.get("depends_on", [])) or "-"
        agent = mission.get("agent", "-")
        print(f"{mid}\t{mission.get('status','pending')}\tdeps={deps}\tagent={agent}\t{mission.get('title','')}")


def cmd_set(args: argparse.Namespace) -> None:
    data = load()
    mm = mission_map(data)
    if args.id not in mm:
        die(f"unknown mission id {args.id}")
    candidate = copy.deepcopy(data)
    target = mission_map(candidate)[args.id]
    target["status"] = args.status
    if args.agent is not None:
        target["agent"] = args.agent
    validated_save(candidate)
    print(f"{args.id}={args.status}")


def cmd_claim(args: argparse.Namespace) -> None:
    data = load()
    mm = mission_map(data)
    if args.id not in mm:
        die(f"unknown mission id {args.id}")
    ready_ids = {m["id"] for m in ready(data)}
    if args.id not in ready_ids:
        die(f"mission {args.id} is not READY")
    candidate = copy.deepcopy(data)
    target = mission_map(candidate)[args.id]
    target["status"] = "running"
    target["agent"] = args.agent
    validated_save(candidate)
    print(f"{args.id}=running agent={args.agent}")


def main() -> None:
    parser = argparse.ArgumentParser(prog="solaris.py")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("init", help="create .solaris/plan.json")
    sp.add_argument("--goal", required=True)
    sp.add_argument("--force", action="store_true")
    sp.set_defaults(func=cmd_init)

    sp = sub.add_parser("validate", help="validate mission DAG and state")
    sp.set_defaults(func=cmd_validate)

    sp = sub.add_parser("ready", help="print missions ready to run")
    sp.set_defaults(func=cmd_ready)

    sp = sub.add_parser("status", help="show mission state")
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("set", help="set mission status after validating the candidate state")
    sp.add_argument("id")
    sp.add_argument("status", choices=sorted(VALID_STATUS))
    sp.add_argument("--agent")
    sp.set_defaults(func=cmd_set)

    sp = sub.add_parser("claim", help="atomically mark a READY mission running")
    sp.add_argument("id")
    sp.add_argument("--agent", required=True)
    sp.set_defaults(func=cmd_claim)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
