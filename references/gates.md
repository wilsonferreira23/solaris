# Gate Design

Use the repository's existing commands whenever possible.

Gate order:
1. syntax/build
2. typecheck/static analysis
3. focused unit tests
4. focused integration tests
5. lint/format if required
6. E2E for changed user flows
7. project-specific evals/invariants
8. benchmark/performance gates when the change can affect them
9. broad regression suite at milestone/final integration

## Evidence rules

A command counts as evidence only if it was actually run in the current relevant state.

Record:
- command
- exit code
- concise result
- relevant failing test names if any

Do not accept:
- "tests should pass"
- "looks correct"
- a worker's claim without output/exit status
- generated tests that only restate implementation details without checking behavior

## Gate economy

Run the cheapest decisive gate first.

Do not run a 20-minute full suite after every local edit if a 5-second targeted test can falsify the current hypothesis. Do run the full required suite before final completion when the repository expects it.

## Evals

If the project has product/agent behavior:
- define evals before accepting behavior-changing implementation
- keep eval inputs separate from implementation prompts when possible
- preserve regression cases discovered during fixes

A failed gate should improve the next worker prompt with concrete evidence.
