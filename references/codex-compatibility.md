# Codex Compatibility Notes

Solaris follows the current Codex skill layout:
- required `SKILL.md` with YAML `name` and `description`
- optional `agents/openai.yaml`
- optional `scripts/` and `references/`

Current multi-agent behavior relevant to Solaris:
- subagents inherit parent model/reasoning unless an explicit spawn value, `[agents]` default, or custom agent config overrides them
- current Codex supports `agents.default_subagent_model` and `agents.default_subagent_reasoning_effort`
- `agents.max_concurrent_threads_per_session` limits open spawned-agent threads
- `max_depth` is a V1 control and is ignored by V2, so no-recursive-delegation must also be stated in prompts
- standard spawn metadata exposes per-agent model and reasoning overrides while omitting a per-spawn service-tier field
- child configuration propagates the session service tier when the selected child model supports it; native `spawn_agent` cannot independently set a different tier for one child
- parallel write-heavy subagents can create coordination conflicts, so Solaris uses disjoint ownership or serialization

Primary references checked for this package:
- Codex skill creator sample
- Codex configuration reference
- Codex Subagents documentation
- Codex Speed documentation
- Codex multi-agent spawn schema/tests
- OpenAI GPT-6 model catalog

If the installed Codex version differs from these notes, prefer the actual tool schema and configuration documentation exposed by that version.
