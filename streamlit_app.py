import streamlit as st
import requests
import os
import urllib.parse

# --- 1. SETTINGS & PREMIUM THEMING ---
st.set_page_config(
    page_title="MindSpark-Ai | Intelligence-Driven Recruitment",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Modern Glassmorphism CSS
st.markdown("""
    <style>
    .stApp { background: radial-gradient(circle at top right, #1a1c24, #0e1117); }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }

    /* Primary Buttons */
    div.stButton > button {
        border-radius: 12px;
        background: linear-gradient(45deg, #4CAF50, #45a049);
        color: white;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.4);
    }

    /* Delete Button Styling */
    button[kind="primary"] {
        background: linear-gradient(45deg, #ff4b4b, #d32f2f) !important;
    }

    .role-badge {
        background: #1f222d;
        padding: 5px 12px;
        border-radius: 20px;
        border: 1px solid #4CAF50;
        font-size: 0.8rem;
        color: #4CAF50;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INITIALIZATION ---
def init_session():
    if "logged_in" not in st.session_state:
        st.session_state.update({
            "logged_in": False, 
            "username": None, 
            "role": None, 
            "token": None
        })

init_session()
# Ensure this matches your Render Backend URL
BASE_URL = st.secrets.get("BASE_URL", "https://hiring-portal-xl3g.onrender.com/api/v1")

# --- 3. AUTHENTICATION UI ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align: center; margin-top: 50px;'>🧠 MindSpark-Ai</h1>", unsafe_allow_html=True)
        tab_login, tab_signup = st.tabs(["🔐 Secure Entry", "🚀 Join the Network"])

        with tab_login:
            with st.form("login_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Launch Dashboard"):
                    try:
                        res = requests.post(f"{BASE_URL}/login", params={"username": u, "password": p})
                        if res.status_code == 200:
                            data = res.json()
                            st.session_state.update({
                                "logged_in": True,
                                "username": data.get('username'),
                                "role": data.get('role'),
                                "token": data.get('access_token')
                            })
                            st.rerun()
                        else:
                            st.error("Invalid Credentials.")
                    except Exception as e:
                        st.error(f"Backend Offline: {e}")

        with tab_signup:
            with st.form("signup_form"):
                nu = st.text_input("New Username")
                np = st.text_input("New Password", type="password")
                nr = st.selectbox("Role", ["candidate", "recruiter"])
                if st.form_submit_button("Create Account"):
                    requests.post(f"{BASE_URL}/signup", params={"username": nu, "password": np, "role": nr})
                    st.success("Account created! Please Login.")
    st.stop()

# --- 4. PROTECTED CONTENT ---
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        st.markdown(f"<span class='role-badge'>{st.session_state.role.upper()}</span>", unsafe_allow_html=True)
        st.divider()
        
        menu = ["Post a Job", "Recruiter Dashboard"] if st.session_state.role == "recruiter" else ["Candidate Portal"]
        choice = st.sidebar.radio("Navigation", menu)
        
        if st.sidebar.button("🚪 Logout"):
            st.session_state.update({"logged_in": False, "username": None, "role": None, "token": None})
            st.rerun()

    # --- RECRUITER: POST A JOB ---
    if choice == "Post a Job":
        st.title("📝 Post a New Opportunity")
        with st.form("job_form"):
            t = st.text_input("Job Title")
            d = st.text_area("Detailed Description")
            r = st.text_area("Requirements (Skills)")
            if st.form_submit_button("🚀 Publish Vacancy"):
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                requests.post(f"{BASE_URL}/jobs/", json={"title": t, "description": d, "requirements": r}, headers=headers)
                st.success("Job Published!")

    # --- RECRUITER: DASHBOARD (Includes Direct Delete) ---
    elif choice == "Recruiter Dashboard":
        st.title("📊 Talent Intelligence Center")
        try:
            jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if jobs:
                job_list = {j['title']: j['id'] for j in jobs}
                
                # Selection and Deletion row
                col_sel, col_del = st.columns([3, 1])
                with col_sel:
                    sel_job = st.selectbox("Select Active Vacancy", list(job_list.keys()))
                with col_del:
                    st.write("") # Padding
                    st.write("") # Padding
                    if st.button("🗑️ Delete Job", type="primary"):
                        requests.delete(f"{BASE_URL}/jobs/{job_list[sel_job]}")
                        st.rerun()

                st.divider()
                cands = requests.get(f"{BASE_URL}/jobs/{job_list[sel_job]}/shortlist").json()
                
                if not cands:
                    st.info("No candidates yet.")
                else:
                    for c in cands:
                        with st.expander(f"👤 {c['full_name']} — Match: {c['score']}%"):
                            col_res, col_ai = st.columns([1.5, 1])
                            with col_res:
                                st.markdown("##### 📄 Digital Portfolio")
                                res_url = c.get('file_path')
                                if res_url and res_url.startswith("http"):
                                    st.markdown(f'<iframe src="{res_url}" width="100%" height="700px" style="border-radius:12px; border:none; background-color:white;"></iframe>', unsafe_allow_html=True)
                                else:
                                    st.warning("Invalid link. Delete this job and apply again to use Cloudinary.")

                            with col_ai:
                                st.markdown("##### 🤖 AI Analysis")
                                st.markdown(f"<div class='glass-card' style='border-left:4px solid #4CAF50;'>{c.get('resume_summary')}</div>", unsafe_allow_html=True)
                                st.info(f"**Skills:** {c.get('skills')}")
                                if st.button(f"✅ Hire {c['full_name']}", key=f"h_{c['id']}"):
                                    requests.put(f"{BASE_URL}/candidates/{c['id']}/status", params={"status": "Selected"})
                                    st.rerun()
            else:
                st.warning("No active jobs.")
        except Exception as e:
            st.error(f"Dashboard Error: {e}")

    # --- CANDIDATE: PORTAL ---
    elif choice == "Candidate Portal":
        st.title("🚀 Career Launchpad")
        t1, t2 = st.tabs(["🎯 Apply", "📈 Status"])
        with t1:
            all_jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if all_jobs:
                j_lookup = {j['title']: j for j in all_jobs}
                title = st.selectbox("Select Role", list(j_lookup.keys()))
                job = j_lookup[title]
                st.markdown(f"<div class='glass-card'><h3>{job['title']}</h3><p>{job['description']}</p></div>", unsafe_allow_html=True)
                with st.form("apply"):
                    email = st.text_input("Contact Email")
                    pdf = st.file_uploader("Resume (PDF)", type=["pdf"])
                    if st.form_submit_button("🚀 Submit"):
                        if email and pdf:
                            files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
                            res = requests.post(f"{BASE_URL}/apply/", data={"job_id": job['id'], "full_name": st.session_state.username, "email": email}, files=files)
                            if res.status_code == 200:
                                st.success(f"Applied! Score: {res.json().get('score')}%")
                                st.balloons()
        with t2:
            track_email = st.text_input("Email to track")
            if st.button("Track Progress"):
                apps = requests.get(f"{BASE_URL}/my-applications/{track_email}").json()
                for a in apps:
                    st.markdown(f"<div class='glass-card'><b>{a['job_title']}</b> — Status: {a['status']}</div>", unsafe_allow_html=True)