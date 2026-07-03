# RPB Adapter Notes

RPB support is an adapter, not the core routing boundary. Keep generic failure
heads in the main contracts and map RPB names only when inputs clearly come from
Role-Play Bench.

## Generic to RPB Mapping

| Generic head | RPB head | Meaning |
| --- | --- | --- |
| `REPETITION_OR_STASIS` | `H3_REPETITION_LOOP` | Repeated phrasing, slow-motion loops, no scene movement |
| `USER_AGENCY_VIOLATION` | `H6_USER_AGENCY_VIOLATION` | Assistant speaks, acts, decides, or feels for the user |
| `ROLE_OR_FORMAT_BREAK` | `H5_PERSONA_BREAK_OR_GENERIC_ASSISTANT` | Assistant leaves role, exposes analysis, or sounds generic |
| `REFUSAL_OR_HARD_END` | `H1_HARD_END_OR_RESET` | Hard ending, refusal, reset, or new-scenario output |

## Reusable Lessons

The existing bench scripts are useful design references:
- `/Users/axel/Work/bench/scripts/scan_rpb_hard_failures.py`
- `/Users/axel/Work/bench/scripts/apply_rpb_prompt_patch.py`

Use their section-discovery and hard-failure ideas as optional inspiration. Do
not make this skill depend on those repo paths at runtime.

## RPB-Specific Gotchas

- H3/H6 often need long-turn evidence; short samples can miss recurrence.
- A rule scanner is a candidate generator, not truth.
- Reducing obvious hard failures can still degrade role-play quality.
- Prompt advice should preserve native streaming and product UX boundaries; do
  not route online/business serving to post-generation repair by default.
