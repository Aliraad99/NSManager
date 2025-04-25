document.addEventListener("DOMContentLoaded", () => {
    const loginForm = document.querySelector("form.needs-validation");
  
    loginForm.addEventListener("submit", async (event) => {
      event.preventDefault(); 
  
      const email = document.getElementById("email").value;
      const password = document.getElementById("yourPassword").value;
  
      console.log("Submitting login request with:", { UserEmail: email, UserPassword: password });
  
      try {
        const response = await fetch("http://localhost:8010/Auth/Login/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            UserEmail: email,
            UserPassword: password,
          }),
        });
  
        console.log("Response status:", response.status);
  
        if (!response.ok) {
          const errorData = await response.json();
          console.error("Error response:", errorData);
          const errorMessage = errorData.detail || "Login failed. Please try again.";
          alert(typeof errorMessage === "string" ? errorMessage : JSON.stringify(errorMessage));
          return;
        }
  
        const data = await response.json();
        console.log("Login successful, response data:", data);
        localStorage.setItem("access_token", data.access_token); // Store token in localStorage
        alert("Login successful!");
        window.location.href = "index.html"; // Redirect to dashboard or another page
      } catch (error) {
        console.error("Error during login:", error);
        alert("An error occurred. Please try again later.");
      }
    });
  });