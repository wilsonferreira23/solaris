# Solaris Orchestration Protocol

## Phase 0: Recon

Root reads:
- user goal / PRD
- AGENTS.md and relevant project instructions
- repository architecture
- existing tests/evals/build commands
- current dirty state
- risky shared modules

Do not design missions before understanding the integration surface.

## Phase 1: Mission DAG

Express the project as outcomes and dependencies, not implementation trivia.

Each node has:
- id
- title
- outcome
- dependencies
- write scope
- acceptance
- targeted gates
- risk: normal | high-uncertainty

Prefer 2-5 initial missions. For large projects, 5-8 macro missions in waves.

A mission can contain many internal coding steps. The worker owns those steps.

## Phase 2: Ready set

A mission is READY only if:
- every dependency passed,
- no running mission owns overlapping write scope,
- enough project context exists to implement it,
- starting it now creates useful progress.

Spawn 1-3 ready Luna missions. Do not fill worker slots merely because they exist.

## Phase 3: Worker local loop

Luna:
1. inspect mission scope
2. implement
3. run targeted gates
4. debug failures
5. rerun
6. return evidence

Do not interrupt a healthy worker for micro-decisions the mission contract already delegates.

## Phase 4: Sol verification

For each return:
1. inspect actual changed files/diff
2. ensure write scope was respected
3. compare behavior to acceptance criteria
4. inspect tests for false confidence / missing edge cases
5. rerun the smallest decisive targeted gates
6. mark accepted or route a fix

Do not ask a reviewer model to replace executable checks.

## Phase 5: Integration

Integrate accepted missions in dependency order.

After each meaningful wave:
- run integration/type gates affected by the wave
- surface conflicts immediately
- unlock dependent missions only after decisive gates pass

Run broad/global gates near milestones and final delivery, not after every trivial file change if targeted gates already give sufficient evidence.

## Failure router

### Bounded implementation defect
Examples: local test failure, type mismatch, local edge case, incomplete acceptance criterion.
Route to the same Luna when practical, with failing evidence and a bounded correction request.

### Mission contract was wrong/incomplete
Sol updates the contract/DAG before asking for more code.

### High uncertainty
Examples: cross-module causality unclear, architecture suspected, nondeterministic concurrency, repeated fixes move the failure elsewhere, critical invariant has no trustworthy test.
Spawn Astra for diagnosis. Astra does not implement production code by default.

### Integration collision
Stop parallel writes into the collision area. Reassign one owner and serialize that boundary.

## Anti-fragmentation rule

Never create a new mission for a step a current worker can reasonably complete inside its existing outcome.

A failed sub-step is not automatically a new task.

Before adding a mission ask: "Does this create a new independently ownable outcome?" If no, keep it inside the current mission.

## Reviewer policy

Independent LLM review is risk-triggered, not mandatory.

Use a reviewer when:
- security or money-critical logic changed
- architecture/invariants changed
- test coverage is plausibly insufficient
- a worker touched unusually broad code
- an external second perspective can run in parallel with useful work

Otherwise Sol + deterministic gates is enough.

## Final gate

Final delivery requires:
- all mission acceptance criteria passed
- no known unresolved blocker
- build/typecheck/lint/tests/evals required by the repo passed
- integration behavior verified
- user-facing requested deliverables present

Report remaining uncertainty explicitly instead of converting it into "done".
