const loginForm = document.getElementById("loginForm");

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const submitBtn = loginForm.querySelector('button[type="submit"], button');
    if (submitBtn) submitBtn.disabled = true;

    const email = document.getElementById("loginEmail").value.trim().toLowerCase();
    const password = document.getElementById("loginPassword").value;

    localStorage.removeItem("token");
    localStorage.removeItem("email");

    const baseUrl = window.API_BASE_URL || (
      (window.location.port === "5500" || window.location.port === "5501" || window.location.protocol === "file:")
        ? "http://127.0.0.1:5000/api"
        : (window.location.origin ? `${window.location.origin}/api` : "http://127.0.0.1:5000/api")
    );

    try {
      const response = await fetch(`${baseUrl}/auth/login`, {
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
      alert("Cannot connect to the SkillBridge server. Please check your backend connection.");
      if (submitBtn) submitBtn.disabled = false;
    }
  });
}