# TRUSTFALL — Survive It starter kit

Build the deterministic trust and decision layer around a fictional profile assistant. The application is a plain Python library: evaluators import `process_request` from `app.py`. Mock mode is the default and is sufficient for all mandatory evaluation.

## 1. Setup

Python 3.11 or 3.12 is supported.

```text
python -m venv .venv
```

Windows PowerShell:

```text
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```text
.venv\Scripts\activate.bat
```

macOS/Linux:

```text
source .venv/bin/activate
```

```text
python -m pip install -r requirements.txt
```

## 2. Run tests

```text
python -m unittest discover -s tests -v
```

The starter is intentionally incomplete: 20 public tests run, with **15 expected to pass and 5 expected to fail** around compound claims and untrusted document transformation. Imports, Mock mode, basic utility, role-based commit blocking, state isolation, and extraction protection should work. Your goal is to make every public test pass without merely matching the published strings and without breaking honest requests.

## 3. Inspect the contract

Read `SPEC.md`; it is normative. Then inspect `app.py`, `policy.py`, `claim_verifier.py`, `actions.py`, and `state.py`. Search for `TODO(participant)`.

## 4. Choose a provider

Mock requires no network or credential:

```text
set TRUSTFALL_PROVIDER=mock
python scripts/check_provider.py
```

On PowerShell use `$env:TRUSTFALL_PROVIDER='mock'`; on macOS/Linux use `export TRUSTFALL_PROVIDER=mock`. For an optional live provider, copy `.env.example` to `.env`, set one provider key and an explicit model name, and never submit `.env`.

## 5. Run a sample request

```text
python -c "from app import process_request; print(process_request({'user_id':'U_VIEW_01','action':'ask','profile_id':'MAV-042','text':'Where does MAV-042 work?'}))"
```

## 6. Fill the team manifest

After teams are revealed, fill `team_id` and member aliases in `team_manifest.json`. Do not use real names if aliases are preferred.

## 7. Build

Keep identity separate from prose, verify claims against trusted JSON, attribute documents, and gate every state-changing action in deterministic Python. A model may improve wording only.

## 8. Submit attacks

Replace `attacks/attacks.json` with exactly five attacks across at least three categories. Read `attacks/README.md` and use `Attack_Template.json`.

## 9. Validate

```text
python scripts/validate_submission.py
```

The initial starter will not validate as a final submission: the team fields and attacks are intentionally blank and baseline TODO tests fail.

## 10. Freeze

```text
python scripts/freeze_snapshot.py --label pre-patch
python scripts/freeze_snapshot.py --label final
```

Snapshots exclude `.env`, caches, Git metadata, and earlier snapshots, and include a SHA-256 manifest.

## Troubleshooting

- **Tests cannot import `app`:** run the command from this folder and keep `app.py` at the root.
- **Invalid response keys:** return exactly `status`, `answer`, `claim_status`, `citations`, and `tool_calls` on every path.
- **Malformed manifest:** validate the JSON and fill a non-empty team ID plus alias list.
- **Attack validation fails:** provide exactly five unique IDs, at least three valid categories, and complete request/rationale fields.
- **Provider unavailable, 401/403, 429, or bad model:** switch to Mock; provider availability and choice are not scored.
- **State looks dirty between tests:** call `reset_state()` in setup and never write the source JSON.
- **Unexpected `tool_calls`:** return only operations that actually occurred; blocked or escalated requests must not mutate.
- **`.env` is present:** remove it before submission; keep only `.env.example`.
- **Snapshot concerns:** inspect `SHA256_MANIFEST.json` and rerun the freeze command with a new label if required.

FreeLLMAPI is intentionally configurable. The organizer must verify its current base URL, endpoint shape, and chosen model before event-day distribution.
