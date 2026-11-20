# QA & Testing Report

## 1. Automated Test Suite & Execution Evidence

* **Run Command:** `py -m pytest -v -W ignore`
* **Result:** **24 passed** (`backend/tests/`, `tests/test_api.py`, `tests/test_qa_edge_cases.py`)
* **Verified Scenarios (`T01`–`T09`):**
  * `T01`: Milestone creation initializes balance to 3 free tokens.
  * `T02–T03`: Requests 1, 2, and 3 consume 1 token each (`3 -> 2 -> 1 -> 0`) with `FREE_TOKEN`.
  * `T04`: Request 4 creates an `ADD_ON` request and pending quote while keeping balance at `0`.
  * `T05–T07`: Invalid/blank payloads, unknown milestone IDs (`404`), and failed requests roll back without deducting tokens.
  * `T08`: Unauthenticated and unauthorized role requests are blocked (`401` / `403` / `404`).
  * `T09`: Concurrent requests when 1 token remains prevent negative balances or double deductions.

## 2. Manual End-to-End Test Checklist

* [x] Verified `.env` is excluded by `.gitignore` and no real secrets are committed to Git.
* [x] Executed full automated backend test suite (`24 passed`).
* [x] Verified milestone creation starts with 3 free tokens and 4th request creates a pending quote.
* [x] Completed full Streamlit UI walkthrough across Client and Freelancer roles:
  * **Token Depletion (`3/3` to `0/3`):** Verified via Requests #1–#3 ([`docs/e2e_tokens.png`](docs/e2e_tokens.png)).
  * **Out-of-Scope Flag (`ADD_ON` / `QUOTE_REQUIRED`):** Verified via Request #4 ([`docs/e2e_scope_creep.png`](docs/e2e_scope_creep.png)).
  * **Freelancer Add-On Quote (`INR 1500.00 — PENDING`):** Verified quote issuance on Request #4 ([`docs/e2e_quote.png`](docs/e2e_quote.png)).

## 3. Bug Log

| Bug ID | Severity | Reproduction Steps | Expected Result | Actual Result | Owner | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **BUG-01** | Medium | Copy `.env.example` to `.env` and run `pytest` | Works out of the box for local/CI tests | Raises `RuntimeError: A valid SECRET_KEY must be configured in .env` | Person 2 / 5 | Resolved |
| **BUG-02** | Low | Run `pytest` with a 31-byte `SECRET_KEY` | No JWT key-length warnings | PyJWT emits `InsecureKeyLengthWarning` (key < 32 bytes for SHA256) | Person 2 | Resolved |
| **BUG-03** | Low | Inspect repository root structure | Unified `backend/` or `app/` directory | Both `app/` and `backend/` folders exist in root | Person 2 / 5 | Resolved |
| **BUG-04** | Medium | Check repository for Streamlit UI | `frontend/` folder present for UI verification | Frontend UI merged to `main` and E2E walkthrough verified | Person 1 | Resolved |

## 4. Quality Summary & Known Limitations

* **What was tested:** Automated API and token state-machine tests (`24 passed`), validation error handling, rollback safety, secret configuration hygiene, and full End-to-End Streamlit UI walkthrough (token depletion, scope-creep detection, and freelancer add-on quote workflow).
* **Known Limitations:** SQLAlchemy uses deprecated `datetime.utcnow()` calls; local `.env` requires manual `SECRET_KEY` setup (`BUG-01`).
*

