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

# Modern Glassmorphism & UI Enhancements
st.markdown("""
    <style>
    /* Global Background */
    .stApp { 
        background: radial-gradient(circle at 20% 30%, #1a1c24 0%, #0e1117 100%); 
    }
    
    /* Stunning Glass Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        margin-bottom: 25px;
    }

    /* Buttons: Emerald Green for Primary */
    div.stButton > button {
        border-radius: 12px;
        padding: 12px 20px;
        background: linear-gradient(135deg, #00b09b, #96c93d);
        color: white;
        border: none;
        font-weight: 700;
        letter-spacing: 0.5px;
        transition: all 0.3s ease;
        width: 100%;
        text-transform: uppercase;
    }
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 176, 155, 0.4);
    }

    /* Red "Pass" Button */
    .reject-btn button {
        background: linear-gradient(135deg, #ff416c, #ff4b2b) !important;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0e1117;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    .role-badge {
        background: rgba(0, 176, 155, 0.1);
        padding: 6px 15px;
        border-radius: 30px;
        border: 1px solid #00b09b;
        font-size: 0.75rem;
        color: #00b09b;
        font-weight: bold;
    }
    
    h1, h2, h3 { color: #ffffff !important; }
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
BASE_URL = st.secrets.get("BASE_URL", "https://hiring-portal-xl3g.onrender.com/api/v1")

# --- 3. AUTHENTICATION UI ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><h1 style='text-align: center;'>🧠 MindSpark-Ai</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>Intelligence-Driven Talent Acquisition</p>", unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["🔐 Secure Access", "🚀 New Account"])

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
                                "logged_in": True, "username": data.get('username'),
                                "role": data.get('role'), "token": data.get('access_token')
                            })
                            st.rerun()
                        else:
                            st.error("Access Denied: Invalid Credentials")
                    except:
                        st.error("Backend Services Offline.")

        with tab_signup:
            with st.form("signup_form"):
                nu = st.text_input("New Username")
                np = st.text_input("New Password", type="password")
                nr = st.selectbox("Role", ["candidate", "recruiter"])
                if st.form_submit_button("Join Network"):
                    requests.post(f"{BASE_URL}/signup", params={"username": nu, "password": np, "role": nr})
                    st.success("Account Created. Welcome to the future.")
    st.stop()

# --- 4. PROTECTED CONTENT ---
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
        st.title("📊 Intelligence Command Center")
        try:
            jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if jobs:
                job_list = {j['title']: j['id'] for j in jobs}
                
                # Selection & Management
                col_sel, col_del = st.columns([3, 1])
                with col_sel:
                    sel_job = st.selectbox("Current Active Mission", list(job_list.keys()))
                with col_del:
                    st.write("") # Spacer
                    st.write("") # Spacer
                    if st.button("🗑️ Delete Job", type="secondary"):
                        requests.delete(f"{BASE_URL}/jobs/{job_list[sel_job]}")
                        st.rerun()

                st.divider()
                cands = requests.get(f"{BASE_URL}/jobs/{job_list[sel_job]}/shortlist").json()
                
                if not cands:
                    st.info("Searching for talent... No applicants yet.")
                else:
                    for c in cands:
                        match_color = "#00b09b" if c['score'] > 70 else "#FFA500" if c['score'] > 40 else "#FF4B2B"
                        
                        with st.expander(f"👤 {c['full_name']} — Match Score: {c['score']}%"):
                            col_res, col_ai = st.columns([1.6, 1])
                            
                            with col_res:
                                st.markdown("##### 📄 Candidate Portfolio")
                                res_url = c.get('file_path')
                                if res_url and res_url.startswith("http"):
                                    # STUNNING FIX: Embedded PDF Viewer using Google Docs wrapper
                                    pdf_display = f'https://docs.google.com/gview?url={res_url}&embedded=true'
                                    st.markdown(f'<iframe src="{pdf_display}" width="100%" height="750px" style="border-radius:15px; border:none;"></iframe>', unsafe_allow_html=True)
                                else:
                                    st.error("Cloud Storage Link Broken.")

                            with col_ai:
                                st.markdown("##### 🤖 AI Engine Analysis")
                                st.markdown(f"""
                                <div class="glass-card" style="border-left: 5px solid {match_color};">
                                    <p style="font-size: 0.9rem; color: #ccc;"><b>AI Summary:</b></p>
                                    <p>{c.get('resume_summary')}</p>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                st.info(f"**Identified Skills:** {c.get('skills')}")
                                
                                # ACTION BUTTONS
                                st.divider()
                                b_col1, b_col2 = st.columns(2)
                                with b_col1:
                                    if st.button(f"✅ Hire", key=f"h_{c['id']}"):
                                        requests.put(f"{BASE_URL}/candidates/{c['id']}/status", params={"status": "Selected"})
                                        st.rerun()
                                with b_col2:
                                    st.markdown('<div class="reject-btn">', unsafe_allow_html=True)
                                    if st.button(f"❌ Pass", key=f"r_{c['id']}"):
                                        requests.put(f"{BASE_URL}/candidates/{c['id']}/status", params={"status": "Rejected"})
                                        st.rerun()
                                    st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("The talent network is empty. Post a job to begin.")
        except:
            st.error("Error synchronizing with TiDB Cloud.")

    # --- RECRUITER: POST A JOB ---
    elif choice == "Post a Job":
        st.title("📝 Broadcast New Opportunity")
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        with st.form("job_form", clear_on_submit=True):
            t = st.text_input("Job Title", placeholder="e.g. Lead AI Engineer")
            d = st.text_area("Detailed Mission Description")
            r = st.text_area("Target Skills (comma separated)", placeholder="Python, FastAPI, Cloudinary, TiDB")
            if st.form_submit_button("🚀 Deploy to Market"):
                headers = {"Authorization": f"Bearer {st.session_state.token}"}
                requests.post(f"{BASE_URL}/jobs/", json={"title": t, "description": d, "requirements": r}, headers=headers)
                st.success("Opportunity Broadcasted Successfully.")
        st.markdown("</div>", unsafe_allow_html=True)

    # --- CANDIDATE: PORTAL ---
    elif choice == "Candidate Portal":
        st.title("🚀 Career Command Center")
        t_apply, t_status = st.tabs(["🎯 Available Roles", "📈 My Status"])
        
        with t_apply:
            jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if jobs:
                job_map = {j['title']: j for j in jobs}
                sel_title = st.selectbox("Select Target Mission", list(job_map.keys()))
                job = job_map[sel_title]
                
                st.markdown(f"<div class='glass-card'><h3>{job['title']}</h3><p>{job['description']}</p></div>", unsafe_allow_html=True)
                
                with st.form("apply_form"):
                    email = st.text_input("Communication Email")
                    pdf = st.file_uploader("Upload Digital Resume (PDF)", type=["pdf"])
                    if st.form_submit_button("🚀 Initiate Application"):
                        if email and pdf:
                            with st.spinner("AI Analysis in progress..."):
                                files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
                                payload = {"job_id": job['id'], "full_name": st.session_state.username, "email": email}
                                res = requests.post(f"{BASE_URL}/apply/", data=payload, files=files)
                                if res.status_code == 200:
                                    st.success(f"Deployed! AI Match Score: {res.json().get('score')}%")
                                    st.balloons()
            else:
                st.info("No active missions at this time.")

        with t_status:
            track = st.text_input("Enter Email to track your deployment")
            if st.button("Search Database"):
                apps = requests.get(f"{BASE_URL}/my-applications/{track}").json()
                for a in apps:
                    st.markdown(f"<div class='glass-card'><b>Mission: {a['job_title']}</b><br>Status: {a['status']}</div>", unsafe_allow_html=True)