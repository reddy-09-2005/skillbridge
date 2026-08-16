function renderJobList(container, jobs) {
  container.innerHTML = "";

  if (!jobs || jobs.length === 0) {
    container.innerHTML = '<p class="empty-state">No matching jobs found.</p>';
    return;
  }

  jobs.forEach((job) => {
    const card = document.createElement("div");
    card.className = "job-card";

    const matchTags = (job.matched_skills || [])
      .map((s) => `<span class="tag tag-match">${s}</span>`)
      .join("");
    const missingTags = (job.missing_skills || [])
      .map((s) => `<span class="tag tag-missing">${s}</span>`)
      .join("");

    card.innerHTML = `
      <div class="job-card-header">
        <strong>${job.title || "Untitled role"}</strong>
        ${job.match_score != null ? `<span class="match-score">${job.match_score}% match</span>` : ""}
      </div>
      <p class="job-meta">${job.company || ""}${job.location ? " — " + job.location : ""}</p>
      <div>${matchTags}${missingTags}</div>
      ${job.url ? `<p><a class="job-link" href="${job.url}" target="_blank" rel="noopener">View job</a></p>` : ""}
    `;
    container.appendChild(card);
  });
}

window.renderJobList = renderJobList;