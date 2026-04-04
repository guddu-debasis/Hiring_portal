import streamlit as st
import requests
import os

# --- 1. SETTINGS & PREMIUM THEMING ---
st.set_page_config(
    page_title="MindSpark-Ai | Intelligence-Driven Recruitment",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for a Clean, High-End Look
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at 20% 30%, #1a1c24 0%, #0e1117 100%); }
    
    /* Remove unnecessary spacing at the top */
    .block-container { padding-top: 2rem !important; }

    /* Stunning Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }

    /* Action Buttons Styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
        border: none;
        height: 3rem;
    }

    /* Hire Button (Emerald) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) button {
        background: linear-gradient(135deg, #00b09b, #96c93d) !important;
        color: white !important;
    }
    
    /* Pass Button (Ruby) */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) button {
        background: linear-gradient(135deg, #ff416c, #ff4b2b) !important;
        color: white !important;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.3);
    }

    /* Role Badge */
    .role-badge {
        background: rgba(0, 176, 155, 0.1);
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid #00b09b;
        color: #00b09b;
        font-size: 0.8rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "username": None, "role": None, "token": None})

BASE_URL = st.secrets.get("BASE_URL", "https://hiring-portal-xl3g.onrender.com/api/v1")

# --- 3. AUTHENTICATION UI ---
if not st.session_state.logged_in:
    # (Keeping your login logic the same as it's working well)
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🧠 MindSpark-Ai</h1>", unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["🔐 Login", "🚀 Join"])
        with tab_login:
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Launch Dashboard", use_container_width=True):
                    res = requests.post(f"{BASE_URL}/login", params={"username": u, "password": p})
                    if res.status_code == 200:
                        d = res.json()
                        st.session_state.update({"logged_in": True, "username": d['username'], "role": d['role'], "token": d['access_token']})
                        st.rerun()
        with tab_signup:
            with st.form("signup"):
                nu, np = st.text_input("New Username"), st.text_input("New Password", type="password")
                nr = st.selectbox("Role", ["candidate", "recruiter"])
                if st.form_submit_button("Register", use_container_width=True):
                    requests.post(f"{BASE_URL}/signup", params={"username": nu, "password": np, "role": nr})
                    st.success("Account Created!")
    st.stop()

# --- 4. DASHBOARD CONTENT ---
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        st.markdown(f"<span class='role-badge'>{st.session_state.role.upper()}</span>", unsafe_allow_html=True)
        st.divider()
        menu = ["Post a Job", "Recruiter Dashboard"] if st.session_state.role == "recruiter" else ["Candidate Portal"]
        choice = st.sidebar.radio("Navigation", menu)
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.update({"logged_in": False, "username": None, "role": None, "token": None})
            st.rerun()

    # --- RECRUITER: DASHBOARD ---
    if choice == "Recruiter Dashboard":
        st.title("📊 Talent Intelligence")
        jobs = requests.get(f"{BASE_URL}/jobs/").json()
        if jobs:
            job_list = {j['title']: j['id'] for j in jobs}
            c1, c2 = st.columns([3, 1])
            with c1:
                sel_job = st.selectbox("Select Active Vacancy", list(job_list.keys()))
            with c2:
                st.write("") # Spacer
                if st.button("🗑️ Delete Job", type="secondary", use_container_width=True):
                    requests.delete(f"{BASE_URL}/jobs/{job_list[sel_job]}")
                    st.rerun()

            st.divider()
            cands = requests.get(f"{BASE_URL}/jobs/{job_list[sel_job]}/shortlist").json()
            
            if not cands:
                st.info("No applications yet.")
            else:
                for c in cands:
                    with st.expander(f"👤 {c['full_name']} — Match Score: {c['score']}%"):
                        col_res, col_ai = st.columns([1.6, 1])
                        with col_res:
                            st.markdown("##### 📄 Candidate Portfolio")
                            res_url = c.get('file_path')
                            pdf_display = f'https://docs.google.com/gview?url={res_url}&embedded=true'
                            st.markdown(f'<iframe src="{pdf_display}" width="100%" height="750px" style="border-radius:10px; border:none;"></iframe>', unsafe_allow_html=True)

                        with col_ai:
                            st.markdown("##### 🤖 AI Engine Analysis")
                            st.markdown(f"<div class='glass-card' style='border-left: 5px solid #00b09b;'><b>Summary:</b><br>{c.get('resume_summary')}</div>", unsafe_allow_html=True)
                            st.info(f"**Identified Skills:** {c.get('skills')}")
                            
                            st.divider()
                            # REFINED BUTTONS
                            btn_hire, btn_pass = st.columns(2)
                            with btn_hire:
                                if st.button("✅ HIRE", key=f"h_{c['id']}", use_container_width=True):
                                    requests.put(f"{BASE_URL}/candidates/{c['id']}/status", params={"status": "Selected"})
                                    st.rerun()
                            with btn_pass:
                                if st.button("❌ PASS", key=f"r_{c['id']}", use_container_width=True):
                                    requests.put(f"{BASE_URL}/candidates/{c['id']}/status", params={"status": "Rejected"})
                                    st.rerun()
        else:
            st.warning("No jobs posted yet.")

    # --- RECRUITER: POST A JOB ---
    elif choice == "Post a Job":
        st.title("📝 Broadcast New Opportunity")
        # Cleaned up the container to remove the "ghost" bar
        with st.container():
            with st.form("job_form", clear_on_submit=True):
                t = st.text_input("Job Title", placeholder="e.g. Lead AI Engineer")
                d = st.text_area("Detailed Mission Description", height=150)
                r = st.text_input("Target Skills (comma separated)", placeholder="Python, FastAPI, TiDB")
                if st.form_submit_button("🚀 Deploy to Market", use_container_width=True):
                    requests.post(f"{BASE_URL}/jobs/", json={"title": t, "description": d, "requirements": r}, headers={"Authorization": f"Bearer {st.session_state.token}"})
                    st.success("Opportunity Live!")

    # --- CANDIDATE: PORTAL ---
    elif choice == "Candidate Portal":
        st.title("🚀 Career Command Center")
        tab1, tab2 = st.tabs(["🎯 Available Roles", "📈 My Status"])
        with tab1:
            all_jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if all_jobs:
                job_map = {j['title']: j for j in all_jobs}
                sel_title = st.selectbox("Select Target Mission", list(job_map.keys()))
                job = job_map[sel_title]
                st.markdown(f"<div class='glass-card'><h3>{job['title']}</h3><p>{job['description']}</p></div>", unsafe_allow_html=True)
                with st.form("apply"):
                    email = st.text_input("Contact Email")
                    pdf = st.file_uploader("Upload Digital Resume (PDF)", type=["pdf"])
                    if st.form_submit_button("🚀 Initiate Application", use_container_width=True):
                        if email and pdf:
                            files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
                            requests.post(f"{BASE_URL}/apply/", data={"job_id": job['id'], "full_name": st.session_state.username, "email": email}, files=files)
                            st.success("Application Deployed!")
                            st.balloons()