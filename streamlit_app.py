import streamlit as st
import requests



def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None
        st.session_state.role = None
        st.session_state.token = None

init_session() # Run this first!

st.set_page_config(page_title="AI Recruitment Portal", page_icon="🎯", layout="wide")

# FastAPI Backend URL
BASE_URL = "http://127.0.0.1:8000/api/v1"

# --- 1. SESSION INITIALIZATION (MUST BE AT THE TOP) ---
if "logged_in" not in st.session_state:
    st.session_state.update({
        "logged_in": False, 
        "username": None, 
        "role": None, 
        "token": None
    })

# --- 2. AUTHENTICATION UI (GATEKEEPER) ---
if not st.session_state.logged_in:
    st.title("🤖 AI Hiring & Shortlisting System")
    tab_login, tab_signup = st.tabs(["🔐 Login", "📝 Create Account"])

    with tab_login:
        with st.form("login_form"):
            u = st.text_input("Username")
            p = st.text_input("Password", type="password")
            if st.form_submit_button("Login", use_container_width=True):
                try:
                    res = requests.post(f"{BASE_URL}/login", params={"username": u, "password": p})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.update({
                            "logged_in": True,
                            "username": data.get('username'),
                            "role": data.get('role'),
                            "token": data.get('access_token') # JWT Token stored here
                        })
                        st.success(f"Session active for 60 mins. Welcome, {data['username']}!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

    with tab_signup:
        with st.form("signup_form"):
            nu = st.text_input("New Username")
            np = st.text_input("New Password", type="password")
            nr = st.selectbox("I am a:", ["candidate", "recruiter"])
            if st.form_submit_button("Sign Up", use_container_width=True):
                try:
                    res = requests.post(f"{BASE_URL}/signup", params={"username": nu, "password": np, "role": nr})
                    if res.status_code == 200:
                        st.success("Account created! Switch to the Login tab.")
                    else:
                        st.error("Signup failed. Username might be taken.")
                except Exception as e:
                    st.error(f"Error: {e}")

# --- 3. PROTECTED CONTENT (LOGGED IN) ---
else:
    # Sidebar Profile & Logout
    st.sidebar.title(f"👤 {st.session_state.username}")
    st.sidebar.info(f"Role: **{st.session_state.role.upper()}**")
    
    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.update({"logged_in": False, "username": None, "role": None, "token": None})
        st.rerun()

    # RBAC: Dynamic Navigation
    menu = ["Post a Job", "Recruiter Dashboard"] if st.session_state.role == "recruiter" else ["Candidate Portal"]
    choice = st.sidebar.radio("Navigation", menu)

    # ---------------------------------------------------------
    # RECRUITER: POST A JOB
    # ---------------------------------------------------------
    if choice == "Post a Job":
        st.header("📝 Create a New Vacancy")
        with st.form("job_form", clear_on_submit=True):
            t = st.text_input("Job Title")
            d = st.text_area("Description")
            r = st.text_area("Requirements (Skills)")
            if st.form_submit_button("Publish Job"):
                if t and d and r:
                    requests.post(f"{BASE_URL}/jobs/", json={"title": t, "description": d, "requirements": r})
                    st.success(f"Job '{t}' posted!")
                else:
                    st.warning("All fields are required.")

    # ---------------------------------------------------------
    # RECRUITER: DASHBOARD (SELECT / REJECT)
    # ---------------------------------------------------------
    elif choice == "Recruiter Dashboard":
        st.header("📊 Application Management")
        try:
            jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if jobs:
                job_list = {j['title']: j['id'] for j in jobs}
                sel_job = st.selectbox("Select Job", list(job_list.keys()))
                j_id = job_list[sel_job]

                st.divider()
                cands = requests.get(f"{BASE_URL}/jobs/{j_id}/shortlist").json()
                
                if not cands:
                    st.info("No candidates yet.")
                else:
                    for c in cands:
                        cid, cname, cstatus = c.get('id'), c.get('full_name'), c.get('status')
                        cscore = c.get('score', 0)

                        # Color-Coded Expander Title
                        header = f"🟡 PENDING: {cname} ({cscore}%)"
                        if cstatus == "Selected": header = f"🟢 SELECTED: {cname} ({cscore}%)"
                        elif cstatus == "Rejected": header = f"🔴 REJECTED: {cname} ({cscore}%)"

                        with st.expander(header):
                            st.write(f"**Email:** {c.get('email')}")
                            if cstatus == "Selected": st.success("Candidate Hired")
                            elif cstatus == "Rejected": st.error("Candidate Rejected")

                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button(f"✅ Hire {cname}", key=f"h_{cid}", type="primary", use_container_width=True):
                                    requests.put(f"{BASE_URL}/candidates/{cid}/status", params={"status": "Selected"})
                                    st.rerun()
                            with col2:
                                if st.button(f"❌ Reject {cname}", key=f"r_{cid}", use_container_width=True):
                                    requests.put(f"{BASE_URL}/candidates/{cid}/status", params={"status": "Rejected"})
                                    st.rerun()
            else: st.warning("No jobs found.")
        except Exception as e:
            st.error(f"Dashboard Error: {e}")

    # ---------------------------------------------------------
    # CANDIDATE: PORTAL (APPLY & STATUS)
    # ---------------------------------------------------------
    elif choice == "Candidate Portal":
        st.header(f"🚀 Hello, {st.session_state.username}")
        t1, t2 = st.tabs(["📤 Apply", "🔍 My Status"])

        with t1:
            all_jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if all_jobs:
                j_map = {j['title']: j['id'] for j in all_jobs}
                target = st.selectbox("Position", list(j_map.keys()))
                with st.form("apply_form"):
                    email = st.text_input("Your Email")
                    pdf = st.file_uploader("Resume (PDF)", type=["pdf"])
                    if st.form_submit_button("Submit"):
                        if email and pdf:
                            with st.spinner("AI is analyzing..."):
                                files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
                                d = {"job_id": j_map[target], "full_name": st.session_state.username, "email": email}
                                res = requests.post(f"{BASE_URL}/apply/", data=d, files=files)
                                st.success(f"Applied! AI Match: {res.json().get('score')}%")

        with t2:
            st.subheader("Check Application Progress")
            mail_check = st.text_input("Enter your application email:")
            if st.button("Fetch My Status", use_container_width=True):
                res = requests.get(f"{BASE_URL}/my-applications/{mail_check}")
                if res.status_code == 200:
                    apps = res.json()
                    if not apps: st.info("No applications found.")
                    for a in apps:
                        st.write("---")
                        # Uses 'job_title' from the Join logic in Backend
                        st.markdown(f"### Role: {a.get('job_title', 'Unknown Role')}")
                        s = a.get('status', 'Pending')
                        if s == "Selected": st.success(f"Status: {s} ✅")
                        elif s == "Rejected": st.error(f"Status: {s} ❌")
                        else: st.warning(f"Status: {s} ⏳")


