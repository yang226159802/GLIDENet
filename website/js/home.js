(function () {
  const datasets = window.DATASETS || [];
  const caseCount = document.querySelector("#home-case-count");
  const totalData = document.querySelector("#home-total-data");
  const datasetCount = document.querySelector("#dataset-count");
  const caseTotal = document.querySelector("#case-total");
  const previewLink = document.querySelector("#home-preview-link");
  const previewImage = document.querySelector("#home-preview-image");
  const previewPlaceholder = document.querySelector("#home-preview-placeholder");
  const previewTitle = document.querySelector("#home-preview-title");
  const previousButton = document.querySelector(".preview-prev");
  const nextButton = document.querySelector(".preview-next");
  let currentIndex = 0;
  let timer = null;

  function parseGigabytes(size) {
    const text = String(size || "").toLowerCase();
    const match = text.match(/([\d.]+)/);
    if (!match) return 0;
    const value = Number.parseFloat(match[1]);
    if (!Number.isFinite(value)) return 0;
    if (text.includes("tb")) return value * 1024;
    if (text.includes("mb")) return value / 1024;
    return value;
  }

  function formatCaseCount(value) {
    return String(Math.max(0, value)).padStart(3, "0");
  }

  function formatTotalData(value) {
    return String(Math.round(Math.max(0, value))).padStart(6, "0");
  }

  function renderBoxes(value, options) {
    const text = String(value);
    const groups = text.replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    const boxes = Array.from(groups)
      .map((character) => {
        if (character === ",") return '<span class="stat-comma">,</span>';
        return '<span class="stat-box">' + character + "</span>";
      })
      .join("");
    const suffix = options && options.suffix
      ? '<span class="stat-box stat-unit">' + options.suffix + "</span>"
      : "";
    return boxes + suffix;
  }

  function setStats() {
    const cases = datasets.reduce((sum, dataset) => sum + (dataset.caseCount || 1), 0);
    const gigabytes = datasets.reduce((sum, dataset) => sum + parseGigabytes(dataset.size), 0);
    if (caseCount) caseCount.innerHTML = renderBoxes(formatCaseCount(cases));
    if (totalData) totalData.innerHTML = renderBoxes(formatTotalData(gigabytes), { suffix: "GB" });
    if (datasetCount) datasetCount.textContent = String(datasets.length);
    if (caseTotal) caseTotal.textContent = String(cases);
  }

  function showDataset(index) {
    if (!datasets.length || !previewLink || !previewTitle) return;
    currentIndex = (index + datasets.length) % datasets.length;
    const dataset = datasets[currentIndex];
    previewLink.href = dataset.detailUrl || "datasets.html";
    previewTitle.textContent = dataset.title || "Dataset";

    if (previewImage && previewPlaceholder) {
      if (dataset.imageUrl) {
        previewImage.src = dataset.imageUrl;
        previewImage.alt = dataset.title || "Dataset preview";
        previewImage.hidden = false;
        previewPlaceholder.hidden = true;
      } else {
        previewImage.hidden = true;
        previewPlaceholder.hidden = false;
      }
    }
  }

  function next() {
    showDataset(currentIndex + 1);
  }

  function previous() {
    showDataset(currentIndex - 1);
  }

  function restartTimer() {
    if (timer) window.clearInterval(timer);
    if (datasets.length > 1) {
      timer = window.setInterval(next, 3000);
    }
  }

  if (nextButton) {
    nextButton.addEventListener("click", () => {
      next();
      restartTimer();
    });
  }

  if (previousButton) {
    previousButton.addEventListener("click", () => {
      previous();
      restartTimer();
    });
  }

  setStats();
  showDataset(0);
  restartTimer();
})();
