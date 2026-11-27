document.addEventListener("DOMContentLoaded", () => {
  // Manejo de tabs
  const tabBtns = document.querySelectorAll(".tab-btn");
  const tabPanes = document.querySelectorAll(".tab-pane");

  tabBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      tabBtns.forEach(b => b.classList.remove("active"));
      tabPanes.forEach(p => p.classList.remove("active"));

      btn.classList.add("active");
      const targetPane = document.getElementById(btn.dataset.tab);
      if (targetPane) {
        targetPane.classList.add("active");
      }
    });
  });

  // Verificación de salud del backend
  const statusDot = document.getElementById("api-status-dot");
  const statusText = document.getElementById("api-status-text");

  async function checkHealth() {
    try {
      const res = await fetch("http://localhost:8000/health");
      if (res.ok) {
        const data = await res.json();
        statusDot.classList.add("online");
        statusText.textContent = `API Online v${data.version}`;
      } else {
        statusText.textContent = "API Degradada";
      }
    } catch {
      statusText.textContent = "API Offline";
    }
  }

  checkHealth();
  setInterval(checkHealth, 30000);
});
