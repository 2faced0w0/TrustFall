# Optional NeMo Guardrails illustration

This directory is optional and is not imported by the application or required by evaluation. It sketches how input, dialogue, and output rails might complement the deterministic Python layer.

NeMo must not decide identity, authorization, allowed update fields, claim truth, or tool execution. Those controls remain in `policy.py`, `claim_verifier.py`, `actions.py`, and `state.py`. Treat the files here as a starting illustration and confirm compatibility with the NeMo version you choose.
