---

## 🖥️ Streamlit Frontend (UI) Setup & Demo Guide

### 1. Install Frontend Dependencies
```bash
pip install streamlit requests
```

### 2. Start the FastAPI Backend (Terminal 1 — Port 8000)
Make sure the backend server is running at `http://localhost:8000` before using the UI:
```bash
uvicorn app.main:app --reload --port 8000
```
*(Interactive Swagger API docs are available at `http://localhost:8000/docs`)*

### 3. Start the Streamlit Dashboard (Terminal 2 — Port 8501)
Open a second terminal in the repository root and run:
```bash
streamlit run frontend/app.py
```
The UI will open automatically in your browser at **`http://localhost:8501`**.

*(Optional: By default, the UI connects to `http://localhost:8000`. To use a custom backend URL or Docker network address, set the `API_BASE_URL` environment variable before starting Streamlit.)*

### 4. Demo Walkthrough (3 Free Tokens + 4th Request Add-On Quote)
1. **Register Demo Accounts:** On `http://localhost:8501`, use the **Register Client** tab (`client@demo.com`) and **Register Freelancer** tab (`freelancer@demo.com` + the `FREELANCER_INVITE_CODE` from `.env`).
2. **Freelancer Setup:** Log in as the Freelancer, create a new project assigned to `client@demo.com`, and add a milestone (automatically starts with **3 / 3 Free Revision Tokens**).
3. **Client Revisions 1–3 (Free Tokens):** Log in as the Client and submit 3 revision requests. The displayed token balance updates from `3 → 2 → 1 → 0`.
4. **Client Revision 4 (Out-of-Scope):** Submit a 4th revision request. The token balance remains at `0` (never negative) and records the request as **Out-of-Scope**.
5. **Add-On Quote Approval:** Log in as the Freelancer to generate an **Add-On Quote** (in INR) for the 4th request, then switch back to the Client view to **Accept** or **Reject** the quote.