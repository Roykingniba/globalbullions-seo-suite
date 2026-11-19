(function () {
  const contentEl = document.getElementById("grader-content");
  const keywordEl = document.getElementById("grader-keyword");
  const titleEl = document.getElementById("grader-title");
  const secondaryEl = document.getElementById("grader-secondary");
  if (!contentEl) return;

  let debounceTimer = null;

  function debounce(fn, delay) {
    return function (...args) {
      clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => fn(...args), delay);
    };
  }

  function statusIcon(status) {
    if (status === "pass") return "✓";
    if (status === "warn") return "!";
    return "✕";
  }

  function render(data) {
    document.getElementById("grader-score").textContent = data.score;
    document.getElementById("grader-wordcount").textContent = data.word_count;
    document.getElementById("grader-headingcount").textContent = data.heading_count;
    document.getElementById("grader-density").textContent = data.keyword_density_pct + "%";
    document.getElementById("grader-kwcount").textContent = data.keyword_count;
    document.getElementById("grader-readability").textContent =
      (data.readability && data.readability.label) || "–";

    const checklist = document.getElementById("grader-checklist");
    checklist.innerHTML = "";
    (data.checklist || []).forEach((item) => {
      const row = document.createElement("div");
      row.className = "checklist-item";
      row.innerHTML =
        '<span class="checklist-icon ' + item.status + '">' + statusIcon(item.status) + "</span>" +
        '<div><div class="checklist-label">' + escapeHtml(item.label) + "</div>" +
        (item.detail ? '<div class="checklist-detail">' + escapeHtml(item.detail) + "</div>" : "") +
        "</div>";
      checklist.appendChild(row);
    });

    const suggestions = document.getElementById("grader-suggestions");
    suggestions.innerHTML = "";
    (data.suggested_keywords || []).forEach((kw) => {
      const span = document.createElement("span");
      span.textContent = kw;
      suggestions.appendChild(span);
    });
    if (!data.suggested_keywords || data.suggested_keywords.length === 0) {
      suggestions.innerHTML = '<span style="background:none;color:var(--text-dim);padding:0;">Add more content to see suggestions.</span>';
    }
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }

  async function gradeNow() {
    const payload = {
      content: contentEl.value,
      keyword: keywordEl.value,
      title: titleEl.value,
      secondary: secondaryEl.value,
    };
    try {
      const resp = await fetch(window.gradeEndpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      render(data);
    } catch (e) {
      // silently ignore transient network errors during live typing
    }
  }

  const debouncedGrade = debounce(gradeNow, 500);

  [contentEl, keywordEl, titleEl, secondaryEl].forEach((el) => {
    el.addEventListener("input", debouncedGrade);
  });

  // Fetch an existing page's text to grade instead of writing from scratch.
  const fetchBtn = document.getElementById("grader-fetch-btn");
  const urlInput = document.getElementById("grader-url");
  const errorBox = document.getElementById("grader-fetch-error");
  if (fetchBtn) {
    fetchBtn.addEventListener("click", async () => {
      errorBox.style.display = "none";
      fetchBtn.disabled = true;
      fetchBtn.textContent = "Fetching...";
      try {
        const resp = await fetch(window.fetchEndpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: urlInput.value }),
        });
        const data = await resp.json();
        if (!resp.ok) {
          errorBox.textContent = data.error || "Couldn't fetch that page.";
          errorBox.style.display = "block";
        } else {
          titleEl.value = data.title || "";
          contentEl.value = data.content || "";
          gradeNow();
        }
      } catch (e) {
        errorBox.textContent = "Couldn't fetch that page.";
        errorBox.style.display = "block";
      } finally {
        fetchBtn.disabled = false;
        fetchBtn.textContent = "Fetch page text";
      }
    });
  }

  gradeNow();
})();
