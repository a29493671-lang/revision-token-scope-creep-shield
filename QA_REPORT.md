\# QA \& Testing Report (Person 4)



\## 1. Automated Test Suite \& Execution Evidence

\* \*\*Run Command:\*\* `py -m pytest -v -W ignore`

\* \*\*Result:\*\* \*\*24 passed\*\* (`backend/tests/`, `tests/test\_api.py`, `tests/test\_qa\_edge\_cases.py`)

\* \*\*Verified Scenarios (`T01`–`T09`):\*\*

&#x20; \* `T01`: Milestone creation initializes balance to 3 free tokens.

&#x20; \* `T02–T03`: Requests 1, 2, and 3 consume 1 token each (`3 -> 2 -> 1 -> 0`) with `FREE\_TOKEN`.

&#x20; \* `T04`: Request 4 creates an `ADD\_ON` request and pending quote while keeping balance at `0`.

&#x20; \* `T05–T07`: Invalid/blank payloads, unknown milestone IDs (`404`), and failed requests roll back without deducting tokens.

&#x20; \* `T08`: Unauthenticated and unauthorized role requests are blocked (`401`/`403`/`404`).

&#x20; \* `T09`: Concurrent requests when 1 token remains prevent negative balances or double deductions.



\## 2. Manual End-to-End Test Checklist

\* \[x] Verified `.env` is excluded by `.gitignore` and no real secrets are committed to Git.

\* \[x] Executed full automated backend test suite (`24 passed`).

\* \[x] Verified milestone creation starts with 3 free tokens and 4th request creates a pending quote.

\* \[ ] Pending: Full Streamlit UI walkthrough once frontend screens are merged to `main`.



\## 3. Bug Log

| Bug ID | Severity | Reproduction Steps | Expected Result | Actual Result | Owner | Status |

| :--- | :--- | :--- | :--- | :--- | :--- | :--- |

| \*\*BUG-01\*\* | Medium | Copy `.env.example` to `.env` and run `pytest` | Works out of the box for local/CI tests | Raises `RuntimeError: A valid SECRET\_KEY must be configured in .env` | Person 2 / 5 | Open |

| \*\*BUG-02\*\* | Low | Run `pytest` with a 31-byte `SECRET\_KEY` | No JWT key-length warnings | PyJWT emits `InsecureKeyLengthWarning` (key < 32 bytes for SHA256) | Person 2 | Open |

| \*\*BUG-03\*\* | Low | Inspect repository root structure | Unified `backend/` or `app/` directory | Both `app/` and `backend/` folders exist in root | Person 2 / 5 | Open |

| \*\*BUG-04\*\* | Medium | Check repository for Streamlit UI | `frontend/` folder present for UI verification | Frontend UI not yet pushed to `main` | Person 1 | Open |



\## 4. Quality Summary \& Known Limitations

\* \*\*What was tested:\*\* Automated API and token state-machine tests (`24 passed`), validation error handling, rollback safety, and secret configuration hygiene.

\* \*\*Known Limitations:\*\* SQLAlchemy uses deprecated `datetime.utcnow()` calls; full browser UI walkthrough awaits the final frontend merge.

\*

