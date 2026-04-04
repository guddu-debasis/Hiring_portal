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
    .stApp {
        background: linear-gradient(to bottom, #0e1117, #1a1c24);
    }
    div.stButton > button {
        border-radius: 8px;
        border: 1px solid #3e424b;
        background-color: #1f222d;
        color: white;
        transition: all 0.3s ease;
    }
    div.stButton > button:hover {
        border-color: #4CAF50;
        color: #4CAF50;
        box-shadow: 0 0 15px rgba(76, 175, 80, 0.2);
    }
    [data-testid="stSidebar"] {
        background-color: #0e1117;
        border-right: 1px solid #262730;
    }
    .streamlit-expanderHeader {
        background-color: #1f222d !important;
        border-radius: 10px !important;
        border: 1px solid #262730 !important;
    }
    .highlight {
        color: #4CAF50;
        font-weight: bold;
    }
    /* Job Detail Card */
    .job-card {
        background-color: #1f222d;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 20px;
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
BASE_URL = st.secrets.get("BASE_URL", "http://127.0.0.1:8000/api/v1")

# --- 3. AUTHENTICATION UI ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title("🧠 MindSpark-Ai")
        st.subheader("Intelligence-Driven Recruitment")
        
        tab_login, tab_signup = st.tabs(["🔐 Secure Login", "📝 Create Account"])

        with tab_login:
            with st.form("login_form"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Access Dashboard", use_container_width=True):
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
                            st.error("Invalid credentials.")
                    except Exception as e:
                        st.error(f"Backend Offline: {e}")

        with tab_signup:
            with st.form("signup_form"):
                nu = st.text_input("New Username")
                np = st.text_input("New Password", type="password")
                nr = st.selectbox("Define Role", ["candidate", "recruiter"])
                if st.form_submit_button("Register Now", use_container_width=True):
                    try:
                        res = requests.post(f"{BASE_URL}/signup", params={"username": nu, "password": np, "role": nr})
                        if res.status_code == 200:
                            st.success("Account created! You can now login.")
                    except Exception as e:
                        st.error(f"Error: {e}")
    st.stop()

# --- 4. PROTECTED CONTENT ---
else:
    with st.sidebar:
        st.markdown(f"### Welcome, <span class='highlight'>{st.session_state.username}</span>", unsafe_allow_html=True)
        st.caption(f"Role: {st.session_state.role.upper()}")
        st.divider()
        
        menu = ["Post a Job", "Recruiter Dashboard"] if st.session_state.role == "recruiter" else ["Candidate Portal"]
        choice = st.sidebar.radio("Navigation", menu)
        
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Sign Out", use_container_width=True):
            st.session_state.update({"logged_in": False, "username": None, "role": None, "token": None})
            st.rerun()

    # --- RECRUITER: POST A JOB ---
    if choice == "Post a Job":
        st.title("📝 Post a New Opportunity")
        with st.form("job_form", clear_on_submit=True):
            t = st.text_input("Job Title", placeholder="e.g. Senior Backend Engineer")
            d = st.text_area("Detailed Description", placeholder="What will they do?")
            r = st.text_area("Requirements (Skills)", placeholder="e.g. Python, FastAPI, Docker")
            if st.form_submit_button("🚀 Publish Vacancy"):
                if t and d and r:
                    headers = {"Authorization": f"Bearer {st.session_state.token}"}
                    requests.post(f"{BASE_URL}/jobs/", json={"title": t, "description": d, "requirements": r}, headers=headers)
                    st.success(f"Job '{t}' is now live!")
                    st.balloons()

    # --- RECRUITER: DASHBOARD ---
    elif choice == "Recruiter Dashboard":
        st.title("📊 Talent Acquisition Dashboard")
        try:
            jobs_res = requests.get(f"{BASE_URL}/jobs/")
            jobs = jobs_res.json()
            
            if jobs:
                job_list = {j['title']: j['id'] for j in jobs}
                with st.sidebar.expander("⚠️ Archive / Delete"):
                    job_to_del = st.selectbox("Select Job", list(job_list.keys()), key="del_job", label_visibility="collapsed")
                    if st.button("Delete Permanently", type="primary"):
                        requests.delete(f"{BASE_URL}/jobs/{job_list[job_to_del]}")
                        st.rerun()

                sel_job = st.selectbox("Select a Job to review candidates", list(job_list.keys()))
                j_id = job_list[sel_job]

                st.divider()
                cands = requests.get(f"{BASE_URL}/jobs/{j_id}/shortlist").json()
                
                if not cands:
                    st.info("No candidates have applied yet.")
                else:
                    for c in cands:
                        cid, cname, cstatus, cscore = c.get('id'), c.get('full_name'), c.get('status'), c.get('score', 0)
                        color = "#4CAF50" if cstatus == "Selected" else "#FF4B4B" if cstatus == "Rejected" else "#FFA500"
                        
                        with st.expander(f"👤 {cname} — AI Match Score: {cscore}%"):
                            col_res, col_ai = st.columns([1.6, 1])
                            with col_res:
                                st.markdown("##### 📄 Digital Resume")
                                f_path = c.get('file_path')
                                if f_path:
                                    encoded_path = urllib.parse.quote(f_path)
                                    # Static files served from root, not /api/v1
                                    ROOT_URL = BASE_URL.replace("/api/v1", "")
                                    pdf_url = f"{ROOT_URL}/static/{encoded_path}"
                                    st.markdown(f'<iframe src="{pdf_url}" width="100%" height="600px" style="border-radius:10px; border:1px solid #262730;"></iframe>', unsafe_allow_html=True)
                                else:
                                    st.warning("Original PDF not available.")
                                
                                st.markdown("##### 🔍 AI-Extracted Text")
                                st.text_area("Extracted Content", c.get('resume_text', "No text"), height=150, key=f"t_{cid}", disabled=True, label_visibility="collapsed")

                            with col_ai:
                                st.markdown("##### 🤖 AI Analysis")
                                st.success(f"**Match Summary:** {c.get('resume_summary', 'Pending...')}")
                                st.info(f"**Top Skills:** {c.get('skills', 'N/A')}")
                                
                                st.divider()
                                st.markdown(f"Status: <span style='color:{color}; font-weight:bold;'>{cstatus.upper()}</span>", unsafe_allow_html=True)
                                
                                b1, b2 = st.columns(2)
                                if b1.button("✅ Hire", key=f"h_{cid}", use_container_width=True):
                                    requests.put(f"{BASE_URL}/candidates/{cid}/status", params={"status": "Selected"})
                                    st.rerun()
                                if b2.button("❌ Reject", key=f"r_{cid}", use_container_width=True):
                                    requests.put(f"{BASE_URL}/candidates/{cid}/status", params={"status": "Rejected"})
                                    st.rerun()
            else:
                st.warning("You haven't posted any jobs yet.")
        except Exception as e:
            st.error(f"Dashboard Error: {e}")

    # --- CANDIDATE: PORTAL ---
    elif choice == "Candidate Portal":
        st.title("🚀 Your Career Launchpad")
        t1, t2 = st.tabs(["🎯 Apply for Openings", "📈 Application Tracker"])

        with t1:
            all_jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if all_jobs:
                job_lookup = {j['title']: j for j in all_jobs}
                target_title = st.selectbox("Select your target role", list(job_lookup.keys()))
                
                # SHOW JOB DETAILS TO CANDIDATE
                selected_job = job_lookup[target_title]
                st.markdown(f"""
                <div class="job-card">
                    <h3 style='margin-top:0;'>📋 {selected_job['title']}</h3>
                    <p><b>Description:</b> {selected_job['description']}</p>
                    <p><b>Requirements:</b> <span class='highlight'>{selected_job['requirements']}</span></p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.form("apply_form"):
                    email = st.text_input("Contact Email")
                    pdf = st.file_uploader("Upload Resume (PDF format)", type=["pdf"])
                    if st.form_submit_button("🚀 Submit Application"):
                        if email and pdf:
                            with st.spinner("AI is analyzing your profile..."):
                                files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
                                payload = {"job_id": selected_job['id'], "full_name": st.session_state.username, "email": email}
                                res = requests.post(f"{BASE_URL}/apply/", data=payload, files=files)
                                
                                if res.status_code == 200:
                                    st.success(f"Submitted! AI Match Score: {res.json().get('score')}%")
                                    st.balloons()
                                elif res.status_code == 400:
                                    st.error(res.json().get('detail'))
                                else:
                                    st.error("Submission failed. Please try again.")
            else:
                st.info("No active openings right now.")

        with t2:
            st.markdown("### Tracker")
            m_check = st.text_input("Enter Email for Tracker", placeholder="Enter your registered email...", label_visibility="collapsed")
            if st.button("Check Application Status"):
                res = requests.get(f"{BASE_URL}/my-applications/{m_check}")
                if res.status_code == 200:
                    for a in res.json():
                        st.markdown(f"<div style='padding:15px; border-radius:10px; border:1px solid #262730; margin-bottom:10px;'><h4>Role: {a.get('job_title')}</h4><p>Status: <b>{a.get('status')}</b></p></div>", unsafe_allow_html=True)