# Mission Contract

Use this template when delegating an implementation mission. Keep it outcome-oriented.

```text
MISSION <ID>: <coherent outcome>

OUTCOME
What must be true for the user when this mission is finished.

CONTEXT
Only the architectural/product context needed to make correct local decisions.

READ SCOPE
- paths the worker may inspect freely

WRITE SCOPE
- production/test paths this worker owns
- must not overlap another concurrently running writer

NON-GOALS
- explicit adjacent work that belongs elsewhere

DEPENDENCIES
- mission IDs or "none"

ACCEPTANCE
- observable behaviors
- invariants
- required tests/evals

TARGETED GATES
- exact commands the worker should run before returning

MODEL POLICY
- model: Luna (prefer gpt-6-luna when available)
- reasoning: high by default; max if this mission is genuinely hard
- speed: respect the active session/config Fast setting; do not claim a per-worker tier override unless exposed

WORKER RULES
- You are not alone in this repository.
- Do not revert unrelated work.
- Do not modify outside WRITE SCOPE unless blocked; report the block instead.
- Do not spawn subagents.
- Make internal implementation decisions yourself.
- Implement -> test -> debug -> retest until locally green.
- Return evidence, not merely "done".
```

## Good mission sizes

Good:
- "Implement authentication end-to-end: persistence, API, session lifecycle, UI wiring, tests."
- "Own billing: checkout, webhook processing, subscription state, retries, tests."
- "Build the dashboard vertical slice from data loading through user interactions and E2E coverage."

Usually too small:
- "Create schema."
- "Create endpoint."
- "Add hook."
- "Add button."
- "Write one unit test."

Split a large mission only for a real reason: independent ownership, dependency boundary, unsafe context size, risk gate, or write-scope collision.
