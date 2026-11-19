import os
import requests

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000").rstrip("/")

# Reuse a single HTTP session so Streamlit doesn't open 7 separate TCP connections per click
_session = requests.Session()


def _headers(token: str | None = None) -> dict:
    headers = {"Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _handle_response(resp: requests.Response):
    if resp.status_code >= 400:
        try:
            body = resp.json()
            detail = body.get("detail", body)
        except Exception:
            detail = resp.text
        return None, f"HTTP {resp.status_code}: {detail}"
    if resp.status_code == 204 or not resp.text:
        return {}, None
    return resp.json(), None


def check_health():
    try:
        resp = _session.get(f"{API_BASE_URL}/health", timeout=5)
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"API unreachable at {API_BASE_URL}: {e}"


# --- AUTHENTICATION (/auth) ---
def register_client(name: str, email: str, password: str):
    try:
        resp = _session.post(
            f"{API_BASE_URL}/auth/register",
            json={"name": name, "email": email, "password": password},
            timeout=8,
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


def register_freelancer(name: str, email: str, password: str, invite_code: str):
    try:
        resp = _session.post(
            f"{API_BASE_URL}/auth/register-freelancer",
            json={
                "name": name,
                "email": email,
                "password": password,
                "invite_code": invite_code,
            },
            timeout=8,
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


def login_user(email: str, password: str):
    """Uses OAuth2PasswordRequestForm (application/x-www-form-urlencoded)."""
    try:
        resp = _session.post(
            f"{API_BASE_URL}/auth/login",
            data={"username": email, "password": password},
            timeout=8,
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


def get_me(token: str):
    try:
        resp = _session.get(
            f"{API_BASE_URL}/auth/me", headers=_headers(token), timeout=5
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


# --- PROJECTS (/projects) ---
def get_projects(token: str):
    try:
        resp = _session.get(
            f"{API_BASE_URL}/projects/", headers=_headers(token), timeout=8
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


def create_project(token: str, title: str, description: str, client_email: str):
    try:
        resp = _session.post(
            f"{API_BASE_URL}/projects/",
            headers=_headers(token),
            json={
                "title": title,
                "description": description,
                "client_email": client_email,
            },
            timeout=8,
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


# --- MILESTONES (/projects/{project_id}/milestones) ---
def get_milestones(token: str, project_id: int):
    try:
        resp = _session.get(
            f"{API_BASE_URL}/projects/{project_id}/milestones/",
            headers=_headers(token),
            timeout=8,
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


def create_milestone(token: str, project_id: int, title: str, description: str):
    try:
        resp = _session.post(
            f"{API_BASE_URL}/projects/{project_id}/milestones/",
            headers=_headers(token),
            json={"title": title, "description": description},
            timeout=8,
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


# --- REVISIONS (/projects/{project_id}/milestones/{milestone_id}/revisions) ---
def get_revisions(token: str, project_id: int, milestone_id: int):
    try:
        resp = _session.get(
            f"{API_BASE_URL}/projects/{project_id}/milestones/{milestone_id}/revisions/",
            headers=_headers(token),
            timeout=8,
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


def create_revision(
    token: str, project_id: int, milestone_id: int, request_description: str
):
    try:
        resp = _session.post(
            f"{API_BASE_URL}/projects/{project_id}/milestones/{milestone_id}/revisions/",
            headers=_headers(token),
            json={"request_description": request_description},
            timeout=8,
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


# --- QUOTES (/projects/{project_id}/quotes) ---
def get_quotes(token: str, project_id: int):
    try:
        resp = _session.get(
            f"{API_BASE_URL}/projects/{project_id}/quotes/",
            headers=_headers(token),
            timeout=8,
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


def create_quote(
    token: str,
    project_id: int,
    revision_id: int,
    amount: float,
    description: str,
    currency: str = "INR",
):
    try:
        resp = _session.post(
            f"{API_BASE_URL}/projects/{project_id}/quotes/{revision_id}",
            headers=_headers(token),
            json={
                "amount": amount,
                "description": description,
                "currency": currency.upper(),
            },
            timeout=8,
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


def update_quote_status(token: str, project_id: int, quote_id: int, status: str):
    """Client updates quote status to ACCEPTED or REJECTED."""
    try:
        resp = _session.patch(
            f"{API_BASE_URL}/projects/{project_id}/quotes/{quote_id}/status",
            headers=_headers(token),
            json={"status": status},
            timeout=8,
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


# --- ACTIVITY & NOTIFICATIONS ---
def get_project_activity(token: str, project_id: int):
    try:
        resp = _session.get(
            f"{API_BASE_URL}/projects/{project_id}/activity/",
            headers=_headers(token),
            timeout=8,
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


def get_notifications(token: str):
    try:
        resp = _session.get(
            f"{API_BASE_URL}/notifications/", headers=_headers(token), timeout=8
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"


def mark_notification_read(token: str, notification_id: int):
    try:
        resp = _session.patch(
            f"{API_BASE_URL}/notifications/{notification_id}/read",
            headers=_headers(token),
            timeout=8,
        )
        return _handle_response(resp)
    except requests.exceptions.RequestException as e:
        return None, f"Connection error: {e}"