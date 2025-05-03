const API_URL = "http://localhost:8010/";

$(document).ready(function () {
    fetchUserDetails();
    // $(document).on("click", "#logoutLink", function (event) {
    //   event.preventDefault();
    //   logout();
    // });
  });

function fetchUserDetails() {
    console.log("Fetching user details from:", API_URL + "Users/GetUserDetails");
    $.ajax({
      url: API_URL + "Users/GetUserDetails",
      type: "GET",
      xhrFields: {
        withCredentials: true, // Include cookies in the request
      },
      success: function (data) {
        console.log("User details fetched successfully:", data);
        $("#userName").text(data.FirstName + " " + data.LastName || "User Name");
        $("#userEmail").text(data.Email || "User Email");
      },
      error: function (xhr) {
        console.error("Failed to fetch user details:", xhr.responseJSON?.detail || xhr.statusText);
        console.log("Full error response:", xhr);
      },
    });
  }


// function logout() {
//   $.ajax({
//     url: API_URL + "Auth/logout", 
//     type: "POST",
//     xhrFields: {
//       withCredentials: true, 
//     },
//     success: function () {
//       alert("You have been logged out.");
//       window.location.href = "login.html"; // Redirect to the login page
//     },
//     error: function (xhr) {
//       console.error("Logout failed:", xhr.responseJSON?.detail || xhr.statusText);
//       alert("Failed to log out. Please try again.");
//     },
//   });
// }