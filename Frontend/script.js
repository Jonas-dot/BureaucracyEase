document.getElementById("fetchBtn").addEventListener("click", async function () {
  const response = await fetch("http://127.0.0.1:5000/appointments");
  const data = await response.json();

  let resultList = document.getElementById("results");
  resultList.innerHTML = "";

  data.forEach((item) => {
    let li = document.createElement("li");
    li.textContent = `${item[1]} (Number: ${item[0]}, Status: ${item[2]}, Additional Info: ${item[3]})`;
    resultList.appendChild(li);
  });
});

document.getElementById("scrapeBtn").addEventListener("click", async function () {
  await fetch("http://127.0.0.1:5000/scrape", { method: "POST" });
  alert("Scraping started. Please wait a few moments and then fetch the appointments.");
});

// WebSocket connection to get real-time updates
const socket = io.connect("http://127.0.0.1:5000");

socket.on("appointments_update", function (data) {
  console.log("Appointments updated:", data);
  // Update the UI with the new appointment data
});
