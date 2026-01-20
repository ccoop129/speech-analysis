// Entities and Noun Phrases Data
const nounPhrasesData = {
  china: [
    { label: "development", count: 4902, width: 100 },
    { label: "cooperation", count: 4877, width: 99.49 },
    { label: "world", count: 4195, width: 85.56 },
    { label: "people", count: 3399, width: 69.34 },
    { label: "peace", count: 2550, width: 52.00 },
    { label: "country", count: 2109, width: 43.03 },
    { label: "africa", count: 1725, width: 35.21 },
    { label: "stability", count: 1629, width: 33.24 },
    { label: "develop country", count: 1523, width: 31.07 },
    { label: "reform", count: 1273, width: 25.96 },

  ],
  russia: [
    { label: "question", count: 6288, width: 100 },
    { label: "ukraine", count: 5590, width: 88.90 },
    { label: "united states", count: 4475, width: 71.15 },
    { label: "syria", count: 3619, width: 57.54 },
    { label: "president", count: 3610, width: 57.39 },
    { label: "situation", count: 3517, width: 55.90 },
    { label: "west", count: 3180, width: 50.57 },
    { label: "agreement", count: 3056, width: 48.60 },
    { label: "country", count: 3018, width: 47.99 },
    { label: "people", count: 2905, width: 46.21 }
  ]
};

const entitiesData = {
  china: [
    { label: "africa", count: 3308, width: 100 },
    { label: "asia", count: 2194, width: 66.32 },
    { label: "united states", count: 2143, width: 64.81 },
    { label: "united nations", count: 1935, width: 58.50 },
    { label: "europe", count: 1128, width: 34.08 },
    { label: "japan", count: 1112, width: 33.61 },
    { label: "russia", count: 847, width: 25.60 },
    { label: "covid-19", count: 660, width: 19.95 },
    { label: "asia - pacific", count: 620, width: 18.74 },
    { label: "India", count: 564, width: 17.04}
  ],
  russia: [
    { label: "united states", count: 10403, width: 100 },
    { label: "syria", count: 8235, width: 79.17 },
    { label: "united nations", count: 6322, width: 60.77 },
    { label: "ukraine", count: 5195, width: 49.92 },
    { label: "europe", count: 4911, width: 47.21 },
    { label: "european union", count: 3462, width: 33.28 },
    { label: "NATO", count: 3357, width: 32.28 },
    { label: "iran", count: 2950, width: 28.35 },
    { label: "china", count: 2757, width: 26.50 },
    { label: "UN Security Council", count: 2605, width: 25.31 }
  ]
};

function getDataset(metric) {
  // metric is "entities" or "noun-phrases"
  return metric === "entities" ? entitiesData : nounPhrasesData;
}

function renderBars(country, metric) {
  const dataset = getDataset(metric);
  const data = dataset[country];

  const container = document.querySelector(
    `.entities-country[data-country="${country}"] .entity-bars`
  );

  container.innerHTML = data
    .map(
      (item) => `
        <div class="entity-bar">
          <label class="entity-label" title="${item.label}">${item.label}</label>
          <div class="bar-wrapper">
            <div class="bar" style="width: ${item.width}%;"></div>
          </div>
          <span class="entity-count">${item.count}</span>
        </div>
      `
    )
    .join("");
}

function renderAll(metric) {
  renderBars("china", metric);
  renderBars("russia", metric);
}

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", function() {
  // Entities visualization initialization
  const metricSelect = document.getElementById("entitiesMetric");
  if (metricSelect) {
    renderAll(metricSelect.value);

    // Update on change
    metricSelect.addEventListener("change", (e) => {
      renderAll(e.target.value);
    });
  }

  // Back to Top Button functionality
  const backToTopButton = document.getElementById("back-to-top");
  
  if (backToTopButton) {
    window.addEventListener("scroll", () => {
      if (window.pageYOffset > 300) {
        backToTopButton.classList.add("show");
      } else {
        backToTopButton.classList.remove("show");
      }
    });
    
    backToTopButton.addEventListener("click", (e) => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
    });
  }
});
