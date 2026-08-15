import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import axios from "axios";
import api, { TOKEN_STORAGE_KEY } from "./services/api";
import "./App.css";

type User = { id: number; username: string; email: string };
type Project = { id: number; name: string; description: string | null; owner_id: number; created_at: string; updated_at: string };
type TokenResponse = { access_token: string; token_type: string };

function messageFrom(error: unknown, fallback: string) {
  if (axios.isAxiosError(error) && typeof error.response?.data?.detail === "string") return error.response.data.detail;
  return fallback;
}

function App() {
  const [user, setUser] = useState<User | null>(null);
  const [projects, setProjects] = useState<Project[]>([]);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [projectName, setProjectName] = useState("");
  const [projectDescription, setProjectDescription] = useState("");
  const [loading, setLoading] = useState(Boolean(sessionStorage.getItem(TOKEN_STORAGE_KEY)));
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");

  const loadWorkspace = async () => {
    const [userResponse, projectsResponse] = await Promise.all([api.get<User>("/users/me/"), api.get<Project[]>("/projects/")]);
    setUser(userResponse.data);
    setProjects(projectsResponse.data);
  };

  useEffect(() => {
    if (!sessionStorage.getItem(TOKEN_STORAGE_KEY)) return;
    loadWorkspace().catch((requestError) => {
      sessionStorage.removeItem(TOKEN_STORAGE_KEY);
      setError(messageFrom(requestError, "Your session has expired. Please sign in again."));
    }).finally(() => setLoading(false));
  }, []);

  const signIn = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); setError(""); setSubmitting(true);
    try {
      const response = await api.post<TokenResponse>("/token", new URLSearchParams({ username, password }), { headers: { "Content-Type": "application/x-www-form-urlencoded" } });
      sessionStorage.setItem(TOKEN_STORAGE_KEY, response.data.access_token);
      await loadWorkspace(); setPassword("");
    } catch (requestError) { setError(messageFrom(requestError, "Unable to sign in. Check your username and password.")); }
    finally { setSubmitting(false); }
  };

  const createProject = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault(); if (!projectName.trim()) return;
    setError(""); setSubmitting(true);
    try {
      const response = await api.post<Project>("/projects/", { name: projectName.trim(), description: projectDescription.trim() || null });
      setProjects((current) => [response.data, ...current]); setProjectName(""); setProjectDescription("");
    } catch (requestError) { setError(messageFrom(requestError, "Unable to create the project.")); }
    finally { setSubmitting(false); }
  };

  const signOut = () => { sessionStorage.removeItem(TOKEN_STORAGE_KEY); setUser(null); setProjects([]); setError(""); };
  if (loading) return <main className="app-shell"><p>Connecting to your workspace...</p></main>;
  if (!user) return <main className="app-shell auth-shell"><section className="panel auth-panel"><p className="eyebrow">Virtual Office</p><h1>AI Software Company</h1><p>Sign in with the account you verified against the FastAPI backend.</p>{error && <p className="error" role="alert">{error}</p>}<form onSubmit={signIn} className="form-stack"><label>Username<input value={username} onChange={(event) => setUsername(event.target.value)} autoComplete="username" required /></label><label>Password<input value={password} onChange={(event) => setPassword(event.target.value)} type="password" autoComplete="current-password" required /></label><button disabled={submitting} type="submit">{submitting ? "Signing in..." : "Sign in"}</button></form></section></main>;
  return <main className="app-shell"><header className="topbar"><div><p className="eyebrow">Virtual Office</p><h1>AI Software Company</h1></div><div className="account"><span>{user.username}</span><button className="secondary" type="button" onClick={signOut}>Sign out</button></div></header>{error && <p className="error" role="alert">{error}</p>}<section className="workspace-grid"><section className="panel"><p className="eyebrow">Projects</p><h2>{projects.length} project{projects.length === 1 ? "" : "s"}</h2><div className="project-list">{projects.length === 0 ? <p className="muted">No projects yet. Create the first one.</p> : projects.map((project) => <article className="project" key={project.id}><h3>{project.name}</h3><p>{project.description || "No description provided."}</p><small>Created {new Date(project.created_at).toLocaleString()}</small></article>)}</div></section><section className="panel"><p className="eyebrow">New project</p><h2>Start a project</h2><form onSubmit={createProject} className="form-stack"><label>Name<input value={projectName} onChange={(event) => setProjectName(event.target.value)} maxLength={200} required /></label><label>Description<textarea value={projectDescription} onChange={(event) => setProjectDescription(event.target.value)} rows={5} /></label><button disabled={submitting} type="submit">{submitting ? "Creating..." : "Create project"}</button></form></section></section></main>;
}

export default App;

