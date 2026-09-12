(function () {
  const datasets = window.DATASETS || [];
  const grid = document.querySelector("#dataset-grid");
  const search = document.querySelector("#dataset-search");
  const count = document.querySelector("#dataset-count");
  const caseTotal = document.querySelector("#case-total");

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

  if (search) {
    search.addEventListener("input", (event) => {
      const query = event.target.value.toLowerCase().trim();
      const filtered = datasets.filter((dataset) =>
        JSON.stringify(dataset).toLowerCase().includes(query)
      );
      render(filtered);
    });
  }

  render(datasets);
})();
