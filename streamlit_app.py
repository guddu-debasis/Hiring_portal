import streamlit as st
import requests
import os

# --- 1. SETTINGS & THEME INITIALIZATION ---
st.set_page_config(
    page_title="MindSpark-Ai | Global Talent Engine",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "logged_in" not in st.session_state:
    st.session_state.update({"logged_in": False, "username": None, "role": None, "token": None})

BASE_URL = st.secrets.get("BASE_URL", "https://hiring-portal-xl3g.onrender.com/api/v1")

# --- 2. DYNAMIC HIGH-CONTRAST CSS ---
if st.session_state.theme == "dark":
    bg_style = "linear-gradient(-45deg, #0e1117, #1a1c24, #0e1117, #161b22)"
    card_bg = "rgba(255, 255, 255, 0.04)"
    sidebar_bg = "rgba(10, 12, 18, 0.95)"
    text_color = "#FFFFFF"
    sub_text = "#AAAAAA"
    border_color = "rgba(255, 255, 255, 0.1)"
    input_text = "#FFFFFF"
else:
    bg_style = "#F0F2F6"
    card_bg = "#FFFFFF"
    sidebar_bg = "#FFFFFF"
    text_color = "#1E293B"
    sub_text = "#475569"
    border_color = "#CBD5E1"
    input_text = "#1E293B"

st.markdown(f"""
    <style>
    /* Global Background & Text */
    .stApp {{
        background: {bg_style};
        color: {text_color} !important;
    }}
    
    /* Force Text Colors for White Mode */
    h1, h2, h3, h4, h5, p, span, label {{
        color: {text_color} !important;
    }}

    /* Fix Input Fields for White Mode */
    div[data-baseweb="input"] input, div[data-baseweb="textarea"] textarea {{
        color: {input_text} !important;
        background-color: transparent !important;
    }}

    /* Floating Glass Sidebar */
    [data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        border-right: 1px solid {border_color};
    }}
    
    /* Stunning Glass Cards */
    .glass-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 20px;
        padding: 25px;
        backdrop-filter: blur(15px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        color: {text_color} !important;
    }}

    /* Buttons */
    .stButton > button {{
        border-radius: 12px;
        font-weight: 700;
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white !important;
        border: none;
        height: 3.2rem;
    }}
    
    .ruby-btn button {{
        background: linear-gradient(135deg, #ff416c, #ff4b2b) !important;
    }}

    /* Remove Red Box on Tabs */
    .stTabs [data-baseweb="tab-list"] button {{
        background: transparent !important;
        border: none !important;
        color: {sub_text} !important;
    }}
    .stTabs [aria-selected="true"] {{
        border-bottom: 3px solid #00b09b !important;
        color: #00b09b !important;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. AUTHENTICATION ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("<br><br><h1 style='text-align: center;'>🧠 MindSpark-Ai</h1>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["🔐 Login", "🚀 Register"])
        with t1:
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Access Dashboard", use_container_width=True):
                    res = requests.post(f"{BASE_URL}/login", params={"username": u, "password": p})
                    if res.status_code == 200:
                        d = res.json()
                        st.session_state.update({"logged_in": True, "username": d['username'], "role": d['role'], "token": d['access_token']})
                        st.rerun()
                    else: st.error("Access Denied")
        with t2:
            with st.form("reg"):
                nu, np = st.text_input("New Username"), st.text_input("New Password", type="password")
                nr = st.selectbox("Role", ["candidate", "recruiter"])
                if st.form_submit_button("Join Network", use_container_width=True):
                    requests.post(f"{BASE_URL}/signup", params={"username": nu, "password": np, "role": nr})
                    st.success("Registered! Switch to Login.")
    st.stop()

# --- 4. DASHBOARD ---
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        # Theme Toggle
        if st.button("🌙 Dark Mode" if st.session_state.theme == "light" else "☀️ White Mode", use_container_width=True):
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
                sel_job = st.selectbox("Select Vacancy", list(job_list.keys()))
            with c2:
                st.write("") 
                if st.button("🗑️ Delete", type="secondary", use_container_width=True):
                    requests.delete(f"{BASE_URL}/jobs/{job_list[sel_job]}")
                    st.rerun()

            cands = requests.get(f"{BASE_URL}/jobs/{job_list[sel_job]}/shortlist").json()
            for c in cands:
                with st.expander(f"👤 {c['full_name']} — Match Score: {c['score']}%"):
                    col_res, col_ai = st.columns([1.6, 1])
                    with col_res:
                        # Professional PDF Frame
                        pdf_url = f"https://docs.google.com/gview?url={c.get('file_path')}&embedded=true"
                        st.markdown(f'<iframe src="{pdf_url}" width="100%" height="750px" style="border-radius:15px; border:none;"></iframe>', unsafe_allow_html=True)
                    with col_ai:
                        st.markdown(f"<div class='glass-card' style='border-left: 5px solid #00b09b;'><b>AI Insights:</b><br>{c.get('resume_summary')}</div>", unsafe_allow_html=True)
                        b_h, b_p = st.columns(2)
                        with b_h:
                            if st.button("✅ HIRE", key=f"h_{c['id']}", use_container_width=True):
                                requests.put(f"{BASE_URL}/candidates/{c['id']}/status", params={"status": "Selected"})
                                st.rerun()
                        with b_p:
                            st.markdown('<div class="ruby-btn">', unsafe_allow_html=True)
                            if st.button("❌ PASS", key=f"r_{c['id']}", use_container_width=True):
                                requests.put(f"{BASE_URL}/candidates/{c['id']}/status", params={"status": "Rejected"})
                                st.rerun()
                            st.markdown('</div>', unsafe_allow_html=True)

    # --- CANDIDATE PORTAL ---
    elif choice == "Candidate Portal":
        st.title("🚀 Career Center")
        t1, t2 = st.tabs(["🎯 Explore", "📈 Tracking"])
        with t1:
            all_jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if all_jobs:
                job_map = {j['title']: j for j in all_jobs}
                title = st.selectbox("Choose Mission", list(job_map.keys()))
                job = job_map[title]
                st.markdown(f"<div class='glass-card'><h3>{job['title']}</h3><p>{job['description']}</p></div>", unsafe_allow_html=True)
                with st.form("apply"):
                    email = st.text_input("Your Registered Email")
                    pdf = st.file_uploader("Upload PDF Resume", type=["pdf"])
                    if st.form_submit_button("Initiate Application", use_container_width=True):
                        if email and pdf:
                            files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
                            requests.post(f"{BASE_URL}/apply/", data={"job_id": job['id'], "full_name": st.session_state.username, "email": email}, files=files)
                            st.success("Successfully Applied!")
                            st.balloons()
        with t2:
            st.markdown("### 📈 Application History")
            email_track = st.text_input("Enter the Email you used to apply", placeholder="example@gmail.com")
            if st.button("Refresh Status", use_container_width=True):
                # FIXED STATUS TRACKER LOGIC
                res = requests.get(f"{BASE_URL}/my-applications/{email_track}")
                if res.status_code == 200:
                    apps = res.json()
                    if not apps:
                        st.info("No applications found for this email address.")
                    for a in apps:
                        current_status = a.get('status', 'Pending')
                        status_color = "#00b09b" if current_status == "Selected" else "#ff416c" if current_status == "Rejected" else "#FFA500"
                        st.markdown(f"""
                        <div class='glass-card' style='border-left: 6px solid {status_color};'>
                            <h4 style='margin:0;'>{a.get('job_title', 'Application')}</h4>
                            <p style='color:{status_color}; font-weight:bold; margin:5px 0;'>Status: {current_status.upper()}</p>
                        </div>
                        """, unsafe_allow_html=True)

    # --- POST A JOB ---
    elif choice == "Post a Job":
        st.title("📝 Broadcast Opportunity")
        with st.form("job_form", clear_on_submit=True):
            t, d, r = st.text_input("Title"), st.text_area("Description"), st.text_input("Requirements")
            if st.form_submit_button("🚀 Post Now", use_container_width=True):
                requests.post(f"{BASE_URL}/jobs/", json={"title": t, "description": d, "requirements": r}, headers={"Authorization": f"Bearer {st.session_state.token}"})
                st.toast("Opportunity Live!", icon="✅")