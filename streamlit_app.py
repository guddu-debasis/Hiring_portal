import streamlit as st
import requests
import os

# --- 1. SETTINGS & THEME INITIALIZATION ---
st.set_page_config(
    page_title="MindSpark-Ai | Intelligence Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "username": None, "role": None, "token": None})

BASE_URL = st.secrets.get("BASE_URL", "https://hiring-portal-xl3g.onrender.com/api/v1")

# --- 2. DYNAMIC STUNNING CSS ---
if st.session_state.theme == "dark":
    bg_style = "linear-gradient(-45deg, #0e1117, #1a1c24, #0e1117, #161b22)"
    card_bg = "rgba(255, 255, 255, 0.03)"
    sidebar_bg = "rgba(10, 12, 18, 0.8)"
    text_color = "#E0E0E0"
    border_glow = "rgba(0, 176, 155, 0.3)"
else:
    bg_style = "linear-gradient(-45deg, #f8fafc, #ffffff, #f1f5f9, #ffffff)"
    card_bg = "rgba(255, 255, 255, 0.8)"
    sidebar_bg = "rgba(255, 255, 255, 0.7)"
    text_color = "#1e293b"
    border_glow = "rgba(0, 0, 0, 0.05)"

st.markdown(f"""
    <style>
    /* Animated Background */
    @keyframes gradient {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    .stApp {{
        background: {bg_style};
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: {text_color};
    }}
    
    /* Floating Glass Sidebar */
    [data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        backdrop-filter: blur(25px) saturate(150%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }}
    
    /* Stunning Neon Glass Cards */
    .glass-card {{
        background: {card_bg};
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 24px;
        padding: 30px;
        backdrop-filter: blur(20px);
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .glass-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 15px 50px {border_glow};
    }}

    /* Premium Button Polish */
    .stButton > button {{
        border-radius: 16px;
        font-weight: 800;
        height: 3.5rem;
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
        border: none;
        box-shadow: 0 8px 20px rgba(0, 176, 155, 0.3);
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }}
    .stButton > button:hover {{
        transform: scale(1.03);
        box-shadow: 0 12px 30px rgba(0, 176, 155, 0.5);
    }}

    /* Reject Button - Ruby Glow */
    .ruby-btn button {{
        background: linear-gradient(135deg, #ff416c, #ff4b2b) !important;
        box-shadow: 0 8px 20px rgba(255, 75, 43, 0.3) !important;
    }}

    /* Animated Header */
    .header-text {{
        font-size: 3.2rem;
        font-weight: 900;
        background: linear-gradient(to right, #00b09b, #96c93d, #56ab2f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -1px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. AUTHENTICATION (The Eye-Catching Entrance) ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 class='header-text' style='text-align: center;'>🧠 MindSpark-Ai</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; opacity: 0.7;'>Next-Gen Intelligent Recruitment Platform</p>", unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["🔐 Secure Login", "🚀 Create Identity"])
        
        with tab_login:
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Enter Dashboard", use_container_width=True):
                    res = requests.post(f"{BASE_URL}/login", params={"username": u, "password": p})
                    if res.status_code == 200:
                        d = res.json()
                        st.session_state.update({"logged_in": True, "username": d['username'], "role": d['role'], "token": d['access_token']})
                        st.rerun()
                    else: st.error("Access Denied")
    st.stop()

# --- 4. DASHBOARD ---
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        # Stunning Theme Toggle
        theme_icon = "☀️" if st.session_state.theme == "dark" else "🌙"
        if st.button(f"{theme_icon} Switch Theme", use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
        
        st.divider()
        menu = ["Post a Job", "Recruiter Dashboard"] if st.session_state.role == "recruiter" else ["Candidate Portal"]
        choice = st.sidebar.radio("Navigation", menu)
        
        if st.sidebar.button("🚪 Sign Out", use_container_width=True):
            st.session_state.update({"logged_in": False, "username": None, "role": None, "token": None})
            st.rerun()

    # --- RECRUITER DASHBOARD (The "Wow" View) ---
    if choice == "Recruiter Dashboard":
        st.markdown("<h1 class='header-text'>📊 Talent Intelligence</h1>", unsafe_allow_html=True)
        jobs = requests.get(f"{BASE_URL}/jobs/").json()
        if jobs:
            job_list = {j['title']: j['id'] for j in jobs}
            c1, c2 = st.columns([3, 1])
            with c1:
                sel_job = st.selectbox("Select Active Vacancy", list(job_list.keys()))
            with c2:
                st.write("") 
                if st.button("🗑️ Archive Job", type="secondary", use_container_width=True):
                    requests.delete(f"{BASE_URL}/jobs/{job_list[sel_job]}")
                    st.rerun()

            cands = requests.get(f"{BASE_URL}/jobs/{job_list[sel_job]}/shortlist").json()
            for c in cands:
                with st.expander(f"👤 {c['full_name']} — Match Score: {c['score']}%"):
                    col_res, col_ai = st.columns([1.6, 1])
                    with col_res:
                        # Stunning PDF Frame
                        pdf_url = f"https://docs.google.com/gview?url={c.get('file_path')}&embedded=true"
                        st.markdown(f'<iframe src="{pdf_url}" width="100%" height="800px" style="border-radius:20px; border:1px solid rgba(255,255,255,0.1); box-shadow: 0 10px 30px rgba(0,0,0,0.5);"></iframe>', unsafe_allow_html=True)
                    with col_ai:
                        st.markdown(f"<div class='glass-card' style='border-left: 6px solid #00b09b;'><b>AI Extraction Insights:</b><br>{c.get('resume_summary')}</div>", unsafe_allow_html=True)
                        st.divider()
                        bh, bp = st.columns(2)
                        with bh:
                            if st.button("✅ HIRE", key=f"h_{c['id']}", use_container_width=True):
                                requests.put(f"{BASE_URL}/candidates/{c['id']}/status", params={"status": "Selected"})
                                st.rerun()
                        with bp:
                            st.markdown('<div class="ruby-btn">', unsafe_allow_html=True)
                            if st.button("❌ PASS", key=f"r_{c['id']}", use_container_width=True):
                                requests.put(f"{BASE_URL}/candidates/{c['id']}/status", params={"status": "Rejected"})
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

    # --- POST A JOB ---
    elif choice == "Post a Job":
        st.markdown("<h1 class='header-text'>📝 Broadcast Vacancy</h1>", unsafe_allow_html=True)
        with st.form("job_form"):
            t = st.text_input("Job Title")
            d = st.text_area("Job Mission", height=200)
            r = st.text_input("Core Requirements")
            if st.form_submit_button("🚀 Deploy to Market", use_container_width=True):
                requests.post(f"{BASE_URL}/jobs/", json={"title": t, "description": d, "requirements": r}, headers={"Authorization": f"Bearer {st.session_state.token}"})
                st.toast("Opportunity is Live!", icon="⚡")

    # --- CANDIDATE PORTAL ---
    elif choice == "Candidate Portal":
        st.markdown("<h1 class='header-text'>🚀 Career Launchpad</h1>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["🎯 Explore Missions", "📈 Status Tracker"])
        with t1:
            all_jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if all_jobs:
                job_map = {j['title']: j for j in all_jobs}
                title = st.selectbox("Choose Mission", list(job_map.keys()))
                job = job_map[title]
                st.markdown(f"<div class='glass-card'><h3>{job['title']}</h3><p>{job['description']}</p></div>", unsafe_allow_html=True)
                with st.form("apply"):
                    email = st.text_input("Contact Email")
                    pdf = st.file_uploader("Upload PDF Resume", type=["pdf"])
                    if st.form_submit_button("Initiate Application", use_container_width=True):
                        files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
                        requests.post(f"{BASE_URL}/apply/", data={"job_id": job['id'], "full_name": st.session_state.username, "email": email}, files=files)
                        st.balloons()