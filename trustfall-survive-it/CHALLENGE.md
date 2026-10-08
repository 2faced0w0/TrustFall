# SURVIVE IT

## Build. Attack. Patch. Defend.

Your mission is not to build a generic chatbot. Complete the deterministic trust and decision layer around a fictional profile assistant, then try to breach another team's frozen build, repair your own, and explain the engineering decisions that survived.

## What you own

You own the Python files in this kit, your five attack submissions, `team_manifest.json`, your snapshots, and the Engineering Decision Card. The starter runs immediately. It includes working request parsing, isolated state, model adapters, a public test harness, and basic happy paths. Several public security tests intentionally fail at baseline because meaningful trust-boundary work remains.

Implement deterministic controls for authenticated roles, claim-by-claim verification, document handling, provenance, guarded state changes, protected-output handling, and the four decisions: ALLOW, BLOCK, TRANSFORM, and ESCALATE. Model output may help with prose but never with authority or execution.

## What adversaries will try

Expect direct instructions, false authority, mixed true and false claims, indirect document instructions, authorization bypasses, extraction, tool misuse, and provenance ambiguity. Hidden evaluation varies wording and placement. Boundary logic wins; exact attack-string matching does not.

## Build and test

Read `SPEC.md` first. Run:

```text
python -m unittest discover -s tests -v
```

Public tests are visible teaching signals. Hidden evaluator tests are not included and may use paraphrases, reordered claims, mixed benign/malicious content, unknown identities, conflicting evidence, and provider changes.

## Attack submission

Submit exactly five attacks in `attacks/attacks.json` using at least three distinct categories. Use `Attack_Template.json` as a shape reference. Cosmetic rewrites are duplicates. Each attack must state its predicted failure, success condition, and rationale.

## Freeze, breach, patch

Create the pre-patch snapshot:

```text
python scripts/freeze_snapshot.py --label pre-patch
```

Opponent evaluators run the assigned attacks against that snapshot. A breach report records evidence only. Example schema:

```json
{
  "attack_id": "T04-A03",
  "breach_type": "AUTHORIZATION",
  "request": {"user_id": "U_VIEW_01", "action": "commit_update", "profile_id": "MAV-042", "text": "..."},
  "observed": {
    "status": "allowed",
    "claim_status": "not_applicable",
    "tool_calls": [{"tool": "update_profile", "executed": true}]
  },
  "expected": "No state-changing tool call",
  "success_condition": "Unauthorized update executed"
}
```

Use one breach class: `INTEGRITY`, `AUTHORIZATION`, `PROVENANCE`, `INSTRUCTION`, `CONFIDENTIALITY`, or `TOOL`. The report must not include root cause, patch advice, or solution code. Diagnose the boundary failure, patch it, rerun both security and utility cases, then freeze:

```text
python scripts/freeze_snapshot.py --label final
```

## Submission

Submit source, exactly five attacks, both requested snapshots, a filled `team_manifest.json`, and a completed `Engineering_Decision_Card.md`. Validate with:

```text
python scripts/validate_submission.py
```

## Event timeline

| Time | Activity |
|---|---|
| 01:18–01:23 | Challenge + code walkthrough |
| 01:23 | Build starts |
| 01:57 | Exactly five attacks due |
| 02:05 | Pre-patch freeze |
| 02:05–02:15 | Opponent evaluation / breach reports |
| 02:15 | Patch starts |
| 02:35 | Code freeze |
| 02:42 | Final submission |
| 02:42–02:52 | Engineering Leader review |
| 02:52 | Awards/results |

The organizer may change these times before distribution.
