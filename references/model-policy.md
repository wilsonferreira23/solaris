# Model and Speed Policy

## Root / orchestrator

Prefer the strongest practical Sol model selected for the Codex session. Solaris does not require a hard-coded root model string; the root role is global reasoning, decomposition, routing, integration, and verification.

For current GPT-6 guidance, medium is the normal starting point for Sol. Raise effort when the orchestration problem itself is unusually ambiguous or risky.

## Implementation workers

Preferred order:
1. `gpt-6-luna` when available
2. `gpt-5.6-luna` when GPT-6 Luna is unavailable
3. the configured/default Luna-equivalent worker if explicit model selection is unavailable

Reasoning:
- **high**: default for implementation missions
- **max**: genuinely difficult implementation, deep refactor, complicated state/concurrency logic, or a meaningful prior failed implementation
- do not lower below high unless the user explicitly changes this policy

A mission may be large in outcome while still being suitable for Luna if Sol has removed ambiguity and given it a bounded ownership surface. Do not confuse "large mission" with "vague mission".

When the active `spawn_agent` surface exposes model/reasoning overrides, request Luna and the intended effort explicitly. Otherwise rely on `[agents]` defaults or the active custom-agent configuration.

## Fast mode

The user prefers Fast mode for Solaris delivery.

Current Codex exposes Fast as a session/config service-tier choice. The standard `spawn_agent` schema exposes model and reasoning overrides but not a per-child `service_tier` override. During child configuration, Codex propagates the session service tier to the child when the selected child model supports that tier. Therefore:
- configure Fast at the session level,
- expect compatible Luna workers spawned from that session to inherit Fast,
- do not claim Solaris can make one child Fast while keeping the root Standard through native `spawn_agent`,
- if credit usage matters, verify the active session tier rather than inferring it from the prompt.

Current GPT-6 Fast mode consumes more ChatGPT credits than Standard. This is intentional when the user prioritizes delivery speed.

Recommended user configuration, **only when the user asks to configure Codex**:

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

Notes:
- `features.fast_mode` controls availability of Fast-tier selection and is currently stable/on by default; `service_tier = "fast"` persists the preference.
- `max_depth` applies to V1 agent threads and may be ignored by V2, so Solaris also prohibits recursive delegation in worker prompts.
- if `gpt-6-luna` is unavailable, use `gpt-5.6-luna`.
- never silently edit the user's global config to apply this snippet.

## Astra

Preferred: `gpt-6-astra`.

Use Astra as a read-only diagnosis/architecture specialist when:
- architecture is genuinely ambiguous,
- root cause crosses several modules,
- race/concurrency behavior is unclear,
- a critical migration or invariant is at risk,
- repeated Luna fixes fail for different reasons,
- Sol's confidence is materially low.

Default Astra reasoning:
- low or medium for diagnosis
- high only when the problem itself justifies it

Astra should return:
- root cause or competing hypotheses
- evidence
- recommended strategy
- risks
- tests that would falsify the recommendation

Then Sol converts the diagnosis into a bounded Luna implementation mission. Astra does not write production code unless the user explicitly overrides Solaris' role separation.

## Routing objective

Minimize **cost/time-to-pass**, not cost per call.

A cheap worker that repeatedly fails can cost more than one early specialist diagnosis followed by one successful Luna implementation.
