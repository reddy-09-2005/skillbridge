const API_BASE_URL = "http://127.0.0.1:5000/api";

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

window.SkillBridgeAPI = { uploadResume, getRecommendations, searchJobs };