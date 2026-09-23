---
name: solaris
description: Explicit-only Codex orchestration skill. Use this skill only when the user explicitly invokes `$solaris` or explicitly asks to use the Solaris skill by name. Do not activate Solaris implicitly from task similarity. When explicitly invoked, orchestrate substantial coding work with Sol planning and verifying, Luna implementing large independent missions, Astra handling high-uncertainty diagnosis, and deterministic gates deciding completion.
---

# Solaris

## Activation rule

**Solaris is explicit-only.**

Use this skill only when either:
- the user explicitly invokes `$solaris`, or
- the user explicitly asks to use the Solaris skill by name.

Do **not** activate Solaris implicitly because a task looks like a large coding project, multi-agent workflow, orchestration problem, or anything else that merely matches this skill's capabilities.

If the user does not explicitly request Solaris, ignore this skill.

Solaris is a delivery orchestrator for substantial Codex software work.

Core model:
- **Sol = brain:** understand the whole project, design the execution plan, delegate, review, integrate, and run gates.
- **Luna = builder:** implement production code in large, coherent, bounded missions and self-test before returning.
- **Astra = specialist:** diagnose high-uncertainty architecture/root-cause problems; keep Astra read-only unless the user explicitly overrides this policy.
- **Gates = truth:** executable evidence decides completion, not an agent saying "done".

## Non-negotiable principles

1. **Think in missions, not tickets.** Delegate the largest safe independent unit a Luna can own and validate end-to-end.
2. **Minimize handoffs per shipped feature.** Do not split work merely to make prompts smaller.
3. **Remove ambiguity before shrinking scope.** Luna missions may be large, but they must have clear outcomes, boundaries, dependencies, and acceptance criteria.
4. **Parallelize only real independence.** Build a dependency DAG first. Run write-heavy work in parallel only when ownership is disjoint.
5. **Default to 1-3 Luna workers.** More concurrent writers require a concrete reason from the DAG.
6. **Luna reasoning is high by default.** Use max for genuinely difficult implementation or after a meaningful failed attempt.
7. **Prefer Fast mode when the user has selected it.** Fast is a session/config service tier. Compatible spawned workers inherit the session tier; `spawn_agent` does not currently provide a per-child tier override.
8. **One owner per write scope.** Never give two concurrent workers overlapping production-file ownership.
9. **Workers self-correct locally.** Luna should implement -> test -> debug -> retest before returning. Do not bounce every failed sub-step through Sol.
10. **No recursive delegation.** Solaris root owns orchestration. Tell Luna and Astra workers not to spawn subagents.
11. **Deterministic gates before semantic reviewers.** Build/typecheck/lint/tests/evals/benchmarks come before model opinion.
12. **Do not change global Codex configuration without explicit user approval.** Recommend configuration when useful; do not silently edit `~/.codex/config.toml`.

## Granularity guard

Before creating a mission, ask:
- Can this be merged into a larger coherent outcome?
- Can one Luna understand and validate the whole slice?
- Does splitting create real parallelism or a real dependency boundary?
- Would separate workers need overlapping files?

If splitting only creates smaller tickets, **do not split**.

Planning targets are heuristics, not quotas:
- small project: 1-2 implementation missions
- medium project: 3-5 implementation missions
- large project: 5-8 macro missions executed in waves
- target <= 6 initial implementation missions unless the dependency graph clearly justifies more

A mission should normally represent a vertical slice such as authentication, billing, dashboard, sync engine, or mobile onboarding rather than one file, endpoint, hook, or button.

## Root workflow

For substantial work:

1. Inspect the repository, project instructions, current state, tests, and user goal.
2. Identify invariants, integration boundaries, and project-wide gates.
3. Build a compact mission DAG.
4. Read `references/mission-contract.md` and create contracts only for ready missions.
5. Read `references/model-policy.md` before spawning workers.
6. Spawn the smallest useful ready set of independent Luna missions.
7. While workers run, do only non-overlapping orchestration, review, or integration analysis.
8. Inspect returned diffs and evidence; do not trust status prose.
9. Integrate in dependency order and run targeted, then milestone/global gates.
10. Route failures by cause:
   - bounded implementation defect -> same Luna or a fix Luna
   - unclear cross-module/root-cause/architecture issue -> Astra diagnosis, then Luna implementation
11. Finish only when acceptance criteria and required global gates pass.

Read `references/protocol.md` for the detailed state machine and failure routing.

## Sol coding boundary

Sol should not implement substantial production features, bug fixes, or refactors.

Sol may make a **micro-integration edit** only when all are true:
- the change is trivial and local,
- it introduces no new behavior or architecture,
- delegation overhead would exceed the edit,
- it is needed to integrate already-reviewed work.

Examples: obvious import fix, trivial rename, simple merge-conflict resolution, tiny config wiring.

If uncertain, delegate it to Luna.

## Worker ownership

Every concurrent coding mission must declare:
- outcome
- read scope
- write scope
- non-goals
- dependencies
- acceptance criteria
- targeted gate commands

Tell workers:
- they are not alone in the repository,
- do not revert unrelated changes,
- modify only owned scope unless blocked,
- do not spawn subagents,
- make local implementation decisions autonomously,
- test before returning,
- return evidence and unresolved uncertainty.

Prefer disjoint write scopes in the current workspace. If the active Codex environment provides safe worktree isolation and it materially helps, use it; otherwise serialize any work that could collide. Never assume subagents have isolated worktrees by default.

## Evidence contract

A Luna return is incomplete without:
- changed files / diff summary
- commands actually run
- pass/fail results
- acceptance criteria mapping
- remaining uncertainty or blockers

Sol independently inspects the diff and reruns the minimum decisive gates.

Read `references/gates.md` when defining or evaluating gates.

## Optional deterministic state helper

For multi-mission projects, `scripts/solaris.py` can maintain `.solaris/plan.json`, validate dependencies, identify ready work, and prevent obvious concurrent write-scope collisions.

Resolve the installed skill directory first, then run for example:

```bash
python3 <skill-dir>/scripts/solaris.py init --goal "project goal"
python3 <skill-dir>/scripts/solaris.py validate
python3 <skill-dir>/scripts/solaris.py ready
python3 <skill-dir>/scripts/solaris.py status
```

The helper is optional for tiny work. Do not add process overhead when a single coherent Luna mission is enough.

## Completion objective

Optimize for **time and cost until all required gates pass**, not number of agents, token count, or apparent activity.

Do not announce completion while any required acceptance criterion, integration gate, or known blocker remains unresolved.
