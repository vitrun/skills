# Lens Catalog

Use the smallest lens that exposes the user's target problem. Avoid applying every lens to the same material unless the user asks for a broad audit.

## Technical Systems

### Request Lifecycle

Use for backend services, APIs, web apps, reliability audits, and codebase orientation.

Shape:

```text
entry point -> routing -> auth/permission -> validation -> controller/handler -> service/domain logic -> data access -> external dependencies -> transaction/cache behavior -> error handling -> logging/metrics -> response
```

Good audit questions:

- Where can errors be swallowed or normalized inconsistently?
- Are retries, transactions, cache writes, and side effects safe?
- Are logs and metrics enough to reconstruct a failed request?

### Error Path

Use when the user cares about failure handling, alerts, incident response, or flaky behavior.

Shape:

```text
trigger -> detection -> local handling -> propagation -> retry/fallback -> user-visible behavior -> logging/alerting -> recovery/cleanup
```

### Dependency Graph

Use for architecture review, refactoring, module boundaries, and ownership.

Shape:

```text
module/component -> depends on -> reason for dependency -> data/control contract -> directionality -> owner -> change risk
```

### State Machine

Use for workflows, lifecycle-heavy products, async jobs, approvals, tasks, orders, or UI state.

Shape:

```text
state -> allowed transitions -> transition trigger -> guard/permission -> side effects -> persisted facts -> terminal states -> invalid states
```

### Permission Model

Use for security, access control, enterprise products, and multi-role PRDs.

Shape:

```text
actor/role -> resource -> operation -> condition/scope -> enforcement point -> audit trail -> exception
```

## Data And ML Systems

### Data Lineage

Use for data quality, ETL, metrics, analytics, and feature pipelines.

Shape:

```text
source event/table -> ingestion -> cleaning/normalization -> joins -> derived fields -> storage -> consumers -> freshness/watermark -> validation -> backfill/replay
```

### Metric Definition Chain

Use when metric correctness, attribution, conversion, or reporting consistency is the concern.

Shape:

```text
business goal -> event definition -> inclusion/exclusion rules -> aggregation -> segmentation -> attribution window -> dashboard/report -> decision using the metric
```

### Sample-To-Serving Chain

Use for recommendation, ranking, search, ads, and ML product-effect analysis.

Shape:

```text
target metric -> exposure -> interaction/conversion -> label/sample construction -> feature production -> training -> offline evaluation -> online ranking/serving -> experiment -> monitoring/attribution -> feedback loop
```

## Product And Operations

### User Journey

Use for PRDs, conversion funnels, onboarding, growth, and support experience.

Shape:

```text
user intent -> entry point -> decision/action -> system response -> next user state -> success/failure exit -> recovery path -> measurement
```

### Cost Structure

Use for infrastructure cost, LLM/tool usage, vendor decisions, and operational efficiency.

Shape:

```text
unit of work -> volume driver -> fixed cost -> variable cost -> external vendor/API -> cache/reuse -> failure/retry cost -> owner/limit -> optimization lever
```

### Decision Or Delivery Chain

Use for organization process, collaboration, approvals, planning, and handoff problems.

Shape:

```text
input/request -> triage -> decision owner -> required evidence -> handoff -> execution -> review -> release -> feedback -> next decision
```

## Lens Selection Heuristics

- If the user asks "where can it break?", choose a flow lens.
- If the user asks "who owns this?", choose ownership or dependency graph.
- If the user asks "why is the metric wrong?", choose metric definition chain or data lineage.
- If the user asks "why does AI give generic answers?", choose a lens that turns raw material into checkable stages.
- If the user asks for a repo audit without more detail, start with request lifecycle for services, component/state flow for frontends, or dependency graph for libraries.
