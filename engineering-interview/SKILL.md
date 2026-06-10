---
name: engineering-interview
description: Prepare, run, organize, and assess senior engineering hiring interviews across multiple stages from a JD, resume, interview answers, prior notes, or focus areas. Use when the user asks for resume-based interview questions, recruiting interview strategy, ownership/authenticity checks, Staff+ technical depth evaluation, answer synthesis, or post-interview assessment.
---

# Engineering Interview

Use this skill to help an experienced hiring manager evaluate engineering candidates. Match the user's language.

The goal is not to generate generic questions. The goal is to test job-relevant evidence of:

- technical depth
- ownership
- system thinking
- engineering judgment
- delivery capability
- resume authenticity

Evaluate only job-relevant facts. Do not infer ability from protected traits, personality labels, education prestige, company prestige, or style alone. Separate evidence from inference.

## Inputs

The user may provide any subset of:

- Job Description
- Candidate Resume
- Interview Questions
- Candidate Answers or Transcript
- Previous Interview Notes
- Special Focus Areas
- Target level or role expectations

If key inputs are missing, continue with explicit assumptions. Ask only when the missing input would make the interview unsafe, unfair, or unusably broad.

## Operating Modes

Choose the mode from the request:

- `prepare`: create a resume/JD-driven interview plan before the interview.
- `live`: provide question prompts and follow-up paths during an interview.
- `organize`: turn interview Q&A, transcript, or notes into structured evidence.
- `assess`: critique or evaluate organized evidence or notes; default to practical
  candidate commentary, and use formal JD/level assessment only when requested.

If the user only provides a resume, JD, or focus areas, default to `prepare`. If the user provides interview answers or notes without asking for a final hiring decision, default to `organize`. If the user provides interview answers or notes and asks for 点评, evaluation, recommendation, JD fit, or hiring signal, use `organize` first internally, then `assess`.

## Stage Workflow

Treat interviewing as a staged workflow, not a one-shot prompt. Keep each stage's output useful on its own and easy to carry into the next stage.

### Stage 1: Resume Analysis and Questioning

Use when preparing or running the interview from a resume, JD, or focus areas.

Goals:

- identify 2-3 highest-leverage interview lines
- connect each line to resume claims and JD requirements when available
- create project-grounded opening questions
- provide follow-up paths for ownership, depth, tradeoffs, execution, failure, and learning
- define what evidence should be captured during the interview

Do not try to evaluate the candidate yet except as clearly labeled hypotheses or risk areas. The output should help the interviewer ask better questions and gather evidence.

### Stage 2: Q&A Organization

Use when the user provides interview notes, answers, or transcript fragments.

Goals:

- group answers by interview line, project, and capability area
- preserve concrete candidate claims, numbers, decisions, tradeoffs, and failure examples
- classify each claim as `Observed Evidence`, `Inference`, `Missing Evidence`, or `Follow-up Needed`
- classify ownership signals as `Builder`, `Contributor`, `Observer`, or `Unclear`
- identify contradictions, vague claims, unsupported breadth, and unvalidated JD requirements
- produce a clean evidence brief that can be evaluated later

Do not inflate rough notes into conclusions. If an answer is ambiguous, keep the ambiguity visible and ask for a follow-up question rather than resolving it by assumption.

### Stage 3: Interview Assessment

Use when the user asks for evaluation, recommendation, hiring decision support, or JD fit.

Goals:

- evaluate only demonstrated evidence, not resume claims alone
- identify strong signals, answer-exposed concerns, and next-step probes
- keep uncovered topics separate from candidate concerns
- when explicitly requested, map the organized evidence to the JD's must-have
  requirements, nice-to-have requirements, target level, and hiring decision
- explain where the evidence is insufficient for a fair conclusion

Default to a concise hiring-manager commentary when the user asks to "点评",
"评价", "怎么看", "总结下候选人", or similar. Use a formal JD-aligned
assessment only when the user explicitly asks for JD fit, a hiring decision,
calibrated level, scorecard, or a formal recommendation.

Do not issue a confident recommendation when the notes are thin or the JD is missing. Use `Insufficient Evidence` when the evidence cannot support a fair decision.

## Stage Handoff

When a response could continue into another stage, end with a compact handoff section:

```markdown
## Next Stage Input Needed
- [The exact notes, answers, transcript, JD excerpt, or role expectation needed next.]

## Carry Forward
- Interview lines: [2-3 lines]
- Key risks to verify: [short list]
- Evidence gaps: [short list]
```

Omit this section only for very short live-interview prompts or when the user asks for a final-only answer.

## Core Interview Loop

Always prioritize:

```text
project -> decision -> tradeoff -> implementation -> failure -> lesson learned
```

Never stop at terminology, framework names, or architecture diagrams. Strong evidence usually includes precise metrics, local constraints, alternatives considered, tradeoffs accepted, operational consequences, and lessons incorporated later.

## Question Design Rules

1. Prefer real project discussion over knowledge questions.
2. Collapse broad resumes into 2-3 deep interview lines. Do not turn every resume bullet into a standalone topic.
3. For each major project, verify ownership:
   - who proposed it
   - who designed it
   - who implemented it
   - who operated it
   - who was accountable for outcomes
4. Quantify everything relevant:
   - QPS, DAU, latency, throughput, token volume, machine count, cost, incidents, team size, delivery time, adoption, revenue, or error rate
5. Follow decisions:
   - alternatives considered
   - why this design won
   - tradeoffs accepted
   - what broke later
6. Follow failures:
   - bottlenecks, outages, incorrect assumptions, scaling limits, redesigns, and operational lessons
7. Use textbook or definition questions only as a fallback when project evidence is absent or a claimed foundation needs quick calibration.

## Builder Verification

For each important claim, distinguish:

- `Builder`: can explain constraints, implementation details, failure modes, metrics, and post-launch operation.
- `Contributor`: can explain a scoped piece, interfaces, handoffs, and concrete work shipped.
- `Observer`: repeats outcomes, diagrams, or team narratives without local decisions or implementation detail.

Do not assume ownership from resume wording. Treat missing numbers, vague ownership, suspicious breadth, and name-dropping as risk signals to verify, not conclusions.

## Stage 1 Output: Resume Analysis and Questioning

Use this structure for interview preparation:

```markdown
# Candidate Brief

## Background Summary
[Concise summary of experience, domains, and major projects. Mark unknowns.]

## Technical Focus
1. [Area] - [confidence: high/medium/low and why]

## Likely Strengths
- [Evidence-backed or hypothesis, labeled clearly]

## Risk Areas
- [Ownership, scale evidence, unclear contribution, suspicious breadth, or role mismatch]

# Interview Strategy
[Recommended breadth/depth/ownership/architecture validation approach. Explain why these 2-3 lines are highest leverage.]

# Interview Lines

## Line 1: [Theme]

### Opening Question
[Project-grounded question.]

### Purpose
[Capability being validated.]

### Strong Signals
- [What a strong answer contains.]

### Weak Signals
- [What needs follow-up or concern.]

### Follow-up Path
1. [Decision and alternatives]
2. [Implementation and interfaces]
3. [Scale, metrics, and constraints]
4. [Failure, operation, and lessons]

# Technical Background

## [Topic]

### Background
[Brief concept summary for the interviewer.]

### Industry Practice
[Common production approach.]

### Common Mistakes
[Typical misconceptions or shallow answers.]

# Resume Authenticity Checks

## Claim
[Quoted or summarized resume claim.]

## Verification Questions
- [Question that separates builder/contributor/observer.]

## Evidence Capture Guide
- [What answer detail should be captured for later evaluation.]

## Next Stage Input Needed
- [Interview answers, transcript, or notes needed for Q&A organization.]

## Carry Forward
- Interview lines: [2-3 lines]
- Key risks to verify: [short list]
- Evidence gaps: [short list]
```

## Live Output

During a live interview, keep the response short and usable:

- ask one primary question at a time
- provide 2-4 follow-ups ordered from broad to deep
- say what signal each follow-up is testing
- adapt based on the candidate's answer instead of continuing a static script

## Stage 2 Output: Q&A Organization

Use this structure when the user provides interview answers, transcript, or notes and needs them organized:

```markdown
# Interview Evidence Brief

## Interview Lines Covered
1. [Line] - [coverage: strong/partial/thin]

## Evidence by Capability

### [Capability or JD Area]

#### Observed Evidence
- [Specific answer, decision, metric, implementation detail, incident, or tradeoff.]

#### Ownership Signal
[Builder | Contributor | Observer | Unclear] - [why]

#### Inference
- [What this may suggest, with confidence.]

#### Missing Evidence
- [What is still not validated.]

#### Follow-up Needed
- [Concrete next question if more evidence is required.]

## Contradictions or Ambiguity
- [Conflicting, vague, or unsupported claims.]

## Carry Forward
- Strongest evidence: [short list]
- Main concerns: [short list]
- Evidence gaps: [short list]
```

Keep the candidate's concrete claims traceable. Do not rewrite vague answers as strong evidence.

## Stage 3 Output: Interview Assessment

Use the concise commentary structure by default when the user provides interview
answers or notes and asks for a practical candidate critique:

```markdown
[One short overall paragraph: concrete background signal, main strength areas,
and what to verify next. Avoid formal hire/no-hire labels unless requested.]

1, 强信号
- [Evidence-backed strength with concrete examples, numbers, systems, or answer details.]

2, 主要担忧
- [Only concerns exposed by the candidate's answers. Do not turn "not enough time",
  "interviewer did not ask", nervousness, or uncovered topics into candidate risks.]

3, 建议下一轮重点
1. [Probe tied to the highest-risk concern.]
2. [Probe tied to ownership, implementation, experiment design, or coding.]
3. [Probe for uncovered-but-important requirements.]
```

Concise commentary rules:

- Do not include a separate `岗位匹配` / `JD Fit Summary` section unless explicitly requested.
- Do not use `Strong Hire | Hire | Leaning Hire | ...` labels unless explicitly requested.
- Keep the output decision-useful: what is strong, what is risky, what to ask next.
- Strong signals should include concrete examples from the interview, not generic praise.
- Concerns must be structural and evidenced by answers. If a topic was simply not covered,
  put it under next-round focus instead of writing it as a concern.
- Prefer cautious, grounded wording such as "经验真实概率较高", "做过线上链路或至少贴得比较近",
  and "需要确认是核心实现者还是参与方案讨论".

Use this formal structure only when the user explicitly asks for JD fit, scorecard,
level calibration, or a hiring recommendation:

```markdown
# Interview Assessment

## JD Fit Summary
- Must-have requirements: [met/partial/not evidenced]
- Nice-to-have requirements: [met/partial/not evidenced]
- Level expectations: [met/partial/not evidenced]

## Overall Recommendation
[Strong Hire | Hire | Leaning Hire | Leaning No Hire | No Hire | Insufficient Evidence]

## Strengths
- [Evidence-backed strength.]

## Concerns
- [Evidence-backed concern.]

## Evidence

### Observation
[Specific observed answer or behavior.]

### Supporting Answer
[Concise evidence from notes.]

### Interpretation
[What it suggests and confidence level.]

## Missing Evidence
- [Unvalidated area that should not be concluded from current notes.]

## Follow-up Probes
- [Question to close the highest-risk evidence gap.]
```

Use `Insufficient Evidence` when the notes do not support a fair recommendation. Avoid emotional language and vague statements. Every conclusion must trace back to interview evidence.

## Domain Guidance

Use these only when the resume, JD, or focus areas make the domain relevant.

### Recommendation Systems

Focus on objectives, labels, feedback loops, ranking architecture, exploration vs exploitation, offline/online metric tension, feature freshness, evaluation bias, and business impact. Push beyond model names.

### LLM Infrastructure

Focus on serving architecture, batching, scheduling, streaming, latency, reliability, token volume, cost optimization, evals, fallback behavior, and operational observability. Push beyond framework familiarity.

### Distributed Systems

Focus on consistency, availability, failure handling, backpressure, scaling bottlenecks, data correctness, incident response, and observability. Push beyond architecture diagrams.

### Platform Engineering

Focus on abstraction boundaries, multi-tenancy, operational burden, upgrade strategy, developer experience, adoption, support load, and migration design. Push beyond feature descriptions.

### Data and ML Platforms

Focus on data contracts, lineage, freshness, quality checks, feature/data ownership, training-serving skew, experiment design, reproducibility, and production monitoring. Push beyond pipeline names.
