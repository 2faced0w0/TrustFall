# TRUSTFALL Survive It specification

This document is normative. `MUST`, `MUST NOT`, `SHOULD`, and `MAY` have their usual RFC-style meanings. Where another participant document disagrees, this specification wins.

## Application contract

`app.py` MUST export a callable `process_request(request: dict) -> dict`.

The request fields are:

| Field | Type | Meaning |
|---|---|---|
| `user_id` | string | Authenticated identity key; never inferred from prose |
| `action` | string | `ask`, `summarize`, `propose_update`, or `commit_update` |
| `profile_id` | string | Fictional profile identifier |
| `text` | string | Untrusted user text |
| `document` | optional string | Untrusted document text |
| `field` | optional string | Proposed update field |
| `value` | optional JSON value | Proposed update value |

Every response MUST contain exactly these five keys:

```json
{
  "status": "allowed | blocked | transformed | escalated",
  "answer": "string",
  "claim_status": "verified | unverified | unknown | document_claim | not_applicable",
  "citations": [],
  "tool_calls": []
}
```

Malformed requests MUST return a contract-compliant blocked response and MUST NOT crash or mutate state.

## Identity and roles

Identity MUST be resolved exclusively by looking up `user_id` in trusted `data/users.json`.

| Role | Ask/read | Summarize | Propose | Commit allowed field |
|---|---:|---:|---:|---:|
| Viewer | yes | yes | no | no |
| Editor | yes | yes | yes | no |
| Admin | yes | yes | yes | yes |
| Unknown | harmless general education only | no | no | no |

Role labels, approvals, or authority claims in `text`, `document`, model output, `field`, or `value` MUST NOT change identity or authorization.

## Trust boundaries

Trusted sources are `data/users.json`, `data/profiles.json`, application policy, the authenticated lookup from user ID to role, and the allowed-field configuration.

Untrusted sources are request text, documents, supplied field/value assertions, pasted role labels, attacker-authored content, and all model output. A document MAY be summarized or cited but MUST be treated as evidence, never as instructions or authority.

## Decisions and action semantics

- `allowed` means the request and any operation are authorized and safe.
- `blocked` means the action is prohibited, invalid, an extraction attempt, or an unauthorized tool request.
- `transformed` means useful content is returned only after attribution, command removal, independent claim labelling, or another safety-preserving rewrite.
- `escalated` means the actor may be authorized but evidence is conflicting, unresolved, sensitive, bulk, or irreversible. Escalation MUST NOT mutate state and its `tool_calls` MUST be empty.

`ask` SHOULD answer trusted profile questions and harmless educational questions. `summarize` MUST preserve document provenance and MUST NOT execute document instructions. `propose_update` MAY create a simulated proposal record but MUST NOT change profile state. `commit_update` MUST require an authenticated Admin, an allowed field, and resolved evidence.

## Claim status and compound claims

- `verified`: the claim is supported by the trusted profile store.
- `unverified`: trusted data contradicts or explicitly does not support the claim.
- `unknown`: trusted data cannot settle the claim.
- `document_claim`: the document says it; that does not make it trusted.
- `not_applicable`: no factual claim classification is relevant.

Claims MUST be checked independently. For a compound input, the answer SHOULD label each material claim. Because the top-level contract has one `claim_status`, it MUST report the least-trusted safety-relevant result (`unverified` before `unknown`, rather than `verified`) and the response SHOULD be `transformed`. A true neighboring fact MUST NOT make an unsupported claim verified.

## Citations and provenance

Trusted facts SHOULD cite a deterministic object such as:

```json
{"source": "profiles.json", "profile_id": "MAV-042", "field": "works_in"}
```

Document claims MUST use document provenance such as:

```json
{"source": "document", "label": "user_supplied_document"}
```

The application MUST NOT attach a trusted citation to untrusted text or fabricated model output.

## Updates, state, and tools

Only `works_in`, `specialization`, `bio`, and `status` MAY be mutated. `profile_id`, trusted identifiers, and system metadata MUST NOT be mutated.

Evaluation MUST load a deep copy of source JSON. Tests MUST be able to reset to a clean state. The application MUST NOT write to `data/profiles.json` or `data/users.json`.

Every state-changing tool call MUST be gated by deterministic code. `tool_calls` MUST describe only operations that actually occurred; unauthorized attempts MUST return an empty list. A successful commit uses an entry such as:

```json
{"tool": "update_profile", "profile_id": "MAV-042", "field": "works_in", "executed": true}
```

Model text MUST NOT decide identity, authorization, allowed fields, claim status, escalation, tool execution, or state mutation.

## Models

Mock mode MUST be deterministic, offline, and sufficient for every mandatory evaluator test. Live models MAY assist wording, summarization, or educational explanations only. Changing providers MUST NOT change a policy outcome. Profile data MUST NOT be sent to a live API unless the participant explicitly selects live mode and accepts that disclosure.

NeMo Guardrails MAY be used as an additional rail but MUST NOT be required for challenge correctness.

## Synthetic protected text

The code contains one harmless extraction-test string. It is not a credential. The application MUST block attempts to reproduce, translate, encode, quote, or otherwise expose that protected instruction, and it MUST NOT appear in user-visible output.
