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

        "dashboard-section":
            "Dashboard",

        "upload-section":
            "Upload Resume",

        "jobs-section":
            "Job Recommendations",

        "history-section":
            "Resume History",

        "profile-section":
            "Profile"
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