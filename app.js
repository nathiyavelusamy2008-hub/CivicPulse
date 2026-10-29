const $ = (id) => document.getElementById(id);
const API = "/api";
let toastTimer;

const categoryIcons = {
  "Water & Sanitation": "💧", "Roads & Potholes": "🛣️",
  "Waste Management": "♻️", "Street Lighting": "💡",
  "Public Safety": "🛡️", "Parks & Public Spaces": "🌳", "Other": "📍"
};

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, c => ({
    "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#39;"
  })[c]);
}
function showToast(message) {
  const el = $("toast");
  el.textContent = message;
  el.classList.add("show");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove("show"), 2600);
}
async function request(url, options = {}) {
  const response = await fetch(url, {
    headers: {"Content-Type":"application/json", ...(options.headers || {})},
    ...options
  });
  if (!response.ok) {
    let message = "Something went wrong.";
    try { const data = await response.json(); message = data.detail || message; } catch {}
    throw new Error(message);
  }
  return response.json();
}
function statusClass(status) { return "status-" + status.replace(/\s+/g, "-"); }
function renderIssue(issue) {
  const duplicates = issue.possible_duplicates || [];
  return `
  <article class="issue-card">
    <div class="issue-top">
      <div class="category-icon">${categoryIcons[issue.category] || "📍"}</div>
      <div class="issue-main">
        <h3>${escapeHtml(issue.title)}</h3>
        <div class="issue-location"><span>⌖</span>${escapeHtml(issue.location)} · ${escapeHtml(issue.category)}</div>
      </div>
      <span class="priority-pill priority-${escapeHtml(issue.priority_label)}">${escapeHtml(issue.priority_label)}</span>
    </div>
    <p class="issue-description">${escapeHtml(issue.description)}</p>
    <div class="issue-meta">
      <span class="score">Priority <b>${issue.priority_score}</b><span>/100</span></span>
      <span class="status-pill ${statusClass(issue.status)}">${escapeHtml(issue.status)}</span>
      <div class="issue-actions">
        <select aria-label="Update status for ${escapeHtml(issue.title)}" data-status-id="${issue.id}">
          <option ${issue.status==="Reported"?"selected":""}>Reported</option>
          <option ${issue.status==="In Progress"?"selected":""}>In Progress</option>
          <option ${issue.status==="Resolved"?"selected":""}>Resolved</option>
        </select>
      </div>
    </div>
    ${duplicates.length ? `<div class="duplicate-note">⚠ Possible similar report${duplicates.length>1?"s":""}: #${duplicates.join(", #")}. Review before creating duplicate work.</div>` : ""}
    <details class="reasons"><summary>Why this priority score?</summary><ul>${issue.priority_reasons.map(r=>`<li>${escapeHtml(r)}</li>`).join("")}</ul></details>
  </article>`;
}
async function loadAnalytics() {
  const data = await request(`${API}/analytics`);
  $("stat-total").textContent = data.total;
  $("stat-open").textContent = data.open;
  $("stat-high").textContent = data.high_priority;
  $("stat-rate").innerHTML = `${data.resolution_rate}<small>%</small>`;
}
async function loadIssues() {
  const params = new URLSearchParams();
  if ($("search").value.trim()) params.set("search", $("search").value.trim());
  params.set("category", $("category-filter").value);
  params.set("priority", $("priority-filter").value);
  params.set("status", $("status-filter").value);
  const issues = await request(`${API}/issues?${params.toString()}`);
  $("visible-count").textContent = `${issues.length} report${issues.length===1?"":"s"}`;
  $("issues-list").innerHTML = issues.length
    ? issues.map(renderIssue).join("")
    : `<div class="empty-state"><b>No matching reports</b>Try changing your filters, or submit a new community issue.</div>`;
}
async function refresh() {
  try {
    await Promise.all([loadAnalytics(), loadIssues()]);
  } catch (error) {
    $("issues-list").innerHTML = `<div class="empty-state"><b>Could not connect to the backend</b>${escapeHtml(error.message)}<br>Make sure the server is running at http://127.0.0.1:8000.</div>`;
  }
}
let searchDebounce;
$("search").addEventListener("input", () => {
  clearTimeout(searchDebounce);
  searchDebounce = setTimeout(loadIssues, 220);
});
["category-filter","priority-filter","status-filter"].forEach(id => $(id).addEventListener("change", loadIssues));

$("issues-list").addEventListener("change", async event => {
  const select = event.target.closest("[data-status-id]");
  if (!select) return;
  const id = select.dataset.statusId;
  try {
    await request(`${API}/issues/${id}`, {
      method:"PATCH", body:JSON.stringify({status:select.value})
    });
    showToast(`Report #${id} updated to ${select.value}.`);
    await refresh();
  } catch (error) {
    showToast(error.message);
    await loadIssues();
  }
});

$("issue-form").addEventListener("submit", async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const message = $("form-message");
  const button = form.querySelector("button[type=submit]");
  const values = Object.fromEntries(new FormData(form).entries());
  values.affected_people = Number(values.affected_people);
  button.disabled = true;
  button.textContent = "Submitting report…";
  message.className = "";
  message.textContent = "";
  try {
    const created = await request(`${API}/issues`, {
      method:"POST", body:JSON.stringify(values)
    });
    message.className = "success";
    message.textContent = `Report #${created.id} submitted. Priority: ${created.priority_label} (${created.priority_score}/100).`;
    form.reset();
    form.elements.severity.value = "Medium";
    form.elements.affected_people.value = 10;
    await refresh();
    showToast("Community report submitted successfully.");
    $("reports").scrollIntoView({behavior:"smooth", block:"start"});
  } catch (error) {
    message.className = "error";
    message.textContent = error.message;
  } finally {
    button.disabled = false;
    button.innerHTML = 'Submit community report <span>→</span>';
  }
});

refresh();
