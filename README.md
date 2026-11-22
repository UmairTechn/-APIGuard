# APIGuard — REST API Security Tester

APIGuard is a Python command-line learning project that checks a **local training API** for:
1. Unauthenticated access to endpoints marked as protected.
2. Cross-account object access (BOLA-style authorization failure).
3. Missing rate limiting (a fixed 20-request lab burst; looks for HTTP 429).
4. Verbose error-message leakage (configured response-text patterns).

## Safety and scope
This project includes deliberately vulnerable demonstration routes. Run it only against the included local Flask lab at `127.0.0.1`. Do not change the target to a public service or a system you do not own or have explicit written permission to test. The Flask server binds to localhost only.

## Requirements
- Python 3.10+
- Windows 10/11, macOS, or Linux

## Install
Open a terminal in this folder and run:

```bash
py -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```

On macOS/Linux, activate with `source .venv/bin/activate`.

## Run the local lab
In Terminal 1:

```bash
python app.py
```

Keep this terminal open. The lab API listens on `http://127.0.0.1:5000`.

## Run APIGuard
Open Terminal 2 in the same project folder, activate the virtual environment, then run:

```bash
python main.py
```

Optional custom file paths:

```bash
python main.py --endpoints config/endpoints.json --tokens config/tokens.json --report reports/report.txt --json-report reports/report.json
```

## Run unit tests

```bash
python -m unittest discover -s tests -v
```

## Understanding results
- **PASS**: The check behaved as expected for the configured lab scenario.
- **FAIL**: The check found behavior that may indicate a weakness.
- **INCONCLUSIVE**: A request failed or the response did not allow a reliable conclusion.
- **N/A**: That probe was not configured for the endpoint.

A PASS does not prove an API is secure. The checks are deliberately small educational checks and should be supplemented with manual review.

## Project structure
- `app.py`: local Flask training API.
- `main.py`: command-line entry point and report writer.
- `config/`: endpoint definitions and dummy lab tokens.
- `probes/`: one Python module per required probe.
- `reports/`: generated text and JSON reports.
- `tests/`: small unit tests.

## Defensive lesson
Authentication verifies who is making a request. Authorization verifies whether that user may access the specific object. APIs should check object ownership on every request, not merely whether a token is valid.
