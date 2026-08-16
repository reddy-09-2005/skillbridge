// Require login before showing this page
const token = localStorage.getItem("token");
if (!token) {
  window.location.href = "login.html";
}
document.addEventListener("DOMContentLoaded", () => {
  const resumeInput = document.getElementById("resume-input");
  const uploadBtn = document.getElementById("upload-btn");
  const findJobsBtn = document.getElementById("find-jobs-btn");
  const keywordsInput = document.getElementById("keywords-input");
  const locationInput = document.getElementById("location-input");
  const statusEl = document.getElementById("status");
  const jobListEl = document.getElementById("job-list");
 
  uploadBtn.addEventListener("click", async () => {
    const file = resumeInput.files[0];
    if (!file) {
      statusEl.textContent = "Choose a resume file first.";
      return;
    }
    await SkillBridgeApp.handleResumeUpload(file, statusEl);
  });
 
  findJobsBtn.addEventListener("click", () => {
    SkillBridgeApp.handleFindJobs(
      keywordsInput.value.trim(),
      locationInput.value.trim(),
      jobListEl,
      statusEl
    );
  });
});