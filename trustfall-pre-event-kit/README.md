# TRUSTFALL pre-event kit

This kit answers one question: **can this laptop and Python environment participate successfully on event day?** It tests supported Python 3.11 or 3.12, imports, JSON and temporary-file support, the request/response shape, and deterministic Mock mode. It contains no challenge data or solution logic.

> Do not build the Survive It challenge ahead of time. This kit only validates your environment.

## Setup

Install Python 3.11 or 3.12, open a terminal in this folder, and create an isolated environment:

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

Install the two lightweight dependencies:

```text
python -m pip install -r requirements.txt
```

## Readiness check

```text
python scripts/check_environment.py
```

The script writes a non-sensitive `readiness_report.json`. A laptop is event-ready when the core environment and Mock model are ready. Live API access is optional.

Run the tests directly with:

```text
python -m unittest discover -s tests -v
```

## Optional live providers

Copy `.env.example` to `.env`, select a provider, set its model name, and add only that provider's key. Never commit or share `.env`.

```text
python scripts/check_providers.py
```

Supported providers are Mock, Google AI Studio, Mistral AI, DeepSeek, Cohere, Groq Cloud, OpenRouter, and configurable FreeLLMAPI. Provider choice is not scored. FreeLLMAPI's base URL and API shape must be confirmed by the organizer before distribution.

## Troubleshooting

- **Wrong Python version:** install Python 3.11 or 3.12 and recreate `.venv` with that interpreter.
- **pip missing:** run `python -m ensurepip --upgrade`, then retry.
- **Activation blocked in PowerShell:** use Command Prompt activation or allow locally signed scripts according to your organization's policy.
- **Package install fails:** check proxy/certificate settings with your IT team, or use an approved offline wheel cache.
- **No API key:** keep `TRUSTFALL_PROVIDER=mock`; no live key is required.
- **Bad live model name:** use a model currently enabled for your provider account.
- **401/403:** verify the selected provider and credential without printing the key.
- **429:** wait for the provider limit to reset or switch to Mock.
- **Provider outage or restricted network:** switch to `TRUSTFALL_PROVIDER=mock`.

**LIVE API FAILURE DOES NOT PREVENT EVENT PARTICIPATION.**
