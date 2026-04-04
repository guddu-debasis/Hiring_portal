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

# Modern UI Enhancements (Deep Night & Emerald Theme)
st.markdown("""
    <style>
    /* Global Styles */
    .stApp {
        background: radial-gradient(circle at top right, #1a1c24, #0e1117);
    }
    
    /* Custom Card Styling */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 15px;
        padding: 25px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }

    /* Animated Button */
    div.stButton > button {
        border-radius: 12px;
        padding: 10px 24px;
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

    /* Sidebar Role Badge */
    .role-badge {
        background: #1f222d;
        padding: 5px 12px;
        border-radius: 20px;
        border: 1px solid #4CAF50;
        font-size: 0.8rem;
        color: #4CAF50;
    }

    /* Match Score Circle */
    .score-container {
        text-align: center;
        padding: 20px;
        border-radius: 50%;
        border: 4px solid #4CAF50;
        width: 100px;
        height: 100px;
        display: flex;
        align-items: center;
        justify-content: center;
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
# Ensure BASE_URL points to your Render API
BASE_URL = st.secrets.get("BASE_URL", "https://hiring-portal-xl3g.onrender.com/api/v1")

# --- 3. AUTHENTICATION UI (The "Stunning" Login) ---
if not st.session_state.logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>🧠 MindSpark-Ai</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #888;'>The future of talent acquisition is here.</p>", unsafe_allow_html=True)
        
        tab_login, tab_signup = st.tabs(["🔐 Secure Entry", "🚀 Join the Network"])

        with tab_login:
            with st.form("login_form"):
                u = st.text_input("Username", placeholder="Enter your ID")
                p = st.text_input("Password", type="password", placeholder="••••••••")
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
                            st.error("Access Denied: Invalid Credentials")
                    except Exception as e:
                        st.error(f"Server Unreachable. Please check BASE_URL.")

        with tab_signup:
            with st.form("signup_form"):
                nu = st.text_input("Choose Username")
                np = st.text_input("Create Password", type="password")
                nr = st.selectbox("I am a...", ["candidate", "recruiter"])
                if st.form_submit_button("Create My Account"):
                    try:
                        res = requests.post(f"{BASE_URL}/signup", params={"username": nu, "password": np, "role": nr})
                        if res.status_code == 200:
                            st.success("Account Ready! Head over to Login.")
                    except Exception as e:
                        st.error(f"Registration Error: {e}")
    st.stop()

# --- 4. PROTECTED CONTENT (The Dashboard) ---
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
        st.title("🚀 Open a New Frontier")
        with st.container():
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            with st.form("job_form"):
                t = st.text_input("Job Title", placeholder="e.g. Lead Python Developer")
                d = st.text_area("What's the mission? (Description)")
                r = st.text_area("Tech Stack / Requirements", placeholder="Python, FastAPI, TiDB, React")
                if st.form_submit_button("Publish to Network"):
                    if t and d and r:
                        headers = {"Authorization": f"Bearer {st.session_state.token}"}
                        requests.post(f"{BASE_URL}/jobs/", json={"title": t, "description": d, "requirements": r}, headers=headers)
                        st.success("Job Published Successfully!")
            st.markdown("</div>", unsafe_allow_html=True)

    # --- RECRUITER: DASHBOARD (Optimized for Cloudinary) ---
    elif choice == "Recruiter Dashboard":
        st.title("📊 Talent Intelligence Center")
        try:
            jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if jobs:
                job_list = {j['title']: j['id'] for j in jobs}
                sel_job = st.selectbox("Select Active Vacancy", list(job_list.keys()))
                j_id = job_list[sel_job]

                st.divider()
                cands = requests.get(f"{BASE_URL}/jobs/{j_id}/shortlist").json()
                
                if not cands:
                    st.info("No operatives have applied for this mission yet.")
                else:
                    for c in cands:
                        score = c.get('score', 0)
                        status = c.get('status', 'Pending')
                        
                        # Glassmorphism Expander
                        with st.expander(f"⚡ {c.get('full_name')} — Match: {score}%"):
                            col_res, col_ai = st.columns([1.5, 1])
                            
                            with col_res:
                                st.markdown("##### 📄 Digital Portfolio")
                                resume_url = c.get('file_path') # This is now our Cloudinary URL!
                                if resume_url:
                                    # STUNNING PDF EMBED
                                    st.markdown(f'<iframe src="{resume_url}" width="100%" height="700px" style="border-radius:12px; border:none;"></iframe>', unsafe_allow_html=True)
                                else:
                                    st.warning("Resume file missing in Cloudinary.")

                            with col_ai:
                                st.markdown("##### 🤖 AI Engine Analysis")
                                st.markdown(f"<div class='glass-card' style='border-left: 4px solid #4CAF50;'><b>Summary:</b><br>{c.get('resume_summary')}</div>", unsafe_allow_html=True)
                                st.info(f"**Identified Skills:** {c.get('skills')}")
                                
                                st.divider()
                                if st.button(f"✅ Select {c.get('full_name')}", key=f"h_{c['id']}"):
                                    requests.put(f"{BASE_URL}/candidates/{c['id']}/status", params={"status": "Selected"})
                                    st.rerun()
                                if st.button(f"❌ Pass", key=f"r_{c['id']}"):
                                    requests.put(f"{BASE_URL}/candidates/{c['id']}/status", params={"status": "Rejected"})
                                    st.rerun()
            else:
                st.warning("No jobs currently active.")
        except Exception as e:
            st.error(f"Interface Error: {e}")

    # --- CANDIDATE: PORTAL ---
    elif choice == "Candidate Portal":
        st.title("🚀 Career Command Center")
        tab1, tab2 = st.tabs(["🎯 Opportunities", "📈 Status Tracker"])

        with tab1:
            all_jobs = requests.get(f"{BASE_URL}/jobs/").json()
            if all_jobs:
                job_lookup = {j['title']: j for j in all_jobs}
                title = st.selectbox("Choose your next challenge", list(job_lookup.keys()))
                job = job_lookup[title]
                
                st.markdown(f"<div class='glass-card'><h3>{job['title']}</h3><p>{job['description']}</p></div>", unsafe_allow_html=True)
                
                with st.form("apply"):
                    email = st.text_input("Your Professional Email")
                    pdf = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
                    if st.form_submit_button("Submit to AI Engine"):
                        if email and pdf:
                            with st.spinner("AI is evaluating your fit..."):
                                files = {"file": (pdf.name, pdf.getvalue(), "application/pdf")}
                                data = {"job_id": job['id'], "full_name": st.session_state.username, "email": email}
                                res = requests.post(f"{BASE_URL}/apply/", data=data, files=files)
                                if res.status_code == 200:
                                    st.success(f"Deployed! Match Score: {res.json().get('score')}%")
                                    st.balloons()
            else:
                st.info("The intelligence network is searching for new roles...")

        with tab2:
            email_track = st.text_input("Check status via email")
            if st.button("Track Progress"):
                apps = requests.get(f"{BASE_URL}/my-applications/{email_track}").json()
                for a in apps:
                    st.markdown(f"<div class='glass-card'><b>{a['job_title']}</b> — Status: {a['status']}</div>", unsafe_allow_html=True)