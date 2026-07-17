/* Isiro — frontend interactions: loading states, sidebar, charts, forms */

document.addEventListener("DOMContentLoaded", function () {

    // --- Navbar scroll shadow on landing page ---
    const nav = document.querySelector(".landing-nav");
    if (nav) {
        window.addEventListener("scroll", () => {
            nav.classList.toggle("scrolled", window.scrollY > 10);
        });
    }

    // --- Mobile sidebar toggle ---
    const menuToggle = document.querySelector(".menu-toggle");
    const sidebar = document.querySelector(".sidebar");
    if (menuToggle && sidebar) {
        menuToggle.addEventListener("click", () => sidebar.classList.toggle("open"));
        // Close sidebar when clicking outside on mobile
        document.addEventListener("click", (e) => {
            if (window.innerWidth <= 768 &&
                !sidebar.contains(e.target) &&
                !menuToggle.contains(e.target) &&
                sidebar.classList.contains("open")) {
                sidebar.classList.remove("open");
            }
        });
    }

    // --- Button loading state on form submit ---
    document.querySelectorAll("form").forEach(form => {
        form.addEventListener("submit", function () {
            const btn = form.querySelector("button[type='submit']");
            if (btn && !btn.disabled) {
                btn.classList.add("loading");
                // Re-enable after 10s in case of error
                setTimeout(() => btn.classList.remove("loading"), 10000);
            }
        });
    });

    // --- Auto-dismiss alerts after 5 seconds ---
    document.querySelectorAll(".alert").forEach(alert => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.5s, transform 0.5s";
            alert.style.opacity = "0";
            alert.style.transform = "translateY(-10px)";
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // --- Filter button active state ---
    document.querySelectorAll(".filter-group .filter-btn").forEach(btn => {
        btn.addEventListener("click", function () {
            this.parentElement.querySelectorAll(".filter-btn")
                .forEach(b => b.classList.remove("active"));
            this.classList.add("active");
        });
    });

    // --- Import preview: remove row ---
    document.querySelectorAll(".row-remove").forEach(btn => {
        btn.addEventListener("click", function () {
            const row = this.closest("tr");
            row.style.transition = "opacity 0.3s, transform 0.3s";
            row.style.opacity = "0";
            row.style.transform = "translateX(-20px)";
            setTimeout(() => row.remove(), 300);
        });
    });

    // --- File upload drag & drop ---
    const uploadArea = document.querySelector(".upload-area");
    if (uploadArea) {
        const fileInput = uploadArea.querySelector("input[type='file']");
        uploadArea.addEventListener("dragover", (e) => {
            e.preventDefault();
            uploadArea.classList.add("drag-over");
        });
        uploadArea.addEventListener("dragleave", () => uploadArea.classList.remove("drag-over"));
        uploadArea.addEventListener("drop", (e) => {
            e.preventDefault();
            uploadArea.classList.remove("drag-over");
            if (e.dataTransfer.files.length) fileInput.files = e.dataTransfer.files;
        });
    }

    // --- Render charts if Chart.js is loaded ---
    if (typeof Chart !== "undefined") {
        renderCharts();
    }
});

// --- Loading overlay helpers ---
function showLoading(msg) {
    const overlay = document.getElementById("loading-overlay");
    if (overlay) {
        if (msg) overlay.querySelector("p").textContent = msg;
        overlay.classList.add("show");
    }
}
function hideLoading() {
    const overlay = document.getElementById("loading-overlay");
    if (overlay) overlay.classList.remove("show");
}

// --- Chart rendering ---
function renderCharts() {
    const pieEl = document.getElementById("pieChart");
    const lineEl = document.getElementById("lineChart");
    const barEl = document.getElementById("barChart");
    const reportPieEl = document.getElementById("reportPieChart");
    const reportBarEl = document.getElementById("reportBarChart");

    const chartDefaults = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: "bottom",
                labels: { font: { family: "Inter", size: 12 }, padding: 16 }
            }
        }
    };

    // Pie chart — expense by category
    if (pieEl) {
        const data = JSON.parse(pieEl.dataset.chart || "{}");
        new Chart(pieEl, {
            type: "doughnut",
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.values || [],
                    backgroundColor: data.colors || ["#4F46E5","#10B981","#EF4444","#F59E0B","#0EA5E9","#8B5CF6"],
                    borderWidth: 2,
                    borderColor: "#fff",
                }]
            },
            options: { ...chartDefaults, cutout: "65%" }
        });
    }

    // Line chart — monthly spending
    if (lineEl) {
        const data = JSON.parse(lineEl.dataset.chart || "{}");
        new Chart(lineEl, {
            type: "line",
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: "Monthly Expenses",
                    data: data.values || [],
                    borderColor: "#4F46E5",
                    backgroundColor: "rgba(79,70,229,0.1)",
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: "#4F46E5",
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    borderWidth: 3,
                }]
            },
            options: {
                ...chartDefaults,
                scales: {
                    y: { beginAtZero: true, grid: { color: "#F3F4F6" } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // Bar chart — weekly expenses
    if (barEl) {
        const data = JSON.parse(barEl.dataset.chart || "{}");
        new Chart(barEl, {
            type: "bar",
            data: {
                labels: data.labels || [],
                datasets: [{
                    label: "Weekly Expenses",
                    data: data.values || [],
                    backgroundColor: "#10B981",
                    borderRadius: 8,
                    barThickness: "flex",
                    maxBarThickness: 50,
                }]
            },
            options: {
                ...chartDefaults,
                scales: {
                    y: { beginAtZero: true, grid: { color: "#F3F4F6" } },
                    x: { grid: { display: false } }
                }
            }
        });
    }

    // Report pie chart
    if (reportPieEl) {
        const data = JSON.parse(reportPieEl.dataset.chart || "{}");
        new Chart(reportPieEl, {
            type: "doughnut",
            data: {
                labels: data.labels || [],
                datasets: [{
                    data: data.values || [],
                    backgroundColor: data.colors || ["#4F46E5","#10B981","#EF4444","#F59E0B"],
                    borderWidth: 2, borderColor: "#fff",
                }]
            },
            options: { ...chartDefaults, cutout: "60%" }
        });
    }

    // Report bar chart — income vs expense
    if (reportBarEl) {
        const data = JSON.parse(reportBarEl.dataset.chart || "{}");
        new Chart(reportBarEl, {
            type: "bar",
            data: {
                labels: ["Income", "Expenses"],
                datasets: [{
                    label: "Amount",
                    data: data.values || [0, 0],
                    backgroundColor: ["#10B981", "#EF4444"],
                    borderRadius: 8,
                    barThickness: 80,
                }]
            },
            options: {
                ...chartDefaults,
                scales: {
                    y: { beginAtZero: true, grid: { color: "#F3F4F6" } },
                    x: { grid: { display: false } }
                },
                plugins: { legend: { display: false } }
            }
        });
    }
}
