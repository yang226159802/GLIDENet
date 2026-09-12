(function () {
  const page = document.body.dataset.page;
  if (!page) return;
  document.querySelectorAll(".nav-links a[data-page]").forEach((link) => {
    if (link.dataset.page === page) {
      link.setAttribute("aria-current", "page");
    }
  });
})();
