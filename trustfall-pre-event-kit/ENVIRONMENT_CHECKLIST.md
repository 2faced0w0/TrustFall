# TRUSTFALL environment checklist

Use this kit only to confirm that the laptop can participate on event day.

- [ ] Python 3.11 or 3.12 is installed and is the active `python`.
- [ ] A virtual environment can be created and activated.
- [ ] `python -m pip install -r requirements.txt` succeeds.
- [ ] `python scripts/check_environment.py` ends with `EVENT READY`.
- [ ] `python scripts/check_providers.py` reports Mock as `PASS`.
- [ ] Optional live-provider keys are stored only in a local `.env`.
- [ ] No `.env` or credential file will be submitted.

Mock mode is enough. Live API failure does not prevent event participation.
