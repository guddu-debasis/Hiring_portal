import streamlit as st
import requests
import os

# --- 1. SETTINGS & THEME INITIALIZATION ---
st.set_page_config(
    page_title="NeuralNexus | Intelligence Engine",
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
    border_color = "rgba(255, 255, 255, 0.1)"
    pdf_bg = "#1e1e1e"
else:
    bg_style = "#F8FAFC"
    card_bg = "#FFFFFF"
    sidebar_bg = "#FFFFFF"
    text_color = "#1E293B"
    border_color = "#CBD5E1"
    pdf_bg = "#E2E8F0"

st.markdown(f"""
    <style>
    .stApp {{ background: {bg_style}; color: {text_color} !important; }}
    
    /* Global Text Force */
    h1, h2, h3, h4, p, span, label, .stMarkdown {{ color: {text_color} !important; }}

    /* Sidebar Glassmorphism */
    [data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        border-right: 1px solid {border_color};
    }}
    
    /* Stunning Cards */
    .glass-card {{
        background: {card_bg};
        border: 1px solid {border_color};
        border-radius: 20px;
        padding: 25px;
        backdrop-filter: blur(15px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.05);
        margin-bottom: 20px;
    }}

    /* PDF Container Fix */
    .pdf-container {{
        background-color: {pdf_bg};
        padding: 10px;
        border-radius: 15px;
        border: 2px solid {border_color};
    }}

    /* Buttons */
    .stButton > button {{
        border-radius: 12px;
        font-weight: 700;
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white !important;
        border: none;
        height: 3.2rem;
        transition: all 0.3s ease;
    }}
    .stButton > button:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,176,155,0.3); }}

    .ruby-btn button {{ background: linear-gradient(135deg, #ff416c, #ff4b2b) !important; }}
    </style>
""", unsafe_allow_html=True)

# --- 3. AUTHENTICATION ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.4, 1])
    with col2:
        st.markdown("<br><br><h1 style='text-align: center;'>🧠 NeuralNexus</h1>", unsafe_allow_html=True)
        t1, t2 = st.tabs(["🔐 Login", "🚀 Register"])
        
        with t1:
            with st.form("login"):
                u = st.text_input("Username")
                p = st.text_input("Password", type="password")
                if st.form_submit_button("Launch Dashboard", use_container_width=True):
                    res = requests.post(f"{BASE_URL}/login", params={"username": u, "password": p})
                    if res.status_code == 200:
                        d = res.json()
                        st.session_state.update({
                            "logged_in": True, 
                            "username": d['username'], 
                            "role": d['role'], 
                            "token": d['access_token']
                        })
                        st.rerun()
                    else: st.error("Access Denied")
        
        with t2:
            with st.form("register"):
                nu = st.text_input("Choose Username")
                np = st.text_input("Set Password", type="password")
                nr = st.selectbox("I am a...", ["candidate", "recruiter"])
                if st.form_submit_button("Create Account", use_container_width=True):
                    res = requests.post(f"{BASE_URL}/signup", params={"username": nu, "password": np, "role": nr})
                    if res.status_code == 200:
                        st.success("Account Created! You can now log in.")
                    else:
                        st.error("Username already exists or invalid data.")
    st.stop()

# --- 4. DASHBOARD ---
else:
    with st.sidebar:
        st.markdown(f"### 👤 {st.session_state.username}")
        if st.button("🌙 Dark Mode" if st.session_state.theme == "light" else "☀️ White Mode", use_container_width=True):
            st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
            st.rerun()
        
        st.divider()
        menu = ["Post a Job", "Recruiter Dashboard"] if st.session_state.role == "recruiter" else ["Candidate Portal"]
        choice = st.sidebar.radio("Navigation", menu)
        if st.sidebar.button("🚪 Sign Out", use_container_width=True):
            st.session_state.update({"logged_in": False, "username": None, "role": None, "token": None})
            st.rerun()

    # --- RECRUITER DASHBOARD ---
    if choice == "Recruiter Dashboard":
        st.title("📊 Intelligence Center")
        jobs = requests.get(f"{BASE_URL}/jobs/").json()
        if jobs:
            job_list = {j['title']: j['id'] for j in jobs}
            c1, c2 = st.columns([3, 1])
            with c1: sel_job = st.selectbox("Vacancy", list(job_list.keys()))
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
                        st.markdown("##### 📄 Candidate Resume")
                        res_url = c.get('file_path')
                        pdf_display = f'https://docs.google.com/gview?url={res_url}&embedded=true'
                        st.markdown(f"""
                            <div class="pdf-container">
                                <iframe src="{pdf_display}" width="100%" height="750px" style="border:none;"></iframe>
                            </div>
                        """, unsafe_allow_html=True)
                        st.link_button("📂 Open PDF in New Tab", res_url)

                    with col_ai:
                        st.markdown(f"<div class='glass-card' style='border-left: 5px solid #00b09b;'><b>AI Summary:</b><br>{c.get('resume_summary')}</div>", unsafe_allow_html=True)
                        st.info(f"**Skills:** {c.get('skills')}")
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
        st.title("🚀 Career Launchpad")
        t1, t2 = st.tabs(["🎯 Available Roles", "📈 My Applications"])
        with t1:
            all_jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if all_jobs:
                job_map = {j['title']: j for j in all_jobs}
                title = st.selectbox("Select Mission", list(job_map.keys()))
                job = job_map[title]
                st.markdown(f"<div class='glass-card'><h3>{job['title']}</h3><p>{job['description']}</p></div>", unsafe_allow_html=True)
                with st.form("apply"):
                    email = st.text_input("Your Email")
                    pdf = st.file_uploader("Resume (PDF)", type=["pdf"])
                    if st.form_submit_button("🚀 Submit"):
                        if email and pdf:
                            files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
                            requests.post(f"{BASE_URL}/apply/", data={"job_id": job['id'], "full_name": st.session_state.username, "email": email}, files=files)
                            st.success("Deployed!")
        with t2:
            email_track = st.text_input("Registered Email")
            if st.button("Track Status", use_container_width=True):
                apps = requests.get(f"{BASE_URL}/my-applications/{email_track}").json()
                if not apps: st.info("No records found.")
                for a in apps:
                    color = "#00b09b" if a['status'] == "Selected" else "#ff416c" if a['status'] == "Rejected" else "#FFA500"
                    st.markdown(f"<div class='glass-card' style='border-left:5px solid {color};'><h4>{a['job_title']}</h4><p>Status: <b>{a['status']}</b></p></div>", unsafe_allow_html=True)

    # --- POST A JOB ---
    elif choice == "Post a Job":
        st.title("📝 Broadcast Vacancy")
        with st.form("job_form", clear_on_submit=True):
            t, d, r = st.text_input("Title"), st.text_area("Description"), st.text_input("Skills")
            if st.form_submit_button("🚀 Post Now", use_container_width=True):
                requests.post(f"{BASE_URL}/jobs/", json={"title": t, "description": d, "requirements": r}, headers={"Authorization": f"Bearer {st.session_state.token}"})
                st.toast("Opportunity Live!", icon="✅")