/* =========================================================
   SKILLBRIDGE DASHBOARD
   ========================================================= */

const token = localStorage.getItem("token");
const email = localStorage.getItem("email");

if (!token) {
    window.location.href = "login.html";
}

const sessionHistory = [];


/* =========================================================
   PAGE LOAD
   ========================================================= */

document.addEventListener("DOMContentLoaded", () => {

    /* -----------------------------------------------------
       PROFILE / EMAIL
    ----------------------------------------------------- */

    const welcomeEl = document.getElementById("welcomeText");
    const profileEmailEl = document.getElementById("profileEmail");

    if (email) {

        if (welcomeEl) {
            welcomeEl.textContent = `Welcome, ${email}`;
        }

        if (profileEmailEl) {
            profileEmailEl.textContent = email;
        }
    }


    /* -----------------------------------------------------
       SECTION NAVIGATION
    ----------------------------------------------------- */

    const navLinks = document.querySelectorAll(
        ".sidebar a[data-target]"
    );

    const sections = document.querySelectorAll(".section");

    const sectionTitle =
        document.getElementById("sectionTitle");


    const titles = {

        "dashboard-section": "Dashboard",
        "guide-section": "How It Works",
        "upload-section": "Upload Resume",
        "jobs-section": "Job Recommendations",
        "history-section": "Resume History",
        "profile-section": "Profile",
        "skills-section": "Recommended Skills"
    };


    function showSection(targetId) {

        sections.forEach(section => {

            section.classList.toggle(
                "active",
                section.id === targetId
            );

        });


        navLinks.forEach(link => {

            link.classList.toggle(
                "active-link",
                link.dataset.target === targetId
            );

        });


        if (sectionTitle) {

            sectionTitle.textContent =
                titles[targetId] || "Dashboard";

        }


        /* Scroll page to top */

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    }


    navLinks.forEach(link => {

        link.addEventListener("click", event => {

            event.preventDefault();

            showSection(
                link.dataset.target
            );

        });

    });


    /* -----------------------------------------------------
       SHARED: FLOWCHART RENDERER
    ----------------------------------------------------- */

    function renderFlowchart(steps) {

        return steps
            .map(
                (step, index) => `
                    <div class="flow-step">
                        <div class="flow-step-badge">${index + 1}</div>
                        <div class="flow-step-body">
                            <div class="flow-step-title">${step.title}</div>
                            <div class="flow-step-duration">${step.duration}</div>
                            <div class="flow-step-detail">${step.detail}</div>
                        </div>
                    </div>
                    ${index < steps.length - 1 ? '<div class="flow-connector"></div>' : ""}
                `
            )
            .join("");

    }


    /* -----------------------------------------------------
       PROJECT GUIDE (static, no API call)
    ----------------------------------------------------- */

    const guideSteps = [
        {
            title: "Upload your resume",
            duration: "1 minute",
            detail: "Go to Upload Resume and add a PDF, DOCX, or TXT file. SkillBridge reads it and pulls out the skills it can detect."
        },
        {
            title: "See your detected skills",
            duration: "Instant",
            detail: "After uploading, your skill count appears on the Dashboard, and every past upload is saved under Resume History."
        },
        {
            title: "Explore job recommendations",
            duration: "A few minutes",
            detail: "Go to Job Recommendations and search keywords (or leave them blank to auto-use your resume's top skills) to see matching live job postings."
        },
        {
            title: "Check Recommended Skills for a target role",
            duration: "A few minutes",
            detail: "Type any job title — like Cloud Engineer, Data Analyst, or Product Manager — under Recommended Skills. SkillBridge compares your resume's skills against real, current postings for that role."
        },
        {
            title: "Follow the study flowchart for each missing skill",
            duration: "Days to weeks, per skill",
            detail: "Every recommended skill comes with its own step-by-step flowchart, plus Docs, Course, and YouTube links to actually learn it."
        },
        {
            title: "Ask the Assistant anytime",
            duration: "Instant",
            detail: "Type or say any job title to the SkillBridge Assistant in the corner, and it'll read your match percentage and top skills to learn out loud."
        }
    ];

    const guideFlowchartEl =
        document.getElementById("guide-flowchart");

    if (guideFlowchartEl) {
        guideFlowchartEl.innerHTML = renderFlowchart(guideSteps);
    }


    /* -----------------------------------------------------
       HERO BUTTON
    ----------------------------------------------------- */

    document
        .querySelectorAll(".primary-btn[data-target]")
        .forEach(button => {

            button.addEventListener("click", () => {

                const target =
                    button.dataset.target;

                showSection(target);

            });

        });


    /* -----------------------------------------------------
       LOGOUT
    ----------------------------------------------------- */

    const logoutLink =
        document.getElementById("logoutLink");

    if (logoutLink) {

        logoutLink.addEventListener(
            "click",
            event => {

                event.preventDefault();

                localStorage.removeItem("token");
                localStorage.removeItem("email");

                window.location.href =
                    "login.html";
            }
        );
    }


    /* -----------------------------------------------------
       UPLOAD RESUME
    ----------------------------------------------------- */

    const resumeInput =
        document.getElementById("resume-input");

    const uploadBtn =
        document.getElementById("upload-btn");

    const statusEl =
        document.getElementById("status");


    if (uploadBtn) {

        uploadBtn.addEventListener(
            "click",
            async () => {

                const file =
                    resumeInput.files[0];


                if (!file) {

                    statusEl.textContent =
                        "Choose a resume file first.";

                    return;
                }


                statusEl.textContent =
                    "Uploading and analyzing resume...";


                try {

                    const ok =
                        await SkillBridgeApp.handleResumeUpload(
                            file,
                            statusEl
                        );


                    if (ok) {

                        const skillCount =
                            SkillBridgeApp.state.skills.length;


                        sessionHistory.push({

                            skillCount:
                                skillCount,

                            uploadedAt:
                                new Date().toLocaleString()

                        });


                        updateDashboardStats();

                        updateHistoryTable();

                    }

                } catch (error) {

                    console.error(
                        "Resume upload error:",
                        error
                    );

                    statusEl.textContent =
                        "Resume upload failed.";

                }

            }
        );
    }


    /* -----------------------------------------------------
       JOB RECOMMENDATIONS
    ----------------------------------------------------- */

    const keywordsInput =
        document.getElementById(
            "keywords-input"
        );

    const locationInput =
        document.getElementById(
            "location-input"
        );

    const findJobsBtn =
        document.getElementById(
            "find-jobs-btn"
        );

    const jobsStatusEl =
        document.getElementById(
            "jobs-status"
        );

    const jobListEl =
        document.getElementById(
            "job-list"
        );


    if (findJobsBtn) {

        findJobsBtn.addEventListener(
            "click",
            async () => {

                try {

                    await SkillBridgeApp.handleFindJobs(

                        keywordsInput.value.trim(),

                        locationInput.value.trim(),

                        jobListEl,

                        jobsStatusEl

                    );

                    updateDashboardStats();

                } catch (error) {

                    console.error(
                        "Job search error:",
                        error
                    );

                }

            }
        );
    }


    /* -----------------------------------------------------
       SKILL RECOMMENDATIONS
    ----------------------------------------------------- */

    const roleInput =
        document.getElementById("role-input");

    const getSkillsBtn =
        document.getElementById("get-skills-btn");

    const skillsStatusEl =
        document.getElementById("skills-status");

    const skillsResultEl =
        document.getElementById("skills-result");


    if (getSkillsBtn) {

        getSkillsBtn.addEventListener(
            "click",
            async () => {

                const role = roleInput.value.trim();

                if (!role) {
                    skillsStatusEl.textContent = "Type a job title first.";
                    return;
                }

                skillsStatusEl.textContent =
                    "Analyzing current job postings...";

                skillsResultEl.innerHTML = "";


                try {

                    const data =
                        await SkillBridgeAPI.getSkillRecommendations(role);


                    if (data.error) {

                        skillsStatusEl.textContent =
                            data.error;

                        return;
                    }


                    skillsStatusEl.textContent =
                        `Based on ${data.based_on_postings} postings — Match: ${data.match_percentage}%`;


                    const matchedHtml =
                        data.matched_skills
                            .map(s => `<li>${s}</li>`)
                            .join("") || "<li>None yet</li>";


                    const recommendedHtml =
                        data.recommended_skills
                            .map(
                                item => `
                                    <div class="skill-card">

                                        <div class="skill-card-header">
                                            <strong>${item.skill}</strong>
                                        </div>

                                        <div class="skill-links">
                                            <a href="${item.resources.docs}" target="_blank" rel="noopener">Docs</a>
                                            <a href="${item.resources.course}" target="_blank" rel="noopener">Course</a>
                                            <a href="${item.resources.youtube}" target="_blank" rel="noopener">YouTube</a>
                                        </div>

                                        <div class="flowchart">
                                            ${renderFlowchart(item.steps)}
                                        </div>

                                    </div>
                                `
                            )
                            .join("") || "<p>None — fully matched!</p>";


                    skillsResultEl.innerHTML = `
                        <h4>You already have:</h4>
                        <ul>${matchedHtml}</ul>

                        <h4>Recommended to learn:</h4>
                        ${recommendedHtml}
                    `;

                } catch (error) {

                    console.error(
                        "Skill recommendation error:",
                        error
                    );

                    skillsStatusEl.textContent =
                        "Could not load recommendations.";

                }

            }
        );
    }


    /* -----------------------------------------------------
       DASHBOARD STATISTICS
    ----------------------------------------------------- */

    function updateDashboardStats() {

        const totalResumesEl =
            document.getElementById(
                "totalResumes"
            );

        const totalSkillsEl =
            document.getElementById(
                "totalSkills"
            );

        const totalJobsEl =
            document.getElementById(
                "totalJobs"
            );


        if (totalResumesEl) {

            totalResumesEl.textContent =
                sessionHistory.length;

        }


        if (
            totalSkillsEl &&
            window.SkillBridgeApp &&
            SkillBridgeApp.state
        ) {

            totalSkillsEl.textContent =
                SkillBridgeApp.state.skills.length;

        }


        if (totalJobsEl) {

            const jobs =
                document.querySelectorAll(
                    "#job-list .job-card"
                );

            totalJobsEl.textContent =
                jobs.length;

        }

    }


    /* -----------------------------------------------------
       HISTORY
    ----------------------------------------------------- */

    function updateHistoryTable() {

        const body =
            document.getElementById(
                "history-body"
            );


        if (!body) {
            return;
        }


        if (sessionHistory.length === 0) {

            body.innerHTML = `
                <tr>
                    <td colspan="3">
                        No resumes uploaded yet.
                    </td>
                </tr>
            `;

            return;
        }


        body.innerHTML =
            sessionHistory
                .map(
                    (history, index) => `
                        <tr>
                            <td>${index + 1}</td>
                            <td>${history.skillCount}</td>
                            <td>${history.uploadedAt}</td>
                        </tr>
                    `
                )
                .join("");

    }


    /* -----------------------------------------------------
       INITIALIZE
    ----------------------------------------------------- */

    updateDashboardStats();

    updateHistoryTable();

});