# OKF Layout

Use ordinary markdown files with YAML frontmatter and relative markdown links. Keep the structure minimal until the library has enough concepts to justify more types.

## Minimal Bundle

```text
research-patterns/
├── index.md
├── log.md
├── papers/
├── patterns/
├── bottlenecks/
└── questions/
```

Add `assumptions/`, `tradeoffs/`, `syntheses/`, `benchmarks/`, or `datasets/` only after those concepts recur across several papers.

## Concept Types

Start with:

- `Paper`: a source paper as evidence and extraction report.
- `Pattern`: a reusable problem or solution move.
- `Bottleneck`: a recurring obstacle shared by papers or domains.
- `Research Question`: a future investigation generated from a pattern boundary.

Allowed optional types include `Assumption`, `Tradeoff`, `Synthesis`, `Transfer Case`, `Method Family`, `Benchmark`, `Dataset`, and `Evidence`.

## Naming

- Use lowercase hyphenated filenames.
- Prefer conceptual names over paper titles for Pattern files.
- Keep paths stable once linked.
- Use a domain subfolder only when it helps navigation.

Examples:

```text
papers/nlp/retrieval-augmented-generation.md
patterns/solution-levers/externalize-memory-with-retrieval.md
bottlenecks/knowledge-staleness.md
questions/handling-conflicting-retrieval-evidence.md
```

## Linking

Use relative markdown links so the bundle works in Obsidian, GitHub, and local tools:

```markdown
This pattern addresses [Knowledge staleness](../../bottlenecks/knowledge-staleness.md)
and raises [Handling conflicting retrieval evidence](../../questions/handling-conflicting-retrieval-evidence.md).
```

Core edges:

- Paper -> Pattern
- Pattern -> Bottleneck
- Pattern -> Assumption
- Pattern -> Tradeoff
- Pattern -> Research Question
- Synthesis -> Pattern cluster

## Index And Log

Use `index.md` as the map for a directory, not a dump of every detail. Use `log.md` for changes in understanding: splits, merges, renamed patterns, deprecated assumptions, and new questions.

## Update Rules

- Update an existing Pattern when the new paper is another instance of the same transferable move.
- Create a new Pattern when the new paper has a different bottleneck, reframing, lever, or transfer boundary.
- Split a Pattern when the concept has two different mechanisms or transfer conditions.
- Mark maturity as `seed`, `recurrent`, `family`, `principle`, or `deprecated`.
