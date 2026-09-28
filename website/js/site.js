(function () {
  const page = document.body.dataset.page;
  if (!page) return;
  document.querySelectorAll(".nav-links a[data-page]").forEach((link) => {
    if (link.dataset.page === page) {
      link.setAttribute("aria-current", "page");
    }
  });

  const sidebarLinks = Array.from(document.querySelectorAll(".page-sidebar a[href^='#']"));
  if (!sidebarLinks.length) return;

  const sections = sidebarLinks
    .map((link) => {
      const id = decodeURIComponent(link.getAttribute("href").slice(1));
      const target = document.getElementById(id);
      return target ? { link, target } : null;
    })
    .filter(Boolean);

  if (!sections.length) return;

  function setActive(activeLink) {
    sidebarLinks.forEach((link) => {
      const isActive = link === activeLink;
      link.classList.toggle("is-active", isActive);
      if (isActive) {
        link.setAttribute("aria-current", "true");
      } else {
        link.removeAttribute("aria-current");
      }
    });
  }

  function updateSidebarActive() {
    const navHeight = parseFloat(getComputedStyle(document.documentElement).getPropertyValue("--nav-height")) || 0;
    const threshold = navHeight + 54;
    let active = sections[0];

    sections.forEach((section) => {
      if (section.target.getBoundingClientRect().top <= threshold) {
        active = section;
      }
    });

    setActive(active.link);
  }

  let ticking = false;
  function requestUpdate() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(() => {
      updateSidebarActive();
      ticking = false;
    });
  }

  sidebarLinks.forEach((link) => {
    link.addEventListener("click", () => {
      window.setTimeout(updateSidebarActive, 80);
    });
  });

  window.addEventListener("scroll", requestUpdate, { passive: true });
  window.addEventListener("resize", requestUpdate);
  updateSidebarActive();
})();
