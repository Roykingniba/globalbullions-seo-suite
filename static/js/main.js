// ── Theme switch (Light / Auto / Dark) ───────────────────────────────────
// The stored value is applied by the inline script in <head> before first
// paint; this only wires up the control and keeps it in sync.
//
// "auto" is represented by the ABSENCE of data-theme, so the CSS media query
// governs. Storing an explicit "auto" string would still satisfy
// :not([data-theme="light"]) and silently break the light override.
(function () {
  var root = document.documentElement;
  var opts = Array.prototype.slice.call(document.querySelectorAll(".theme-opt"));
  if (!opts.length) return;

  var KEY = "kai-theme";

  function read() {
    try {
      var v = localStorage.getItem(KEY);
      return v === "light" || v === "dark" ? v : "auto";
    } catch (e) {
      return "auto";
    }
  }

  function paint(mode) {
    opts.forEach(function (b) {
      b.setAttribute("aria-checked", String(b.dataset.themeSet === mode));
    });
  }

  function apply(mode) {
    // Suppress transitions for one frame so switching is instant rather than
    // every surface cross-fading at a different rate.
    root.classList.add("theme-switching");

    if (mode === "auto") {
      root.removeAttribute("data-theme");
    } else {
      root.setAttribute("data-theme", mode);
    }

    try {
      if (mode === "auto") localStorage.removeItem(KEY);
      else localStorage.setItem(KEY, mode);
    } catch (e) {
      /* Storage unavailable — the choice still applies for this page view. */
    }

    paint(mode);
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        root.classList.remove("theme-switching");
      });
    });
  }

  opts.forEach(function (btn) {
    btn.addEventListener("click", function () {
      apply(btn.dataset.themeSet);
    });
    // Arrow-key navigation, expected of a radiogroup.
    btn.addEventListener("keydown", function (e) {
      var i = opts.indexOf(btn);
      var next = null;
      if (e.key === "ArrowRight" || e.key === "ArrowDown") next = opts[(i + 1) % opts.length];
      if (e.key === "ArrowLeft" || e.key === "ArrowUp") next = opts[(i - 1 + opts.length) % opts.length];
      if (!next) return;
      e.preventDefault();
      next.focus();
      apply(next.dataset.themeSet);
    });
  });

  paint(read());

  // Keep the control honest if the OS flips while we're on "auto", and pick up
  // a change made in another tab.
  if (window.matchMedia) {
    var mq = window.matchMedia("(prefers-color-scheme: dark)");
    var onChange = function () { if (read() === "auto") paint("auto"); };
    if (mq.addEventListener) mq.addEventListener("change", onChange);
    else if (mq.addListener) mq.addListener(onChange);
  }
  window.addEventListener("storage", function (e) {
    if (e.key !== KEY) return;
    var mode = read();
    if (mode === "auto") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", mode);
    paint(mode);
  });
})();

// ── "All tools" menu ─────────────────────────────────────────────────────
// One button opens the panel holding every category. On desktop the panel is
// a mega menu with every list visible; under 900px each category is a row
// that expands on tap. Closes on outside click, Escape, or picking a link.
const navToggle = document.querySelector(".nav-toggle");
const mainNav = document.querySelector(".main-nav");
const isMobileNav = () => window.matchMedia("(max-width: 900px)").matches;

function setNav(open) {
  if (!mainNav || !navToggle) return;
  mainNav.classList.toggle("open", open);
  navToggle.setAttribute("aria-expanded", String(open));
  if (open && isMobileNav()) {
    // Start with the current page's category expanded on phones.
    const current = mainNav.querySelector(".nav-item-current");
    if (current && !mainNav.querySelector(".nav-item-open")) {
      current.classList.add("nav-item-open");
      const t = current.querySelector(".nav-trigger");
      if (t) t.setAttribute("aria-expanded", "true");
    }
  }
}

if (navToggle && mainNav) {
  navToggle.addEventListener("click", (e) => {
    e.stopPropagation();
    setNav(!mainNav.classList.contains("open"));
  });
}

document.querySelectorAll(".nav-trigger").forEach((btn) => {
  btn.addEventListener("click", () => {
    if (!isMobileNav()) return;           // desktop: headings are labels only
    const item = btn.closest(".nav-item");
    const willOpen = !item.classList.contains("nav-item-open");
    item.classList.toggle("nav-item-open", willOpen);
    btn.setAttribute("aria-expanded", String(willOpen));
  });
});

document.addEventListener("click", (e) => {
  if (!mainNav || !mainNav.classList.contains("open")) return;
  if (!e.target.closest(".main-nav") && !e.target.closest(".nav-toggle")) setNav(false);
});

document.addEventListener("keydown", (e) => {
  if (e.key !== "Escape" || !mainNav || !mainNav.classList.contains("open")) return;
  setNav(false);
  navToggle.focus();
});

// ── Copy-to-clipboard buttons ────────────────────────────────────────────
// Used by the Text and Data Utilities output panels. Falls back to a hidden
// textarea + execCommand because navigator.clipboard is unavailable over
// plain HTTP and in some older mobile browsers.
document.querySelectorAll(".btn-copy").forEach(function (btn) {
  btn.addEventListener("click", function () {
    var target = document.getElementById(btn.dataset.copy);
    if (!target) return;
    var text = target.textContent;

    var done = function (ok) {
      var original = btn.dataset.label || btn.textContent;
      btn.dataset.label = original;
      btn.textContent = ok ? "Copied" : "Press Ctrl+C";
      btn.classList.toggle("copied", ok);
      setTimeout(function () {
        btn.textContent = btn.dataset.label;
        btn.classList.remove("copied");
      }, 1600);
    };

    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(function () { done(true); },
                                              function () { done(false); });
      return;
    }
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    var ok = false;
    try { ok = document.execCommand("copy"); } catch (e) { ok = false; }
    document.body.removeChild(ta);
    done(ok);
  });
});

// ── Homepage tool search ─────────────────────────────────────────────────
// Filters the directory client-side. With ~40 tools and growing, scanning
// nine category sections by eye is the main friction on this page.
const search = document.getElementById("tool-search");
if (search) {
  const cards = Array.from(document.querySelectorAll(".tool-card"));
  const sections = Array.from(document.querySelectorAll(".tool-category"));
  const chips = document.querySelector(".cat-chips");
  const empty = document.getElementById("search-empty");

  const apply = (raw) => {
    // Every whitespace-separated term must match, so "pdf merge" narrows
    // rather than widening the way a single-substring test would.
    const terms = raw.toLowerCase().trim().split(/\s+/).filter(Boolean);

    cards.forEach((card) => {
      const hay = card.dataset.name + " " + card.dataset.desc;
      card.classList.toggle("hidden", !terms.every((t) => hay.includes(t)));
    });

    // Hide a category heading once all of its cards are filtered out.
    sections.forEach((sec) => {
      const visible = sec.querySelectorAll(".tool-card:not(.hidden)").length;
      sec.classList.toggle("hidden", visible === 0);
    });

    const anyVisible = cards.some((c) => !c.classList.contains("hidden"));
    if (empty) empty.classList.toggle("show", !anyVisible);
    if (chips) chips.style.display = terms.length ? "none" : "";
  };

  let t;
  search.addEventListener("input", () => {
    clearTimeout(t);
    t = setTimeout(() => apply(search.value), 90);
  });

  search.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      search.value = "";
      apply("");
    }
  });

  const clear = document.getElementById("search-clear");
  if (clear) {
    clear.addEventListener("click", (e) => {
      e.preventDefault();
      search.value = "";
      apply("");
      search.focus();
    });
  }
}
