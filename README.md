# Solaris

**Solaris** is a Codex orchestration skill for shipping substantial software quickly with a clear division of labor:

- **Sol** plans, decomposes, integrates, reviews, and verifies.
- **Luna** implements production code in large, coherent missions and self-tests before returning.
- **Astra** is an escalation specialist for high-uncertainty architecture and root-cause analysis.
- **Gates** decide whether work is actually complete.

The core idea is simple: **minimize handoffs, maximize mission ownership, parallelize only real independence, and trust executable evidence over agent status text.**

## Why Solaris

Solaris is intentionally biased against micro-tasking. Instead of splitting a project into dozens of tiny tickets, the root agent builds a dependency DAG and delegates the **largest safe independent mission** each Luna can own end-to-end.

Typical missions look like:

- authentication end-to-end
- billing + webhooks + subscription state
- dashboard vertical slice
- sync engine
- onboarding flow

not:

- create one schema
- add one endpoint
- add one hook
- add one button

## Recommended runtime policy

For the workflow this repository is designed around:

- root: strongest practical **Sol** model for orchestration
- workers: **GPT-6 Luna** when available
- worker reasoning: **high** by default, **max** for genuinely difficult implementation
- concurrency: normally **1-3 Luna workers**
- Astra: only for high-uncertainty diagnosis/escalation
- Fast mode: configure at the **session** level when delivery speed is the priority

Current Codex behavior propagates the session service tier to a spawned child when that child model supports the tier. `spawn_agent` can override model/reasoning, but does not currently expose an independent per-child `service_tier`. So a Fast Solaris session normally means compatible Luna workers are Fast too.

Example configuration, only if these settings are supported by your installed Codex build:

```toml
service_tier = "fast"

[features]
fast_mode = true

[agents]
enabled = true
max_concurrent_threads_per_session = 3
default_subagent_model = "gpt-6-luna"
default_subagent_reasoning_effort = "high"
max_depth = 1
```

Solaris itself does **not** silently modify your global Codex configuration.

## Install

Clone the repository into a Codex-discovered personal skill directory. In current Codex documentation, personal skills are commonly discovered from `~/.agents/skills`:

```bash
git clone https://github.com/wilsonferreira23/solaris ~/.agents/skills/solaris
```

If your Codex build uses a different discovered skill path, place the repository there instead. The important requirement is that Codex sees:

```text
solaris/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
└── scripts/
```

## Use

Invoke it explicitly:

```text
$solaris Build this project from the PRD. Use large Luna missions, keep handoffs low, and verify with gates.
```

Or let Codex select it when the task matches the skill description.

## Architecture

```text
                         USER / GOAL
                              │
                              ▼
                             SOL
                 plan · route · integrate
                         · verify
                              │
               ┌──────────────┼──────────────┐
               ▼              ▼              ▼
             LUNA           LUNA           LUNA
           mission A      mission B      mission C
               │              │              │
               └──────────────┼──────────────┘
                              ▼
                             SOL
                       review + gates
                              │
                  ┌───────────┴───────────┐
                  ▼                       ▼
                PASS                    FAIL
                  │                       │
                merge             Luna fix / Astra
                                      diagnosis
```

## Key rules

- Think in **missions**, not tickets.
- Default to **1-3 concurrent workers**.
- One owner per write scope.
- No recursive delegation from Luna/Astra.
- Luna implements → tests → debugs → retests before returning.
- Deterministic gates come before semantic model review.
- Sol may make only trivial micro-integration edits; substantial implementation stays with Luna.
- Astra diagnoses uncertainty; Luna normally performs the resulting production edit.
- Optimize for **time and cost until all required gates pass**.

## Optional state helper

For multi-mission projects, Solaris ships a small standard-library-only helper:

```bash
python3 scripts/solaris.py init --goal "project goal"
python3 scripts/solaris.py validate
python3 scripts/solaris.py ready
python3 scripts/solaris.py status
```

It maintains `.solaris/plan.json`, validates the dependency DAG, reports ready missions, and catches obvious concurrent write-scope collisions.

## Repository layout

```text
SKILL.md
agents/openai.yaml
references/
  codex-compatibility.md
  gates.md
  mission-contract.md
  model-policy.md
  plan.example.json
  protocol.md
scripts/solaris.py
```

See `SKILL.md` for the operational instructions Codex follows.
