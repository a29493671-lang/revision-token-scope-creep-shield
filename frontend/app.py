import streamlit as st
from api_client import (
    API_BASE_URL,
    check_health,
    create_milestone,
    create_project,
    create_quote,
    create_revision,
    get_milestones,
    get_notifications,
    get_project_activity,
    get_projects,
    get_quotes,
    get_revisions,
    login_user,
    mark_notification_read,
    register_client,
    register_freelancer,
    update_quote_status,
)

st.set_page_config(
    page_title="Revision Token & Scope-Creep Shield",
    page_icon="🛡️",
    layout="wide",
)

# --- SESSION STATE ---
if "token" not in st.session_state:
    st.session_state.token = None
if "user" not in st.session_state:
    st.session_state.user = None

# --- SIDEBAR: HEALTH, AUTH & DEMO ACCESS ---
with st.sidebar:
    st.title("🛡️ Revision Shield")
    st.caption(f"Backend: `{API_BASE_URL}`")

    health_data, health_err = check_health()
    if health_err or (health_data and health_data.get("status") != "healthy"):
        st.error(f"Backend Offline ({health_err or 'DB disconnected'})")
    else:
        st.success("API & Database Connected")

    st.divider()

    if st.session_state.user:
        u = st.session_state.user
        role_badge = "🛠️ FREELANCER" if u["role"] == "FREELANCER" else "👤 CLIENT"
        st.markdown(f"### Logged in: {u['name']}")
        st.markdown(f"**Role:** `{role_badge}`")
        st.caption(f"Email: {u['email']} (ID: {u['id']})")

        if st.button("🚪 Logout / Switch Role", use_container_width=True):
            st.session_state.token = None
            st.session_state.user = None
            st.rerun()

        # --- NOTIFICATIONS PANEL ---
        st.divider()
        notif_data, notif_err = get_notifications(st.session_state.token)
        if not notif_err and notif_data:
            unread = notif_data.get("unread_notifications", 0)
            st.subheader(f"🔔 Notifications ({unread} unread)")
            for n in notif_data.get("notifications", [])[:6]:
                prefix = "🔵 " if not n["is_read"] else "⚪ "
                st.caption(f"{prefix}{n['message']}")
                if not n["is_read"]:
                    if st.button("Mark read", key=f"read_{n['id']}"):
                        mark_notification_read(st.session_state.token, n["id"])
                        st.rerun()
    else:
        st.info("Demo Access Portal — Log in or register below.")

# --- LANDING / AUTH SCREEN WHEN NOT LOGGED IN ---
if not st.session_state.token or not st.session_state.user:
    st.title("🛡️ Revision Token & Scope-Creep Shield")
    st.markdown(
        "A client-approval portal that makes freelance revisions visible, limited (3 free tokens per milestone), and trackable."
    )

    tab_login, tab_reg_client, tab_reg_free = st.tabs(
        ["🔑 Login", "👤 Register Client", "🛠️ Register Freelancer"]
    )

    with tab_login:
        with st.form("login_form"):
            st.subheader("Sign In (Client or Freelancer)")
            l_email = st.text_input("Email", placeholder="client@demo.com or freelancer@demo.com")
            l_pw = st.text_input("Password", type="password", placeholder="Minimum 8 characters")
            if st.form_submit_button("Login", use_container_width=True):
                res, err = login_user(l_email.strip(), l_pw)
                if err:
                    st.error(err)
                else:
                    st.session_state.token = res["access_token"]
                    st.session_state.user = res["user"]
                    st.success("Logged in!")
                    st.rerun()

    with tab_reg_client:
        with st.form("reg_client_form", clear_on_submit=True):
            st.subheader("Create a Client Account")
            c_name = st.text_input("Full Name", value="Demo Client")
            c_email = st.text_input("Client Email", value="client@demo.com")
            c_pw = st.text_input("Password (min 8 chars)", type="password", value="password123")
            if st.form_submit_button("Register as Client", use_container_width=True):
                res, err = register_client(c_name, c_email, c_pw)
                if err:
                    st.error(err)
                else:
                    st.success(f"Client '{res['email']}' registered! Go to the Login tab to sign in.")

    with tab_reg_free:
        with st.form("reg_freelancer_form", clear_on_submit=True):
            st.subheader("Create a Freelancer Account")
            st.caption("Note: Matches `FREELANCER_INVITE_CODE` in your backend `.env` file.")
            f_name = st.text_input("Full Name", value="Demo Freelancer")
            f_email = st.text_input("Freelancer Email", value="freelancer@demo.com")
            f_pw = st.text_input("Password (min 8 chars)", type="password", value="password123")
            f_code = st.text_input("Freelancer Invite Code", placeholder="Enter FREELANCER_INVITE_CODE from .env")
            if st.form_submit_button("Register as Freelancer", use_container_width=True):
                res, err = register_freelancer(f_name, f_email, f_pw, f_code)
                if err:
                    st.error(err)
                else:
                    st.success(f"Freelancer '{res['email']}' registered! Go to the Login tab to sign in.")

    st.stop()

# ==============================================================================
# AUTHENTICATED DASHBOARD (FREELANCER OR CLIENT)
# ==============================================================================
token = st.session_state.token
user = st.session_state.user
role = user["role"]  # "FREELANCER" or "CLIENT"

st.title(f"{'🛠️ Freelancer' if role == 'FREELANCER' else '👤 Client'} Dashboard")

# --- FETCH PROJECTS ---
proj_data, proj_err = get_projects(token)
if proj_err:
    st.error(f"Failed to load projects: {proj_err}")
    st.stop()

projects = proj_data.get("projects", [])

# --- FREELANCER: CREATE PROJECT ---
if role == "FREELANCER":
    with st.expander("➕ Create New Project", expanded=(len(projects) == 0)):
        st.caption("Note: The Client Email must already be registered as a CLIENT account.")
        with st.form("create_project_form", clear_on_submit=True):
            p_title = st.text_input("Project Title *")
            p_desc = st.text_area("Project Scope & Agreement *")
            p_client_email = st.text_input("Registered Client Email *", value="client@demo.com")
            if st.form_submit_button("Create Project"):
                if not p_title.strip() or not p_desc.strip() or not p_client_email.strip():
                    st.error("All fields are required.")
                else:
                    res, err = create_project(token, p_title, p_desc, p_client_email)
                    if err:
                        st.error(err)
                    else:
                        st.success(res.get("message", "Project created!"))
                        st.rerun()

if not projects:
    if role == "CLIENT":
        st.info(
            f"No projects assigned to `{user['email']}` yet. Ask your Freelancer to create a project using your email address."
        )
    st.stop()

# --- SELECT PROJECT ---
proj_map = {f"#{p['id']} — {p['title']} (Client: {p['client_name']})": p for p in projects}
selected_proj_label = st.selectbox("📂 Select Project", list(proj_map.keys()))
active_project = proj_map[selected_proj_label]
project_id = active_project["id"]

st.caption(f"**Project Scope:** {active_project['description']}")

# --- FREELANCER: CREATE MILESTONE ---
if role == "FREELANCER":
    with st.expander("➕ Add Milestone (Initialises with 3 Free Revision Tokens)"):
        with st.form("create_milestone_form", clear_on_submit=True):
            m_title = st.text_input("Milestone Title *")
            m_desc = st.text_area("Milestone Deliverables & Scope *")
            if st.form_submit_button("Create Milestone"):
                if not m_title.strip() or not m_desc.strip():
                    st.error("Milestone title and description are required.")
                else:
                    res, err = create_milestone(token, project_id, m_title, m_desc)
                    if err:
                        st.error(err)
                    else:
                        st.success(res.get("message", "Milestone created with 3 free tokens!"))
                        st.rerun()

# --- FETCH MILESTONES ---
m_data, m_err = get_milestones(token, project_id)
if m_err:
    st.error(f"Could not load milestones: {m_err}")
    st.stop()

milestones = m_data.get("milestones", [])
if not milestones:
    st.warning("No milestones exist for this project yet.")
    st.stop()

m_map = {
    f"#{m['id']} — {m['title']} ({m['tokens_remaining']}/{m['tokens_total']} free tokens)": m
    for m in milestones
}
selected_m_label = st.selectbox("🎯 Select Milestone", list(m_map.keys()))
active_milestone = m_map[selected_m_label]
milestone_id = active_milestone["id"]

tokens_rem = active_milestone["tokens_remaining"]
tokens_tot = active_milestone["tokens_total"]

# --- MILESTONE TOKEN STATUS CARDS ---
st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("Milestone", active_milestone["title"])
col2.metric("Free Revision Tokens Remaining", f"{tokens_rem} / {tokens_tot}")
col3.metric("Milestone Status", active_milestone["status"])

visual_tokens = "🟢 " * tokens_rem + "⚪ " * max(0, tokens_tot - tokens_rem)
st.markdown(f"**Token Balance Visual:** {visual_tokens} &nbsp; *(Scope: {active_milestone['description']})*")

# ==============================================================================
# CLIENT: SUBMIT REVISION REQUEST
# ==============================================================================
if role == "CLIENT":
    st.subheader("📝 Submit a Revision Request")
    if tokens_rem > 0:
        st.info(
            f"You have **{tokens_rem}** free revision token(s) remaining. Submitting this form will consume **1 free token**."
        )
    else:
        st.warning(
            "🚨 **0 Free Tokens Remaining!** All 3 included revisions have been used. "
            "Submitting another request will mark it as **Out-of-Scope** and require a paid **Add-On Quote** from the freelancer. Your token balance will stay at 0."
        )

    with st.form("submit_revision_form", clear_on_submit=True):
        rev_title = st.text_input("Concise Revision Title *", placeholder="e.g., Update hero banner colors")
        rev_details = st.text_area(
            "Detailed Change Description *",
            placeholder="Describe exactly what needs to be changed...",
        )
        rev_link = st.text_input(
            "Optional Reference URL (Figma / Drive / Screenshot Link)",
            placeholder="https://...",
        )
        submitted = st.form_submit_button("Submit Revision")

        if submitted:
            if not rev_title.strip() or not rev_details.strip():
                st.error("Validation Error: Title and Detailed Description cannot be blank. No token was deducted.")
            else:
                # Format into request_description required by RevisionCreate schema
                combined_desc = f"[{rev_title.strip()}] {rev_details.strip()}"
                if rev_link.strip():
                    combined_desc += f" | Reference URL: {rev_link.strip()}"

                res, err = create_revision(token, project_id, milestone_id, combined_desc)
                if err:
                    st.error(f"Submission failed — no token was deducted. ({err})")
                else:
                    new_rev = res.get("revision", {})
                    new_bal = res.get("tokens_remaining", tokens_rem)
                    rev_type = new_rev.get("revision_type", "")
                    if "FREE" in rev_type.upper():
                        st.success(
                            f"Revision submitted using 1 free token! Remaining balance: {new_bal}"
                        )
                    else:
                        st.warning(
                            f"Out-of-Scope revision recorded ({rev_type})! Token balance remains {new_bal}. Awaiting Freelancer add-on quote."
                        )
                    st.rerun()

# ==============================================================================
# SHARED: REVISION HISTORY & ADD-ON QUOTES
# ==============================================================================
st.divider()
st.subheader("📜 Timestamped Revision History & Add-On Quotes")

rev_data, rev_err = get_revisions(token, project_id, milestone_id)
quote_data, quote_err = get_quotes(token, project_id)

revisions = rev_data.get("revisions", []) if rev_data else []
quotes = quote_data.get("quotes", []) if quote_data else []
quotes_by_rev = {q["revision_id"]: q for q in quotes}

if rev_err:
    st.error(f"Error loading revisions: {rev_err}")
elif not revisions:
    st.caption("No revision requests submitted for this milestone yet.")
else:
    for idx, rev in enumerate(revisions, start=1):
        rev_id = rev["id"]
        r_type = rev["revision_type"]
        r_status = rev["status"]
        is_free = "FREE" in r_type.upper()
        badge = "🟢 FREE TOKEN" if is_free else f"🟠 {r_type} (Out-of-Scope)"

        with st.container(border=True):
            st.markdown(
                f"#### Request #{idx} (ID: `{rev_id}`) — {badge} &nbsp;|&nbsp; Status: **`{r_status}`**"
            )
            st.write(rev["request_description"])

            linked_quote = quotes_by_rev.get(rev_id)

            # Display existing quote if created
            if linked_quote:
                q_id = linked_quote["id"]
                q_amt = linked_quote["amount"]
                q_curr = linked_quote["currency"]
                q_stat = linked_quote["status"]
                q_desc = linked_quote["description"]

                st.info(
                    f"💰 **Add-On Quote #{q_id}:** `{q_curr} {q_amt}` — **{q_stat}**\n\n"
                    f"*Scope Note:* {q_desc}"
                )

                # CLIENT can Accept or Reject a PENDING quote
                if role == "CLIENT" and q_stat == "PENDING":
                    qc1, qc2 = st.columns(2)
                    if qc1.button("✅ Accept Quote", key=f"acc_{q_id}", use_container_width=True):
                        _, q_err = update_quote_status(token, project_id, q_id, "ACCEPTED")
                        if q_err:
                            st.error(q_err)
                        else:
                            st.success("Quote accepted!")
                            st.rerun()
                    if qc2.button("❌ Reject Quote", key=f"rej_{q_id}", use_container_width=True):
                        _, q_err = update_quote_status(token, project_id, q_id, "REJECTED")
                        if q_err:
                            st.error(q_err)
                        else:
                            st.warning("Quote rejected.")
                            st.rerun()

            # FREELANCER can generate an Add-On Quote for out-of-scope requests without a quote
            elif not is_free and role == "FREELANCER":
                with st.expander(f"💲 Generate Add-On Quote for Out-of-Scope Request #{idx}"):
                    with st.form(f"quote_form_{rev_id}", clear_on_submit=True):
                        q_amount = st.number_input("Estimate Amount", min_value=1.0, value=1500.0, step=100.0)
                        q_currency = st.text_input("Currency (3-letter ISO)", value="INR", max_chars=3)
                        q_scope = st.text_input(
                            "Quote Scope Description",
                            value=f"Additional out-of-scope work for Revision #{rev_id}",
                        )
                        if st.form_submit_button("Send Add-On Quote to Client"):
                            _, q_err = create_quote(
                                token, project_id, rev_id, q_amount, q_scope, q_currency
                            )
                            if q_err:
                                st.error(q_err)
                            else:
                                st.success("Add-on quote created and sent to client!")
                                st.rerun()
            elif not is_free and role == "CLIENT":
                st.caption("⏳ *Waiting for Freelancer to issue an add-on quote estimate for this out-of-scope request.*")

# ==============================================================================
# SHARED: PROJECT AUDIT / ACTIVITY LOG
# ==============================================================================
st.divider()
with st.expander("📊 View Timestamped Project Activity Log"):
    act_data, act_err = get_project_activity(token, project_id)
    if act_err:
        st.error(act_err)
    elif act_data and act_data.get("activities"):
        for act in act_data["activities"]:
            st.markdown(
                f"- **`{act['created_at']}`** — **{act['action']}** (User #{act['actor_id']}): {act.get('details', '')}"
            )
    else:
        st.caption("No activity logs recorded yet.")