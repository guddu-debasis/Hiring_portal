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

# --- 2. DYNAMIC PREMIUM CSS ---
if st.session_state.theme == "dark":
    # DEEP NIGHT THEME
    bg_color = "radial-gradient(circle at 20% 30%, #1a1c24 0%, #0e1117 100%)"
    card_bg = "rgba(255, 255, 255, 0.04)"
    sidebar_bg = "rgba(14, 17, 23, 0.95)"
    text_color = "#FFFFFF"
    border_color = "rgba(255, 255, 255, 0.1)"
    input_bg = "#1e2128"
else:
    # CLOUD WHITE THEME
    bg_color = "#f8fafc"
    card_bg = "#ffffff"
    sidebar_bg = "#ffffff"
    text_color = "#1e293b"
    border_color = "#e2e8f0"
    input_bg = "#f1f5f9"

st.markdown(f"""
    <style>
    /* Global Background */
    .stApp {{ background: {bg_color}; color: {text_color}; }}
    
    /* Sidebar Overhaul */
    [data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        border-right: 1px solid {border_color};
        padding: 2rem 1rem;
    }}
    
    /* Stunning Glass Cards */
    .glass-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 20px;
        padding: 30px;
        backdrop-filter: blur(20px);
        box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        margin-bottom: 25px;
    }}

    /* Input Field Styling */
    div[data-baseweb="input"], div[data-baseweb="textarea"] {{
        background-color: {input_bg} !important;
        border-radius: 12px !important;
        border: 1px solid {border_color} !important;
    }}

    /* Professional Buttons */
    .stButton > button {{
        border-radius: 12px;
        font-weight: 700;
        height: 3.2rem;
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
        border: none;
        box-shadow: 0 4px 15px rgba(0, 176, 155, 0.2);
        transition: all 0.3s ease;
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 176, 155, 0.4);
    }}

    /* Reject Button */
    .ruby-btn button {{
        background: linear-gradient(135deg, #ff416c, #ff4b2b) !important;
        box-shadow: 0 4px 15px rgba(255, 75, 43, 0.2) !important;
    }}

    /* Custom Header */
    .header-text {{
        font-size: 2.5rem;
        font-weight: 800;
        background: -webkit-linear-gradient(#00b09b, #96c93d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }}
    </style>
""", unsafe_allow_html=True)

# --- 3. AUTHENTICATION ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 class='header-text' style='text-align: center;'>🧠 MindSpark-Ai</h1>", unsafe_allow_html=True)
        t_log, t_reg = st.tabs(["🔐 Login", "🚀 Join"])
        
        with t_log:
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Access Portal", use_container_width=True):
                    res = requests.post(f"{BASE_URL}/login", params={"username": u, "password": p})
                    if res.status_code == 200:
                        d = res.json()
                        st.session_state.update({"logged_in": True, "username": d['username'], "role": d['role'], "token": d['access_token']})
                        st.rerun()
                    else: st.error("Access Denied")
        with t_reg:
            with st.form("reg"):
                nu, np = st.text_input("New Username"), st.text_input("New Password", type="password")
                nr = st.selectbox("Role", ["candidate", "recruiter"])
                if st.form_submit_button("Register Account", use_container_width=True):
                    requests.post(f"{BASE_URL}/signup", params={"username": nu, "password": np, "role": nr})
                    st.success("Welcome aboard!")
    st.stop()

# --- 4. DASHBOARD ---
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        # Dynamic Theme Toggle
        if st.button("🌙 Dark Mode" if st.session_state.theme == "light" else "☀️ White Mode", use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
        
        st.divider()
        menu = ["Post a Job", "Recruiter Dashboard"] if st.session_state.role == "recruiter" else ["Candidate Portal"]
        choice = st.sidebar.radio("Navigate", menu)
        
        if st.sidebar.button("🚪 Sign Out", use_container_width=True):
            st.session_state.update({"logged_in": False, "username": None, "role": None, "token": None})
            st.rerun()

    # --- POST A JOB ---
    if choice == "Post a Job":
        st.markdown("<h1 class='header-text'>📝 Broadcast Opportunity</h1>", unsafe_allow_html=True)
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("job_form", clear_on_submit=True):
            t = st.text_input("Job Title", placeholder="e.g. Senior Software Architect")
            d = st.text_area("Detailed Mission Description", height=200)
            r = st.text_input("Requirements", placeholder="Python, FastAPI, AWS...")
            if st.form_submit_button("🚀 Deploy to Market", use_container_width=True):
                requests.post(f"{BASE_URL}/jobs/", json={"title": t, "description": d, "requirements": r}, headers={"Authorization": f"Bearer {st.session_state.token}"})
                st.toast("Opportunity is Live!", icon="✅")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- RECRUITER DASHBOARD ---
    elif choice == "Recruiter Dashboard":
        st.markdown("<h1 class='header-text'>📊 Intelligence Center</h1>", unsafe_allow_html=True)
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
                with st.expander(f"👤 {c['full_name']} — Match Score: {c['score']}%"):
                    col_res, col_ai = st.columns([1.6, 1])
                    with col_res:
                        pdf_url = f"https://docs.google.com/gview?url={c.get('file_path')}&embedded=true"
                        st.markdown(f'<iframe src="{pdf_url}" width="100%" height="800px" style="border-radius:15px; border:none;"></iframe>', unsafe_allow_html=True)
                    with col_ai:
                        st.markdown(f"<div class='glass-card' style='border-left: 5px solid #00b09b;'><b>AI Insights:</b><br>{c.get('resume_summary')}</div>", unsafe_allow_html=True)
                        st.divider()
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
        st.markdown("<h1 class='header-text'>🚀 Career Launchpad</h1>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["🎯 Explore", "📈 Tracking"])
        with t1:
            all_jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if all_jobs:
                job_map = {j['title']: j for j in all_jobs}
                title = st.selectbox("Choose Mission", list(job_map.keys()))
                job = job_map[title]
                st.markdown(f"<div class='glass-card'><h3>{job['title']}</h3><p>{job['description']}</p></div>", unsafe_allow_html=True)
                with st.form("apply"):
                    email = st.text_input("Your Email")
                    pdf = st.file_uploader("Upload PDF Resume", type=["pdf"])
                    if st.form_submit_button("Initiate Application", use_container_width=True):
                        files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
                        requests.post(f"{BASE_URL}/apply/", data={"job_id": job['id'], "full_name": st.session_state.username, "email": email}, files=files)
                        st.balloons()