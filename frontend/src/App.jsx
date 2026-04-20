import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate, Navigate } from 'react-router-dom';
import { 
  Briefcase, Users, FileText, CheckCircle, 
  XCircle, LogOut, UploadCloud, ChevronRight, User as UserIcon
} from 'lucide-react';

const API_BASE = 'https://hiring-portal-xl3g.onrender.com/api/v1';

// ---------- COMPONENTS ----------

const Spinner = () => <div className="spinner"></div>;

const AuthPage = ({ setToken, setRole, setUsername }) => {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ username: '', password: '', role: 'candidate' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      if (isLogin) {
        const res = await fetch(`${API_BASE}/login?username=${formData.username}&password=${formData.password}`, {
          method: 'POST',
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Login failed');
        
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('role', data.role);
        localStorage.setItem('username', data.username);
        
        setToken(data.access_token);
        setRole(data.role);
        setUsername(data.username);
      } else {
        const res = await fetch(`${API_BASE}/signup?username=${formData.username}&password=${formData.password}&role=${formData.role}`, {
          method: 'POST',
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.detail || 'Signup failed');
        setIsLogin(true);
        setError('Signup successful! Please login.');
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container fade-in">
      <div className="glass-panel auth-box">
        <h2 className="page-title gradient-text">{isLogin ? 'Welcome Back' : 'Join NeuralNexus'}</h2>
        {error && <p className="text-danger mb-4 text-center">{error}</p>}
        <form onSubmit={handleSubmit} className="grid">
          <div className="input-group">
            <label className="input-label">Username</label>
            <input 
              type="text" 
              className="glass-input" 
              required
              value={formData.username}
              onChange={e => setFormData({...formData, username: e.target.value})}
            />
          </div>
          <div className="input-group">
            <label className="input-label">Password</label>
            <input 
              type="password" 
              className="glass-input" 
              required
              value={formData.password}
              onChange={e => setFormData({...formData, password: e.target.value})}
            />
          </div>
          {!isLogin && (
            <div className="input-group">
              <label className="input-label">Role</label>
              <select 
                className="glass-input"
                value={formData.role}
                onChange={e => setFormData({...formData, role: e.target.value})}
              >
                <option value="candidate">Candidate</option>
                <option value="recruiter">Recruiter</option>
              </select>
            </div>
          )}
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? <Spinner /> : (isLogin ? 'Login' : 'Sign Up')}
          </button>
        </form>
        <div className="mt-6 text-center">
          <button 
            className="nav-link" 
            onClick={() => setIsLogin(!isLogin)}
          >
            {isLogin ? "Don't have an account? Sign up" : "Already have an account? Login"}
          </button>
        </div>
      </div>
    </div>
  );
};

// -- Candidate Dashboard --
const CandidateDashboard = ({ username }) => {
  const [jobs, setJobs] = useState([]);
  const [myApps, setMyApps] = useState([]);
  const [loading, setLoading] = useState(true);
  const [view, setView] = useState('jobs'); // 'jobs' | 'myapps'
  
  // Apply Job state
  const [selectedJob, setSelectedJob] = useState(null);
  const [applyForm, setApplyForm] = useState({ fullName: '', email: '' });
  const [resume, setResume] = useState(null);
  const [applying, setApplying] = useState(false);
  const [msg, setMsg] = useState('');
  const [emailSearch, setEmailSearch] = useState('');

  useEffect(() => {
    fetchJobs().finally(() => setLoading(false));
  }, [username]);

  const fetchJobs = async () => {
    try {
      const res = await fetch(`${API_BASE}/jobs/`);
      const data = await res.json();
      setJobs(data);
    } catch(err) { console.error(err); }
  };

  const handleSearchApps = async () => {
    if (!emailSearch) return;
    try {
      const res = await fetch(`${API_BASE}/my-applications/${emailSearch}`);
      const data = await res.json();
      if (Array.isArray(data)) setMyApps(data);
      else setMyApps([]);
    } catch(err) { console.error(err); }
  };

  const handleApply = async (e) => {
    e.preventDefault();
    if (!resume) return setMsg("Please upload a resume");
    setApplying(true);
    setMsg('');
    
    const formData = new FormData();
    formData.append('job_id', selectedJob.id);
    formData.append('full_name', applyForm.fullName);
    formData.append('email', applyForm.email);
    formData.append('file', resume);

    try {
      const res = await fetch(`${API_BASE}/apply/`, {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail);
      setMsg(`Success! AI Match Score: ${data.score}%`);
      setSelectedJob(null);
    } catch (err) {
      setMsg(err.message);
    } finally {
      setApplying(false);
    }
  };

  if (loading) return <div className="auth-container"><Spinner /></div>;

  return (
    <div className="fade-in">
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <button className={`btn ${view === 'jobs' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setView('jobs')}>
          <Briefcase size={18} /> Open Roles
        </button>
        <button className={`btn ${view === 'myapps' ? 'btn-primary' : 'btn-secondary'}`} onClick={() => setView('myapps')}>
          <FileText size={18} /> My Applications
        </button>
      </div>

      {msg && <div className="glass-panel" style={{ padding: '1rem', marginBottom: '1rem', color: 'var(--success)' }}>{msg}</div>}

      {view === 'jobs' && !selectedJob && (
        <div className="grid lg:grid-cols-3 md:grid-cols-2">
          {jobs.map(job => (
            <div key={job.id} className="glass-card flex-col">
              <h3 style={{ fontSize: '1.25rem', marginBottom: '0.5rem' }}>{job.title}</h3>
              <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }} className="flex-1">{job.description}</p>
              <button className="btn btn-primary w-full" onClick={() => setSelectedJob(job)}>
                Apply Now <ChevronRight size={18} />
              </button>
            </div>
          ))}
          {jobs.length === 0 && <p>No open roles at the moment.</p>}
        </div>
      )}

      {selectedJob && (
        <div className="glass-panel" style={{ padding: '2rem', maxWidth: '600px', margin: '0 auto' }}>
          <h3 className="mb-4">Apply for {selectedJob.title}</h3>
          <form onSubmit={handleApply} className="grid">
            <div className="input-group">
              <label className="input-label">Full Name</label>
              <input type="text" className="glass-input" required 
                value={applyForm.fullName} onChange={e => setApplyForm({...applyForm, fullName: e.target.value})}
              />
            </div>
            <div className="input-group">
              <label className="input-label">Email</label>
              <input type="email" className="glass-input" required 
                value={applyForm.email} onChange={e => setApplyForm({...applyForm, email: e.target.value})}
              />
            </div>
            <div className="input-group">
              <label className="input-label">Resume (PDF)</label>
              <div className="file-upload-wrapper">
                <input type="file" accept=".pdf" className="file-upload-input" onChange={e => setResume(e.target.files[0])} />
                <div className="file-upload-visual">
                  <UploadCloud />
                  <span>{resume ? resume.name : 'Drag & Drop or Click to Upload'}</span>
                </div>
              </div>
            </div>
            <div style={{ display: 'flex', gap: '1rem' }}>
              <button type="submit" className="btn btn-primary flex-1" disabled={applying}>
                {applying ? <Spinner /> : 'Submit Application'}
              </button>
              <button type="button" className="btn btn-secondary" onClick={() => setSelectedJob(null)}>Cancel</button>
            </div>
          </form>
        </div>
      )}

      {view === 'myapps' && (
        <div className="glass-panel" style={{ padding: '2rem' }}>
          <h3 className="mb-4">My Applications</h3>
          <div className="input-group" style={{ flexDirection: 'row', gap: '1rem', alignItems: 'flex-end', marginBottom: '2rem' }}>
            <div style={{ flex: 1 }}>
              <label className="input-label">Email Used for Application</label>
              <input type="email" className="glass-input" value={emailSearch} onChange={e => setEmailSearch(e.target.value)} placeholder="e.g. user@example.com" />
            </div>
            <button className="btn btn-primary" onClick={handleSearchApps}>Search</button>
          </div>
          
          <div className="grid">
            {myApps.map(app => (
               <div key={app.id} className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                 <div>
                   <h4 style={{ margin: 0 }}>{app.job_title || 'Application'}</h4>
                   <p style={{ margin: '0.25rem 0 0 0', color: 'var(--text-muted)' }}>Match Score: <span className={app.score >= 80 ? 'text-success' : ''}>{app.score}%</span></p>
                 </div>
                 <span className={`status-badge status-${app.status.toLowerCase()}`}>{app.status}</span>
               </div>
            ))}
            {myApps.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No applications found. Please search using the email address you applied with.</p>}
          </div>
        </div>
      )}
    </div>
  );
};

// -- Recruiter Dashboard --
const RecruiterDashboard = () => {
  const [jobs, setJobs] = useState([]);
  const [shortlist, setShortlist] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState(null);
  
  // Create Job state
  const [showCreate, setShowCreate] = useState(false);
  const [createForm, setCreateForm] = useState({ title: '', description: '', requirements: '' });
  const [loadingAction, setLoadingAction] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    const res = await fetch(`${API_BASE}/jobs/`);
    const data = await res.json();
    setJobs(data);
  };

  const fetchShortlist = async (jobId) => {
    setSelectedJobId(jobId);
    setShortlist([]);
    try {
      const res = await fetch(`${API_BASE}/jobs/${jobId}/shortlist`);
      const data = await res.json();
      if (Array.isArray(data)) {
        setShortlist(data);
      } else {
        console.error("Shortlist endpoint did not return an array. Backend issue.", data);
        setShortlist([]);
      }
    } catch(err) {
      console.error(err);
      setShortlist([]);
    }
  };

  const handleCreateJob = async (e) => {
    e.preventDefault();
    setLoadingAction(true);
    await fetch(`${API_BASE}/jobs/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(createForm)
    });
    setLoadingAction(false);
    setShowCreate(false);
    setCreateForm({ title: '', description: '', requirements: '' });
    fetchJobs();
  };

  const handleDeleteJob = async (id) => {
    await fetch(`${API_BASE}/jobs/${id}`, { method: 'DELETE' });
    fetchJobs();
    if (selectedJobId === id) setSelectedJobId(null);
  };

  const handleUpdateStatus = async (candId, status) => {
    await fetch(`${API_BASE}/candidates/${candId}/status?status=${status}`, { method: 'PUT' });
    fetchShortlist(selectedJobId);
  };

  const getScoreClass = (score) => {
    if (score >= 80) return 'score-high';
    if (score >= 50) return 'score-medium';
    return 'score-low';
  };

  return (
    <div className="grid lg:grid-cols-3 fade-in gap-6" style={{ gridTemplateColumns: 'minmax(300px, 1fr) 2fr' }}>
      
      {/* Sidebar: Open Roles */}
      <div className="glass-panel" style={{ padding: '1.5rem', maxHeight: 'calc(100vh - 120px)', overflowY: 'auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h3>Open Roles</h3>
          <button className="btn btn-primary" style={{ padding: '0.5rem 1rem' }} onClick={() => setShowCreate(true)}>
            + New
          </button>
        </div>
        
        <div className="grid grid-cols-1">
          {jobs.map(job => (
            <div 
              key={job.id} 
              className={`glass-card ${selectedJobId === job.id ? 'active' : ''}`}
              style={{ cursor: 'pointer', padding: '1rem', borderColor: selectedJobId === job.id ? 'var(--primary)' : '' }}
              onClick={() => { setShowCreate(false); fetchShortlist(job.id); }}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <h4 style={{ margin: 0 }}>{job.title}</h4>
                <button 
                  className="btn btn-danger" 
                  style={{ padding: '0.25rem 0.5rem' }}
                  onClick={(e) => { e.stopPropagation(); handleDeleteJob(job.id); }}
                >
                  <XCircle size={16} />
                </button>
              </div>
            </div>
          ))}
          {jobs.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No jobs posted yet.</p>}
        </div>
      </div>

      {/* Main Panel */}
      <div className="glass-panel" style={{ padding: '2rem' }}>
        {showCreate ? (
          <div className="fade-in">
            <h3 className="mb-4">Create New Role</h3>
            <form onSubmit={handleCreateJob} className="grid">
              <div className="input-group">
                <label className="input-label">Title</label>
                <input type="text" className="glass-input" required 
                  value={createForm.title} onChange={e => setCreateForm({...createForm, title: e.target.value})} />
              </div>
              <div className="input-group">
                <label className="input-label">Description</label>
                <textarea className="glass-input" required rows="3"
                  value={createForm.description} onChange={e => setCreateForm({...createForm, description: e.target.value})}></textarea>
              </div>
              <div className="input-group">
                <label className="input-label">AI Matching Requirements</label>
                <textarea className="glass-input" required rows="3" placeholder="List keywords, degrees, skills expected..."
                  value={createForm.requirements} onChange={e => setCreateForm({...createForm, requirements: e.target.value})}></textarea>
              </div>
              <button type="submit" className="btn btn-primary" disabled={loadingAction}>
                {loadingAction ? <Spinner /> : 'Publish Role'}
              </button>
            </form>
          </div>
        ) : selectedJobId ? (
          <div className="fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h3 style={{ margin: 0 }}>Candidates Shortlist</h3>
              <span className="status-badge status-shortlisted">{shortlist.length} Applicants</span>
            </div>
            
            <div style={{ overflowX: 'auto' }}>
              <table className="glass-table">
                <thead>
                  <tr>
                    <th>Candidate</th>
                    <th>Match</th>
                    <th>Status</th>
                    <th>Resume</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {shortlist.map(c => (
                    <tr key={c.id}>
                      <td>
                        <div style={{ fontWeight: 500 }}>{c.full_name}</div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{c.email}</div>
                      </td>
                      <td>
                        <div className={`score-badge ${getScoreClass(c.score)}`}>
                          {c.score}
                        </div>
                      </td>
                      <td>
                        <span className={`status-badge status-${c.status.toLowerCase()}`}>
                          {c.status}
                        </span>
                      </td>
                      <td>
                        <button 
                          className="btn btn-secondary" 
                          style={{ padding: '0.25rem 0.5rem', fontSize: '0.8rem' }}
                          onClick={() => setPdfUrl(c.file_path)}
                        >
                          View PDF
                        </button>
                      </td>
                      <td>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <button className="btn btn-secondary" style={{ padding: '0.25rem 0.5rem', color: 'var(--success)', borderColor: 'var(--success)' }}
                            onClick={() => handleUpdateStatus(c.id, 'Shortlisted')} title="Shortlist">
                            <CheckCircle size={16} />
                          </button>
                          <button className="btn btn-danger" style={{ padding: '0.25rem 0.5rem' }}
                            onClick={() => handleUpdateStatus(c.id, 'Rejected')} title="Reject">
                            <XCircle size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                  {shortlist.length === 0 && (
                    <tr>
                      <td colSpan="5" style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                        No candidates have applied yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
            <div style={{ textAlign: 'center' }}>
              <Users size={48} style={{ opacity: 0.5, marginBottom: '1rem', margin: '0 auto' }} />
              <p>Select a role to view candidates</p>
            </div>
          </div>
        )}
      </div>

      {/* PDF View Modal */}
      {pdfUrl && (
        <div style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.85)', zIndex: 9999, display: 'flex', flexDirection: 'column', backdropFilter: 'blur(8px)' }}>
          <div style={{ padding: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'var(--bg-darker)', borderBottom: '1px solid var(--panel-border)' }}>
            <h3 style={{ margin: 0 }}>Resume Viewer</h3>
            <button className="btn btn-danger" onClick={() => setPdfUrl(null)}><XCircle size={18} /> Close</button>
          </div>
          <div style={{ flex: 1, position: 'relative' }}>
            <iframe 
               src={`https://docs.google.com/viewer?url=${encodeURIComponent(pdfUrl)}&embedded=true`}
               style={{ width: '100%', height: '100%', border: 'none' }}
               title="PDF Viewer"
            ></iframe>
          </div>
        </div>
      )}
    </div>
  );
};

// -- Main App Component --
export default function App() {
  const [session, setSession] = useState(() => ({
    token: localStorage.getItem('token') || null,
    role: localStorage.getItem('role') || null,
    username: localStorage.getItem('username') || null,
  }));

  const updateSession = (token, role, username) => {
    if (token) {
      localStorage.setItem('token', token);
      localStorage.setItem('role', role);
      localStorage.setItem('username', username);
    } else {
      localStorage.clear();
    }
    setSession({ token, role, username });
  };

  const logout = () => {
    updateSession(null, null, null);
  };

  return (
    <Router>
      <div className="app-container">
        
        {/* Navigation / Header */}
        <nav className="glass-panel navbar fade-in">
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ background: 'var(--primary)', padding: '0.5rem', borderRadius: '8px' }}>
              <Briefcase color="white" size={24} />
            </div>
            <h1 style={{ fontSize: '1.5rem', margin: 0 }} className="gradient-text">NeuralNexus</h1>
          </div>
          
          {session.token && (
            <div className="nav-links">
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'rgba(255,255,255,0.05)', padding: '0.5rem 1rem', borderRadius: '99px' }}>
                <UserIcon size={16} />
                <span style={{ fontSize: '0.9rem', fontWeight: 500 }}>{session.username}</span>
                <span className="status-badge status-shortlisted" style={{ marginLeft: '0.5rem' }}>{session.role}</span>
              </div>
              <button className="btn btn-secondary" onClick={logout} style={{ padding: '0.5rem' }} title="Logout">
                <LogOut size={18} />
              </button>
            </div>
          )}
        </nav>

        {/* Main Content Area */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          {!session.token ? (
            <AuthPage 
              setToken={(t) => updateSession(t, localStorage.getItem('role'), localStorage.getItem('username'))} 
              setRole={(r) => updateSession(localStorage.getItem('token'), r, localStorage.getItem('username'))} 
              setUsername={(u) => updateSession(localStorage.getItem('token'), localStorage.getItem('role'), u)} 
            />
          ) : (
            <Routes>
              {session.role === 'recruiter' ? (
                <>
                  <Route path="/" element={<RecruiterDashboard />} />
                  <Route path="*" element={<Navigate to="/" />} />
                </>
              ) : (
                <>
                  <Route path="/" element={<CandidateDashboard username={session.username} />} />
                  <Route path="*" element={<Navigate to="/" />} />
                </>
              )}
            </Routes>
          )}
        </div>
      </div>
    </Router>
  );
}
