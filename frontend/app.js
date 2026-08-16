const state = {
  resumeText: "",
  skills: [],
};
 
async function handleResumeUpload(file, statusEl) {
  statusEl.textContent = "Parsing resume...";
  try {
    const { resume_text, skills } = await SkillBridgeAPI.uploadResume(file);
    state.resumeText = resume_text;
    state.skills = skills;
    statusEl.textContent = skills.length
      ? `Found ${skills.length} skills: ${skills.join(", ")}`
      : "Resume parsed, but no known skills were detected.";
    return true;
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
    return false;
  }
}
 
async function handleFindJobs(keywords, location, jobListEl, statusEl) {
  if (!state.resumeText) {
    statusEl.textContent = "Upload a resume first.";
    return;
  }
  statusEl.textContent = "Finding matching jobs...";
  try {
    const { jobs } = await SkillBridgeAPI.getRecommendations(
      state.resumeText,
      keywords,
      location
    );
    renderJobList(jobListEl, jobs);
    statusEl.textContent = `Found ${jobs.length} matching jobs.`;
  } catch (err) {
    statusEl.textContent = `Error: ${err.message}`;
  }
}
 
window.SkillBridgeApp = { state, handleResumeUpload, handleFindJobs };
