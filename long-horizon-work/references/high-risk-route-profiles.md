# High-Risk Route Profiles

Use this reference when a long-horizon route is not a simple bounded API/service task. Load it for `data/algorithm`, `provider/cloud`, `simulator/eval`, and `mixed` profiles.

## Profile Guidance

| Profile | Extra route requirements |
| --- | --- |
| `data/algorithm` | Data lineage, decision/event ledger, metric semantics, hand fixtures for math, and explicit evidence labels. |
| `provider/cloud` | Provider-neutral capability contract, fake/local conformance, live-provider probe plan, and provider mapping source of truth. |
| `simulator/eval` | Source provenance, negative controls, metric-family separation, repeatability evidence, and explicit "not production effect" labels. |
| `mixed` | Combine the above requirements for each active risk; keep the first slice narrow. |

For these profiles, the first slice should usually prove boundary shape and validation fidelity before broad implementation.

## Required Contracts

Add a route section like this when contracts determine correctness:

```markdown
## Required Contracts
| Contract | Source Of Truth | Needed Before | Notes |
| --- | --- | --- | --- |
| <capability/event/data/API/provider/metric contract> | <file/doc/API/live source> | <slice/workstream> | <notes> |
```

Typical contract categories:

- Public API/IDL contract.
- Capability abstraction or provider-neutral port contract.
- Event, decision, exposure, feedback, attribution, or reward ledger.
- Data lineage and ownership contract.
- Provider mapping and live behavior contract.
- Metric semantics and evaluation contract.

## Sharp-Edge Register

Use this for areas where plausible code can pass ordinary tests while being conceptually wrong:

```markdown
## Sharp-Edge Register
| Area | Why Risky | Reference | Required Invariant | Required Test / Probe | Must Not |
| --- | --- | --- | --- | --- | --- |
| <ID/time/math/provider/event/etc.> | <risk> | <source> | <invariant> | <test/probe> | <bad inference/action> |
```

Common sharp edges:

- IDs, UUID versions, clocks, randomness, TTL, expiry, and ordering.
- Algorithms, linear algebra, vector normalization, distance conversion, and metric semantics.
- Idempotency, compare-and-set, retries, partial failure, timeout, rollback, and concurrency.
- Provider-specific serialization, consistency, credentials, network reachability, and SDK behavior.
- Cross-system event contracts, attribution keys, and data ownership.

Prefer libraries, official docs, reference implementations, hand fixtures, property tests, conformance tests, or live probes over model memory.

## Evidence Claim Block

Use this block when closing a meaningful slice:

```text
Claim:
  <What this slice claims is now true.>

Proof:
  <Commands, tests, scripts, probes, artifacts, or observations.>

Evidence Level:
  unit | process-local | fake-conformance | simulator | live-provider | shadow | canary

Can Be Trusted For:
  <The narrow conclusion supported by the proof.>

Must Not Be Used To Claim:
  <Adjacent or stronger conclusions not proven.>

Not Proven:
  <Known gaps and untested surfaces.>

Next Reality Step:
  <The next higher-fidelity validation or integration step.>
```

Evidence labels:

- `unit`: direct module/function tests only.
- `process-local`: real local process, CLI, server, worker, job, or public entrypoint with local/mock dependencies.
- `fake-conformance`: provider-neutral contract passed against fake/local implementation.
- `simulator`: offline, synthetic, or modeled environment evidence.
- `live-provider`: real external provider/cloud behavior was probed.
- `shadow`: production-shaped traffic path observed without user-visible effect.
- `canary`: limited production rollout with monitoring and rollback.

Never promote lower-fidelity evidence into a higher-fidelity claim. In-process smoke is not process-local E2E, fake conformance is not live-provider proof, simulator evidence is not online effect proof, and local green tests are not production readiness.
