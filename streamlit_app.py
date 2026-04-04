import streamlit as st
import requests
import os

# --- 1. SETTINGS & THEME INITIALIZATION ---
st.set_page_config(
    page_title="MindSpark-Ai | Premium Recruitment",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize Theme and Session
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "username": None, "role": None, "token": None})

BASE_URL = st.secrets.get("BASE_URL", "https://hiring-portal-xl3g.onrender.com/api/v1")

# --- 2. DYNAMIC CSS (DARK/WHITE MODES) ---
dark_style = """
    <style>
    .stApp { background: radial-gradient(circle at 20% 30%, #1a1c24 0%, #0e1117 100%); color: white; }
    [data-testid="stSidebar"] { background: rgba(14, 17, 23, 0.95) !important; backdrop-filter: blur(10px); border-right: 1px solid rgba(255,255,255,0.05); }
    .glass-card { background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 16px; padding: 25px; backdrop-filter: blur(15px); box-shadow: 0 8px 32px 0 rgba(0,0,0,0.4); margin-bottom: 20px; }
    .stTabs [data-baseweb="tab-list"] button { background: transparent !important; color: #888 !important; border: none !important; }
    .stTabs [aria-selected="true"] { color: #00b09b !important; border-bottom: 2px solid #00b09b !important; }
    </style>
"""

light_style = """
    <style>
    .stApp { background: radial-gradient(circle at 20% 30%, #f0f2f6 0%, #ffffff 100%); color: #1a1c24; }
    [data-testid="stSidebar"] { background: rgba(255, 255, 255, 0.9) !important; backdrop-filter: blur(10px); border-right: 1px solid #ddd; }
    .glass-card { background: rgba(255, 255, 255, 0.8); border: 1px solid #ddd; border-radius: 16px; padding: 25px; box-shadow: 0 4px 20px rgba(0,0,0,0.05); margin-bottom: 20px; color: #1a1c24; }
    .stTabs [data-baseweb="tab-list"] button { background: transparent !important; color: #666 !important; }
    .stTabs [aria-selected="true"] { color: #00b09b !important; border-bottom: 2px solid #00b09b !important; }
    </style>
"""

# Apply Theme
st.markdown(dark_style if st.session_state.theme == "dark" else light_style, unsafe_allow_html=True)

# Global Button Styles (Emerald & Ruby Gradients)
st.markdown("""
    <style>
    .stButton > button { border-radius: 12px; font-weight: 700; transition: all 0.3s ease; border: none; height: 3rem; text-transform: uppercase; letter-spacing: 1px; }
    /* Primary Emerald */
    div.stButton > button[kind="primary"], .emerald-btn button { background: linear-gradient(135deg, #00b09b, #96c93d) !important; color: white !important; }
    /* Ruby Red for Reject */
    .ruby-btn button { background: linear-gradient(135deg, #ff416c, #ff4b2b) !important; color: white !important; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.2); }
    </style>
""", unsafe_allow_html=True)

# --- 3. AUTHENTICATION UI ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><h1 style='text-align: center;'>🧠 MindSpark-Ai</h1>", unsafe_allow_html=True)
        t_log, t_reg = st.tabs(["🔐 Secure Login", "🚀 Create Account"])
        
        with t_log:
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Access Dashboard", use_container_width=True):
                    res = requests.post(f"{BASE_URL}/login", params={"username": u, "password": p})
                    if res.status_code == 200:
                        d = res.json()
                        st.session_state.update({"logged_in": True, "username": d['username'], "role": d['role'], "token": d['access_token']})
                        st.rerun()
        with t_reg:
            with st.form("reg"):
                nu, np = st.text_input("New Username"), st.text_input("New Password", type="password")
                nr = st.selectbox("I am a...", ["candidate", "recruiter"])
                if st.form_submit_button("Join Network", use_container_width=True):
                    requests.post(f"{BASE_URL}/signup", params={"username": nu, "password": np, "role": nr})
                    st.success("Account Ready!")
    st.stop()

# --- 4. PROTECTED DASHBOARD ---
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        # Theme Toggle
        theme_label = "🌙 Dark Mode" if st.session_state.theme == "dark" else "☀️ White Mode"
        if st.button(theme_label, use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
        
        st.divider()
        menu = ["Post a Job", "Recruiter Dashboard"] if st.session_state.role == "recruiter" else ["Candidate Portal"]
        choice = st.sidebar.radio("Navigate", menu)
        
        if st.sidebar.button("🚪 Sign Out", use_container_width=True):
            st.session_state.update({"logged_in": False, "username": None, "role": None, "token": None})
            st.rerun()

    # --- RECRUITER DASHBOARD ---
    if choice == "Recruiter Dashboard":
        st.title("📊 Talent Intelligence")
        jobs = requests.get(f"{BASE_URL}/jobs/").json()
        if jobs:
            job_list = {j['title']: j['id'] for j in jobs}
            c1, c2 = st.columns([3, 1])
            with c1:
                sel_job = st.selectbox("Select Active Vacancy", list(job_list.keys()))
            with c2:
                st.write("") 
                if st.button("🗑️ Delete", type="secondary", use_container_width=True):
                    requests.delete(f"{BASE_URL}/jobs/{job_list[sel_job]}")
                    st.rerun()

            cands = requests.get(f"{BASE_URL}/jobs/{job_list[sel_job]}/shortlist").json()
            for c in cands:
                with st.expander(f"👤 {c['full_name']} — Match: {c['score']}%"):
                    col_res, col_ai = st.columns([1.6, 1])
                    with col_res:
                        res_url = c.get('file_path')
                        pdf_display = f'https://docs.google.com/gview?url={res_url}&embedded=true'
                        st.markdown(f'<iframe src="{pdf_display}" width="100%" height="750px" style="border-radius:12px; border:none;"></iframe>', unsafe_allow_html=True)
                    with col_ai:
                        st.markdown(f"<div class='glass-card' style='border-left: 5px solid #00b09b;'><b>AI Analysis:</b><br>{c.get('resume_summary')}</div>", unsafe_allow_html=True)
                        st.divider()
                        b_h, b_p = st.columns(2)
                        with b_h:
                            st.markdown('<div class="emerald-btn">', unsafe_allow_html=True)
                            if st.button("✅ HIRE", key=f"h_{c['id']}", use_container_width=True):
                                requests.put(f"{BASE_URL}/candidates/{c['id']}/status", params={"status": "Selected"})
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)
                        with b_p:
                            st.markdown('<div class="ruby-btn">', unsafe_allow_html=True)
                            if st.button("❌ PASS", key=f"r_{c['id']}", use_container_width=True):
                                requests.put(f"{BASE_URL}/candidates/{c['id']}/status", params={"status": "Rejected"})
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

    # --- CANDIDATE PORTAL ---
    elif choice == "Candidate Portal":
        st.title("🚀 Career Center")
        t1, t2 = st.tabs(["🎯 Apply", "📈 Status"])
        with t1:
            all_jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if all_jobs:
                job_map = {j['title']: j for j in all_jobs}
                title = st.selectbox("Choose Role", list(job_map.keys()))
                job = job_map[title]
                st.markdown(f"<div class='glass-card'><h3>{job['title']}</h3><p>{job['description']}</p></div>", unsafe_allow_html=True)
                with st.form("apply"):
                    email = st.text_input("Contact Email")
                    pdf = st.file_uploader("Upload PDF", type=["pdf"])
                    if st.form_submit_button("🚀 Submit Application", use_container_width=True):
                        files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
                        requests.post(f"{BASE_URL}/apply/", data={"job_id": job['id'], "full_name": st.session_state.username, "email": email}, files=files)
                        st.success("Deployed to AI Engine!")
                        st.balloons()
        with t2:
            st.markdown("### Tracker")
            email_track = st.text_input("Registered Email")
            if st.button("Search History", use_container_width=True):
                apps = requests.get(f"{BASE_URL}/my-applications/{email_track}").json()
                for a in apps:
                    color = "#00b09b" if a['status'] == "Selected" else "#ff416c" if a['status'] == "Rejected" else "#FFA500"
                    st.markdown(f"<div class='glass-card' style='border-left:5px solid {color};'><h4>{a['job_title']}</h4><p>Status: <b>{a['status']}</b></p></div>", unsafe_allow_html=True)

    # --- POST A JOB ---
    elif choice == "Post a Job":
        st.title("📝 Broadcast Opportunity")
        with st.form("job_form", clear_on_submit=True):
            t, d, r = st.text_input("Title"), st.text_area("Description"), st.text_input("Requirements")
            if st.form_submit_button("🚀 Post Now", use_container_width=True):
                requests.post(f"{BASE_URL}/jobs/", json={"title": t, "description": d, "requirements": r}, headers={"Authorization": f"Bearer {st.session_state.token}"})
                st.success("Live on Dashboard!")