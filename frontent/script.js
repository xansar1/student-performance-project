async function loadData() {
  const res = await fetch("http://localhost:8000/analytics/kpis");
  const data = await res.json();

  document.getElementById("students").innerText = data.total_students;
  document.getElementById("avg").innerText = data.avg_score;
  document.getElementById("top").innerText = data.top_score;
  document.getElementById("risk").innerText = data.at_risk;
}
