async function loadDashboard() {
  const res = await fetch("https://ai-academic-backend.onrender.com/analytics/kpis");
  const data = await res.json();

  // Update KPI
  document.getElementById("students").innerText = data.total_students;
  document.getElementById("avg").innerText = data.avg_score;
  document.getElementById("top").innerText = data.top_score;
  document.getElementById("risk").innerText = data.at_risk;

  // Fake student data (demo)
  const students = [
    { name: "Ameen", score: 78, risk: "Low" },
    { name: "Fathima", score: 88, risk: "Low" },
    { name: "Rahul", score: 45, risk: "High" }
  ];

  // Table
  const tbody = document.querySelector("#studentTable tbody");
  tbody.innerHTML = "";

  students.forEach(s => {
    const row = `
      <tr>
        <td>${s.name}</td>
        <td>${s.score}</td>
        <td style="color:${s.risk === "High" ? "red" : "lightgreen"}">${s.risk}</td>
      </tr>
    `;
    tbody.innerHTML += row;
  });

  // Charts
  renderCharts();
}

function renderCharts() {
  const ctx1 = document.getElementById("barChart");
  const ctx2 = document.getElementById("lineChart");

  new Chart(ctx1, {
    type: 'bar',
    data: {
      labels: ['Physics', 'Chemistry', 'Math'],
      datasets: [{
        label: 'Scores',
        data: [78, 85, 90]
      }]
    }
  });

  new Chart(ctx2, {
    type: 'line',
    data: {
      labels: ['Test 1', 'Test 2', 'Test 3'],
      datasets: [{
        label: 'Progress',
        data: [60, 75, 85]
      }]
    }
  });
}
