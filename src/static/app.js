document.addEventListener("DOMContentLoaded", () => {
  loadActivities();
  setupFormListener();
});

function loadActivities() {
  // Fetch activities from your backend
  fetch("/api/activities")
    .then((response) => response.json())
    .then((activities) => {
      renderActivities(activities);
      populateActivitySelect(activities);
    })
    .catch((error) => console.error("Error loading activities:", error));
}

function renderActivities(activities) {
  const template = document.getElementById("activity-card-template");
  const activitiesList = document.getElementById("activities-list");
  activitiesList.innerHTML = "";

  activities.forEach((activity) => {
    const card = template.content.cloneNode(true);
    card.querySelector("h4").textContent = activity.name;
    card.querySelector("p").textContent = activity.description;

    const participantsList = card.querySelector(".participants-list");
    if (activity.participants && activity.participants.length > 0) {
      participantsList.innerHTML = activity.participants
        .map((participant) => `<li>${participant}</li>`)
        .join("");
    } else {
      participantsList.innerHTML = `<li class="no-participants">No participants yet</li>`;
    }

    activitiesList.appendChild(card);
  });
}

function populateActivitySelect(activities) {
  const select = document.getElementById("activity");
  activities.forEach((activity) => {
    const option = document.createElement("option");
    option.value = activity.id;
    option.textContent = activity.name;
    select.appendChild(option);
  });
}

function setupFormListener() {
  const form = document.getElementById("signup-form");
  form.addEventListener("submit", handleSignup);
}

function handleSignup(e) {
  e.preventDefault();
  const email = document.getElementById("email").value;
  const activityId = document.getElementById("activity").value;
  const messageDiv = document.getElementById("message");

  fetch("/api/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, activityId }),
  })
    .then((response) => response.json())
    .then((data) => {
      messageDiv.className = "message success";
      messageDiv.textContent = "Successfully signed up!";
      loadActivities();
      form.reset();
    })
    .catch((error) => {
      messageDiv.className = "message error";
      messageDiv.textContent = "Error signing up. Please try again.";
    });
}
