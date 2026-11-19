// Email & Contact Finder
// ---------------------------------------------------------------------------
// The browser works through the list itself, sending one domain per request to
// /email-finder/scan. That keeps every request short (no host timeouts on long
// lists), gives an exact progress bar, and lets the visitor stop at any point
// without losing what has been found so far. The CSV is built here from the
// results already on screen, so downloading never re-runs the scan.
(function () {
  "use strict";

  var form = document.getElementById("ef-form");
  if (!form || !window.fetch) return;   // no fetch: the plain form POST fallback runs

  var CONCURRENCY = 3;
  var $ = function (id) { return document.getElementById(id); };
  var domainsEl = $("domains"), keywordsEl = $("keywords");
  var startBtn = $("ef-start"), stopBtn = $("ef-stop");
  var progress = $("ef-progress"), resultsCard = $("ef-results");
  var rowsEl = $("ef-rows"), emptyEl = $("ef-empty");

  var state = null;       // current run
  var results = [];       // [{index, domain, status, emails, pages, errors}]
  var filter = "all";

  // ── Input helpers ─────────────────────────────────────────────────────────
  function cleanDomains(text) {
    var seen = {}, out = [];
    text.split(/\r?\n/).forEach(function (line) {
      var d = line.trim().toLowerCase();
      if (!d) return;
      d = d.replace(/^[a-z]+:\/\//, "").split(/[\/?#\s,;]/)[0].replace(/\.$/, "");
      if (!d || d.indexOf(".") === -1) return;
      var key = d.replace(/^www\./, "");
      if (seen[key]) return;
      seen[key] = true;
      out.push(d);
    });
    return out;
  }

  function keywordList() {
    return keywordsEl.value.split(/\r?\n/).map(function (k) { return k.trim(); }).filter(Boolean);
  }

  function updateCounts() {
    var n = cleanDomains(domainsEl.value).length;
    $("ef-count").textContent = n ? n + (n === 1 ? " domain" : " domains") : "";
    $("ef-kw-count").textContent = "(" + keywordList().length + ")";
  }
  domainsEl.addEventListener("input", updateCounts);
  keywordsEl.addEventListener("input", updateCounts);
  $("ef-kw-reset").addEventListener("click", function () {
    keywordsEl.value = keywordsEl.dataset.default;
    updateCounts();
  });
  updateCounts();

  // ── Formatting ────────────────────────────────────────────────────────────
  function fmtTime(sec) {
    if (!isFinite(sec) || sec < 0) return "-";
    sec = Math.round(sec);
    if (sec < 60) return sec + "s";
    var m = Math.floor(sec / 60), s = sec % 60;
    if (m < 60) return m + "m " + (s < 10 ? "0" : "") + s + "s";
    return Math.floor(m / 60) + "h " + (m % 60) + "m";
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text != null) e.textContent = text;
    return e;
  }

  function kind(r) {
    if (r.status === "error") return "fail";
    return r.emails.length ? "hit" : "miss";
  }

  // ── Rendering ─────────────────────────────────────────────────────────────
  function renderRow(r) {
    var tr = el("tr");
    tr.dataset.kind = kind(r);
    tr.dataset.index = r.index;

    tr.appendChild(el("td", "num", String(r.index + 1)));

    var tdDomain = el("td", "ef-domain");
    var a = el("a", null, r.domain);
    a.href = "https://" + r.domain;
    a.target = "_blank";
    a.rel = "noopener nofollow";
    tdDomain.appendChild(a);
    tr.appendChild(tdDomain);

    var tdEmails = el("td", "ef-emails");
    if (r.emails.length) {
      r.emails.forEach(function (e) {
        var chip = el("a", "email-chip", e);
        chip.href = "mailto:" + e;
        tdEmails.appendChild(chip);
      });
    } else {
      tdEmails.appendChild(el("span", "muted", r.status === "error" ? "-" : "None found"));
    }
    tr.appendChild(tdEmails);

    var tdPages = el("td", "ef-pages");
    var withEmails = r.pages.filter(function (p) { return p.emails.length; });
    var list = withEmails.length ? withEmails : r.pages;
    if (!list.length) tdPages.appendChild(el("span", "muted", "-"));
    list.slice(0, 4).forEach(function (p) {
      var link = el("a", null, pathOf(p.url));
      link.href = p.url;
      link.target = "_blank";
      link.rel = "noopener nofollow";
      link.title = p.url;
      tdPages.appendChild(link);
    });
    if (list.length > 4) tdPages.appendChild(el("span", "muted", "+" + (list.length - 4) + " more"));
    tr.appendChild(tdPages);

    var tdStatus = el("td");
    if (r.status === "error") {
      var msg = r.errors.length ? r.errors[0].error : "Failed";
      var b = el("span", "badge badge-error", "Failed");
      tdStatus.appendChild(b);
      tdStatus.appendChild(el("div", "ef-err", msg));
    } else if (r.emails.length) {
      tdStatus.appendChild(el("span", "badge badge-ok", r.emails.length + (r.emails.length === 1 ? " email" : " emails")));
    } else {
      tdStatus.appendChild(el("span", "badge badge-warn", "No emails"));
    }
    tr.appendChild(tdStatus);
    return tr;
  }

  function pathOf(url) {
    try {
      var u = new URL(url);
      var p = u.pathname.replace(/\/$/, "");
      return p ? decodeURI(p) : "Homepage";
    } catch (e) { return url; }
  }

  function upsertRow(r) {
    var tr = renderRow(r);
    var existing = rowsEl.querySelector('tr[data-index="' + r.index + '"]');
    if (existing) {
      rowsEl.replaceChild(tr, existing);
    } else {
      // keep list order even though replies arrive out of order
      var after = null;
      Array.prototype.some.call(rowsEl.children, function (row) {
        if (+row.dataset.index > r.index) { after = row; return true; }
        return false;
      });
      rowsEl.insertBefore(tr, after);
    }
    applyFilter();
  }

  function applyFilter() {
    var shown = 0;
    Array.prototype.forEach.call(rowsEl.children, function (tr) {
      var show = filter === "all" || tr.dataset.kind === filter;
      tr.hidden = !show;
      if (show) shown++;
    });
    emptyEl.hidden = shown > 0;

    var counts = { all: 0, hit: 0, miss: 0, fail: 0 };
    results.forEach(function (r) { if (r) { counts.all++; counts[kind(r)]++; } });
    Array.prototype.forEach.call($("ef-filter").children, function (b) {
      b.querySelector("span").textContent = counts[b.dataset.f];
    });
    $("ef-retry").hidden = !counts.fail || !!(state && state.running);
  }

  $("ef-filter").addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b) return;
    filter = b.dataset.f;
    Array.prototype.forEach.call(this.children, function (x) {
      x.setAttribute("aria-selected", String(x === b));
    });
    applyFilter();
  });

  function uniqueEmails() {
    var set = {};
    results.forEach(function (r) { if (r) r.emails.forEach(function (e) { set[e] = true; }); });
    return Object.keys(set).sort();
  }

  function updateProgress() {
    var s = state;
    var done = s.done, total = s.queue.length;
    var pct = total ? Math.floor(done / total * 100) : 0;
    $("ef-fill").style.width = pct + "%";
    $("ef-bar").setAttribute("aria-valuenow", pct);
    $("ef-percent").textContent = pct + "%";

    var hits = 0, failed = 0;
    s.queue.forEach(function (i) {
      var r = results[i];
      if (!r) return;
      if (r.status === "error") failed++;
      else if (r.emails.length) hits++;
    });
    $("ef-s-done").textContent = done + " / " + total;
    $("ef-s-emails").textContent = uniqueEmails().length;
    $("ef-s-hits").textContent = hits;
    $("ef-s-failed").textContent = failed;

    var elapsed = (Date.now() - s.started) / 1000;
    var eta = done >= 2 ? elapsed / done * (total - done) : NaN;
    $("ef-s-eta").textContent = s.running ? fmtTime(eta) : "Done";

    var active = Object.keys(s.active).map(function (k) { return s.active[k]; });
    $("ef-current").textContent = s.running && active.length ? "Now scanning: " + active.join(", ") : "";

    if (s.running) {
      $("ef-status").textContent = "Scanning " + total + (total === 1 ? " domain" : " domains");
    } else if (s.stopped) {
      $("ef-status").textContent = "Stopped after " + done + " of " + total;
    } else {
      $("ef-status").textContent = "Finished in " + fmtTime(elapsed);
    }
    progress.classList.toggle("is-done", !s.running);
  }

  // ── Running a scan ────────────────────────────────────────────────────────
  function scanOne(index, keywords) {
    var domain = results[index] ? results[index].domain : state.domains[index];
    state.active[index] = domain;
    updateProgress();

    return fetch(window.EF_SCAN_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ domain: domain, keywords: keywords })
    })
      .then(function (res) {
        if (!res.ok) throw new Error("Server returned " + res.status);
        return res.json();
      })
      .catch(function (err) {
        return { domain: domain, status: "error", emails: [], pages: [],
                 errors: [{ url: domain, error: err.message || "Request failed" }] };
      })
      .then(function (r) {
        delete state.active[index];
        r.index = index;
        r.domain = domain;
        results[index] = r;
        state.done++;
        upsertRow(r);
        updateProgress();
      });
  }

  function run(indexes, keywords) {
    state.queue = indexes;
    state.done = 0;
    state.started = Date.now();
    state.running = true;
    state.stopped = false;
    state.active = {};
    var next = 0;

    progress.hidden = false;
    resultsCard.hidden = false;
    startBtn.disabled = true;
    startBtn.textContent = "Scanning…";
    stopBtn.hidden = false;
    updateProgress();

    function worker() {
      if (!state.running || next >= indexes.length) return Promise.resolve();
      var i = indexes[next++];
      return scanOne(i, keywords).then(worker);
    }

    var workers = [];
    for (var w = 0; w < Math.min(CONCURRENCY, indexes.length); w++) workers.push(worker());
    Promise.all(workers).then(finish);
  }

  function finish() {
    state.running = false;
    startBtn.disabled = false;
    startBtn.textContent = "Start scanning";
    stopBtn.hidden = true;
    updateProgress();
    applyFilter();
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (state && state.running) return;
    var domains = cleanDomains(domainsEl.value);
    if (!domains.length) {
      domainsEl.focus();
      $("ef-count").textContent = "Add at least one domain";
      return;
    }
    results = [];
    rowsEl.innerHTML = "";
    filter = "all";
    Array.prototype.forEach.call($("ef-filter").children, function (x) {
      x.setAttribute("aria-selected", String(x.dataset.f === "all"));
    });
    state = { domains: domains, keywords: keywordList() };
    run(domains.map(function (_, i) { return i; }), state.keywords);
    progress.scrollIntoView({ behavior: "smooth", block: "start" });
  });

  stopBtn.addEventListener("click", function () {
    if (!state || !state.running) return;
    state.running = false;      // workers finish their current domain, then stop
    state.stopped = true;
    stopBtn.hidden = true;
    startBtn.textContent = "Stopping…";
  });

  $("ef-retry").addEventListener("click", function () {
    if (!state || state.running) return;
    var failed = [];
    results.forEach(function (r) { if (r && r.status === "error") failed.push(r.index); });
    if (failed.length) run(failed, state.keywords);
  });

  window.addEventListener("beforeunload", function (e) {
    if (state && state.running) { e.preventDefault(); e.returnValue = ""; }
  });

  // ── Export ────────────────────────────────────────────────────────────────
  function flash(btn, text) {
    var original = btn.dataset.label || btn.textContent;
    btn.dataset.label = original;
    btn.textContent = text;
    setTimeout(function () { btn.textContent = original; }, 1600);
  }

  $("ef-copy").addEventListener("click", function () {
    var btn = this, text = uniqueEmails().join("\n");
    if (!text) { flash(btn, "No emails yet"); return; }
    var ok = function () { flash(btn, "Copied " + uniqueEmails().length); };
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(ok, function () { flash(btn, "Copy failed"); });
    } else {
      var ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); ok(); } catch (err) { flash(btn, "Copy failed"); }
      document.body.removeChild(ta);
    }
  });

  function csvCell(v) {
    v = v == null ? "" : String(v);
    return /[",\n\r]/.test(v) ? '"' + v.replace(/"/g, '""') + '"' : v;
  }

  $("ef-csv").addEventListener("click", function () {
    var lines = [["domain", "email", "found_on", "keyword", "status", "error"]];
    results.forEach(function (r) {
      if (!r) return;
      if (r.status === "error") {
        lines.push([r.domain, "", "", "", "failed", r.errors.length ? r.errors[0].error : ""]);
        return;
      }
      if (!r.emails.length) {
        lines.push([r.domain, "", "", "", "no emails", ""]);
        return;
      }
      r.emails.forEach(function (email) {
        var src = r.pages.filter(function (p) { return p.emails.indexOf(email) !== -1; })[0] || {};
        lines.push([r.domain, email, src.url || "", src.keyword || "", "found", ""]);
      });
    });
    var csv = lines.map(function (l) { return l.map(csvCell).join(","); }).join("\r\n");
    var blob = new Blob(["﻿" + csv], { type: "text/csv;charset=utf-8" });
    var a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "contact_emails_" + new Date().toISOString().slice(0, 10) + ".csv";
    document.body.appendChild(a);
    a.click();
    setTimeout(function () { URL.revokeObjectURL(a.href); a.remove(); }, 500);
  });
})();
