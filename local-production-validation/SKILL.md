---
name: local-production-validation
description: Guard local validation of services, jobs, serverless functions, and cloud-backed workflows so tests exercise production-shaped component boundaries instead of in-process shortcuts. Use when the user asks to locally validate, adapterize cloud dependencies, walk through serving, or run end-to-end verification against an IDL, gRPC, job trigger, event contract, or deployed-process-shaped surface.
---

# Local Production Validation

Use this skill when local validation might drift away from the production component shape.

## Scope

Apply this to services, workers, jobs, serverless functions, adapters, and cloud-backed workflows where validation should cross a real component boundary.

Do not trigger this for pure library functions, UI-only checks, narrow unit tests, or ordinary build/lint/test requests unless the user explicitly asks for production-shaped local validation.

If `long-horizon-work` also applies, use that skill for route/ledger control and this skill for the validation plan and evidence standard.

## Validation Level Gate

Before implementation, state the validation level you are choosing:

1. **In-process smoke** - direct function, handler, or module calls. This is useful as a unit/smoke check only and must be labeled that way.
2. **Process-level local integration** - start or invoke the real server, worker, binary, job runner, CLI, or serverless emulator locally, with external systems replaced by local or mock backends.
3. **Production-shape local harness** - exercise the same public surface used in production: IDL, gRPC, HTTP route, job trigger, event contract, queue message, or serverless entrypoint. Preserve startup, config loading, serialization, adapter initialization, and local/mock dependency wiring.

Prefer the highest feasible level. If choosing level 1 while level 2 or 3 is feasible, ask the user for confirmation before implementing.

If level 2 or 3 is blocked, name the specific blocker and the closest validation you can run without pretending it is production-shaped.

## Implementation Guardrails

- Identify the production entrypoint and public contract from the repo: proto/IDL, route registration, job trigger, event schema, deployment config, server startup, or worker bootstrap.
- Keep the component shape real: server as server, job as job, serverless function as serverless function, worker as worker.
- Abstract cloud products and external systems behind adapter traits, ports, interfaces, or provider modules.
- Wire a local profile to local/mock backends: mockserver, local database, fake queue, test event trigger, emulator, fixture-backed service, or equivalent.
- Call through the public surface. Do not bypass serialization, transport, config, or bootstrap by calling internal helper functions.
- Exercise timeout and error paths where practical, especially adapter initialization failures and dependency timeouts.
- Keep in-process replay as a supplemental smoke test and label it explicitly.
- Do not invent enum values, events, RPCs, config keys, thresholds, or cloud behavior that the codebase does not expose.

## Anti-Patterns

- Calling a handler, controller, or worker function directly and reporting it as end-to-end validation.
- Replacing the whole component under test with a fake instead of adapting its external dependencies.
- Constructing in-memory domain objects and skipping IDL, JSON/protobuf, transport, config, or startup behavior.
- Running only a happy-path unit test while claiming local production readiness.
- Depending on real cloud accounts when a local adapter or emulator is feasible for the requested validation.

## Done Evidence

Final reporting must include:

- Chosen validation level and why it was appropriate.
- The real entrypoint or public surface used.
- The local profile and adapter/mock backend wiring.
- Exact command or test script used to start or call the component.
- What was covered: serialization, config, startup, adapter initialization, timeout/error behavior.
- Any gaps, labeled honestly as smoke-only or not yet production-shaped.
