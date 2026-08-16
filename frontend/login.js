loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const submitBtn = loginForm.querySelector('button[type="submit"], button');
    if (submitBtn) submitBtn.disabled = true;

    const email = document.getElementById("loginEmail").value.trim().toLowerCase();
    const password = document.getElementById("loginPassword").value;

    localStorage.removeItem("token");
    localStorage.removeItem("email");

    try {
        const response = await fetch("http://127.0.0.1:5000/api/auth/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();
        console.log("Login response:", data);

        if (response.ok && data.token) {
            localStorage.setItem("token", data.token);
            localStorage.setItem("email", data.email || email);
            window.location.href = "dashboard.html";
        } else {
            alert(data.error || "Login failed");
            if (submitBtn) submitBtn.disabled = false;
        }
    } catch (error) {
        console.error("Login error:", error);
        alert("Cannot connect to the SkillBridge server. Make sure Flask is running on port 5000.");
        if (submitBtn) submitBtn.disabled = false;
    }
});