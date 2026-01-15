let sentimentChart = null;
let themeChart = null;
let currentPid = null;

async function loadProducts() {
  const res = await fetch("/api/products");
  const products = await res.json();
  const sel = document.getElementById("product");

  sel.innerHTML = "";
  products.forEach(p => {
    const o = document.createElement("option");
    o.value = p.sku;
    o.textContent = p.name;
    o.dataset.id = p.id;
    sel.appendChild(o);
  });

  currentPid = products[0].id;
  loadStats(currentPid);
  loadFeedbackTable(currentPid);

  sel.onchange = () => {
    currentPid = sel.selectedOptions[0].dataset.id;
    loadStats(currentPid);
    loadFeedbackTable(currentPid);
    clearInsights();
  };
}

async function submitFeedback() {
  await fetch("/api/feedback", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify({
      product_sku: product.value,
      rating: rating.value,
      text: text.value
    })
  });

  
  showSubmitStatus();

  loadStats(currentPid);
  loadFeedbackTable(currentPid);
  clearInsights();
}

function showSubmitStatus() {
  const s = document.getElementById("submitStatus");
  s.style.display = "block";
  setTimeout(() => {
    s.style.display = "none";
  }, 3000);
}

async function loadStats(pid) {
  const d = await fetch(`/api/stats/${pid}`).then(r => r.json());

  if (sentimentChart) sentimentChart.destroy();
  if (themeChart) themeChart.destroy();

  
  sentimentChart = new Chart(document.getElementById("sentimentChart"), {
    type: "pie",
    data: {
      labels: ["Positive", "Negative"],
      datasets: [{
        data: [
          d.sentiments.positive,
          d.sentiments.negative
        ],
        backgroundColor: ["#ff6384", "#36a2eb"]
      }]
    }
  });

  themeChart = new Chart(document.getElementById("themeChart"), {
    type: "bar",
    data: {
      labels: Object.keys(d.themes),
      datasets: [{
        label: "Mentions",
        data: Object.values(d.themes),
        backgroundColor: "#4dabf7"
      }]
    }
  });
}

async function generateInsights() {
  const ins = await fetch(`/api/insights/${currentPid}`).then(r => r.json());
  const ul = document.getElementById("insights");
  ul.innerHTML = "";

  ins.forEach(i => {
    const li = document.createElement("li");
    li.textContent = i;
    ul.appendChild(li);
  });
}

async function loadFeedbackTable(pid) {
  const rows = await fetch(`/api/feedback/${pid}`).then(r => r.json());
  const tbody = document.getElementById("feedbackTable");
  tbody.innerHTML = "";

  rows.forEach(f => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${f.rating}</td>
      <td>${f.sentiment}</td>
      <td>${f.text}</td>
    `;
    tbody.appendChild(tr);
  });
}

function clearInsights() {
  document.getElementById("insights").innerHTML = "";
}

loadProducts();
