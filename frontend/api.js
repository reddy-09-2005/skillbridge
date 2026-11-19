/**
 * SkillBridge AI - Frontend API Client
 * Dynamically resolves API URL across local development, Docker, and Cloud deployments (Render, Vercel, Railway).
 */

const API_BASE_URL = window.API_BASE_URL || (
  (window.location.port === "5500" || window.location.port === "5501" || window.location.protocol === "file:")
    ? "http://127.0.0.1:5000/api"
    : (window.location.origin ? `${window.location.origin}/api` : "http://127.0.0.1:5000/api")
);

window.API_BASE_URL = API_BASE_URL;

function authHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function uploadResume(file) {
  const formData = new FormData();
  formData.append("resume", file);

  const res = await fetch(`${API_BASE_URL}/upload-resume`, {
    method: "POST",
    headers: { ...authHeaders() },
    body: formData,
  });
  if (!res.ok) throw new Error((await res.json()).error || "Upload failed");
  return res.json();
}

async function getRecommendations(resumeText, keywords, location, topN = 10) {
  const res = await fetch(`${API_BASE_URL}/recommend`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({
      resume_text: resumeText,
      keywords,
      location,
      top_n: topN,
    }),
  });
  if (!res.ok) throw new Error((await res.json()).error || "Recommendation failed");
  return res.json();
}

async function searchJobs(keywords, location, limit = 25) {
  const params = new URLSearchParams({ keywords, limit });
  if (location) params.append("location", location);

  const res = await fetch(`${API_BASE_URL}/jobs/search?${params}`, {
    headers: { ...authHeaders() },
  });
  if (!res.ok) throw new Error((await res.json()).error || "Job search failed");
  return res.json();
}

async function getSkillRecommendations(targetRole) {
  const res = await fetch(`${API_BASE_URL}/skill-recommendations`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ target_role: targetRole }),
  });
  if (!res.ok) throw new Error((await res.json()).error || "Skill recommendation failed");
  return res.json();
}

async function getAvailableRoles() {
  const res = await fetch(`${API_BASE_URL}/available-roles`);
  if (!res.ok) throw new Error("Could not load roles");
  return res.json();
}

window.SkillBridgeAPI = {
  uploadResume,
  getRecommendations,
  searchJobs,
  getSkillRecommendations,
  getAvailableRoles,
  API_BASE_URL,
};