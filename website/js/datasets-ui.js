(function () {
  const datasets = window.DATASETS || [];
  const grid = document.querySelector("#dataset-grid");
  const search = document.querySelector("#dataset-search");
  const filterButtons = document.querySelectorAll("[data-filter-group]");
  const count = document.querySelector("#dataset-count");
  const caseTotal = document.querySelector("#case-total");
  const state = {
    query: "",
    dimension: "",
    hosting: ""
  };

  if (count) count.textContent = String(datasets.length);
  if (caseTotal) {
    const total = datasets.reduce((sum, dataset) => sum + (dataset.caseCount || 1), 0);
    caseTotal.textContent = String(total);
  }

  function caseLabel(countValue) {
    const n = countValue || 1;
    return n > 1 ? n + " cases" : "1 case";
  }

  function imageMarkup(dataset) {
    if (!dataset.imageUrl) {
      return '<div class="image-placeholder" aria-hidden="true"></div>';
    }
    return '<img src="' + dataset.imageUrl + '" alt="' + dataset.title + '" />';
  }

  function render(items) {
    if (!grid) return;
    grid.innerHTML = items
      .map((dataset) => {
        return [
          '<article class="dataset-tile">',
          '  <a href="' + dataset.detailUrl + '">',
          imageMarkup(dataset),
          '    <h3>' + dataset.title + '</h3>',
          '  </a>',
          '  <div class="dataset-meta">' + caseLabel(dataset.caseCount) + '</div>',
          '</article>'
        ].join("");
      })
      .join("");
  }

  function normalizedHosting(dataset) {
    const platform = String(dataset.hostingPlatform || "").toLowerCase();
    if (platform.includes("kaggle")) return "kaggle";
    if (platform.includes("modelscope")) return "modelscope";
    return "other";
  }

  function matchesFilters(dataset) {
    const dimension = String(dataset.dimension || "").replace(/d$/i, "");
    const matchesDimension = !state.dimension || dimension === state.dimension;
    const matchesHosting = !state.hosting || normalizedHosting(dataset) === state.hosting;
    const matchesSearch = !state.query || JSON.stringify(dataset).toLowerCase().includes(state.query);
    return matchesDimension && matchesHosting && matchesSearch;
  }

  function applyFilters() {
    render(datasets.filter(matchesFilters));
  }

  function resetFilters() {
    state.dimension = "";
    state.hosting = "";
    filterButtons.forEach((button) => button.classList.remove("is-active"));
    const showAll = document.querySelector('[data-filter-group="all"]');
    if (showAll) showAll.classList.add("is-active");
  }

  if (search) {
    search.addEventListener("input", (event) => {
      state.query = event.target.value.toLowerCase().trim();
      applyFilters();
    });
  }

  filterButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const group = button.dataset.filterGroup;
      const value = button.dataset.filterValue || "";
      if (group === "all") {
        resetFilters();
        applyFilters();
        return;
      }
      state[group] = state[group] === value ? "" : value;
      document.querySelectorAll('[data-filter-group="' + group + '"]').forEach((peer) => {
        peer.classList.toggle("is-active", peer === button && state[group] === value);
      });
      const showAll = document.querySelector('[data-filter-group="all"]');
      if (showAll) showAll.classList.toggle("is-active", !state.dimension && !state.hosting);
      applyFilters();
    });
  });

  applyFilters();
})();
