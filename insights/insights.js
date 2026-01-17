async function loadCache(url) {
  return fetch(url).then(r => r.json());
}

function parseEventsCsv(csvText) {
  // Parse CSV and return array of {keyword, year, event}
  const lines = csvText.trim().split('\n');
  const events = [];
  for (let i = 1; i < lines.length; i++) {
    const line = lines[i];
    if (!line.trim()) continue;
    // Simple CSV parsing: "id","keyword","year","event"
    const matches = line.match(/"[^"]*"|[^,]+/g);
    if (matches && matches.length >= 4) {
      const keyword = matches[1].replace(/"/g, '').trim();
      const year = parseInt(matches[2].replace(/"/g, '').trim());
      const event = matches[3].replace(/"/g, '').trim();
      events.push({ keyword, year, event });
    }
  }
  return events;
}

function createKeywordsCheckboxes(keywordMap, eventLines) {
  // Define keyword categories by ID
  const categories = {
    continents: ['1', '2', '3', '4', '5'],
    areas: ['42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60'],
    organizations: ['6', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41'],
    topics: ['7', '9', '10', '12', '13', '14', '17', '19', '20', '21', '22', '23'],
    rhetorical: ['8', '11', '15', '16', '18', '24', '25', '26', '27', '28', '29', '30'],
    chineseConcepts: ['61', '62', '63', '64', '65', '66', '67', '68', '69', '70']
  };

  // Build suggested topics from event keywords
  const suggestedKeywords = new Set();
  eventLines.forEach(evt => {
    // Find the ID for this keyword
    Object.entries(keywordMap).forEach(([id, name]) => {
      if (name === evt.keyword) {
        suggestedKeywords.add(id);
      }
    });
  });
  categories.suggested = Array.from(suggestedKeywords);

  function createCheckbox(id, label) {
    const idSafe = 'kw_' + id;
    const row = document.createElement('div');
    row.className = 'checkbox-row';
    const cb = document.createElement('input');
    cb.type = 'checkbox';
    cb.id = idSafe;
    cb.value = id;
    cb.checked = false;
    const lab = document.createElement('label');
    lab.htmlFor = idSafe;
    lab.textContent = label;
    row.appendChild(cb);
    row.appendChild(lab);
    return row;
  }

  // Populate each category
  Object.entries(categories).forEach(([catKey, ids]) => {
    const container = document.getElementById(`kw-${catKey}`);
    if (!container) return;
    ids.forEach(id => {
      if (keywordMap[id]) {
        container.appendChild(createCheckbox(id, keywordMap[id]));
      }
    });
  });
}

function getSelectedKeywordIds() {
  return Array.from(document.querySelectorAll('#keywords-list input[type=checkbox]:checked')).map(i => i.value);
}

function updateSelectionCounts() {
  const categories = {
    suggested: [],  // Will be populated dynamically
    continents: ['1', '2', '3', '4', '5'],
    areas: ['42', '43', '44', '45', '46', '47', '48', '49', '50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60'],
    organizations: ['6', '31', '32', '33', '34', '35', '36', '37', '38', '39', '40', '41'],
    topics: ['7', '9', '10', '12', '13', '14', '17', '19', '20', '21', '22', '23'],
    rhetorical: ['8', '11', '15', '16', '18', '24', '25', '26', '27', '28', '29', '30'],
    chineseConcepts: ['61', '62', '63', '64', '65', '66', '67', '68', '69', '70']
  };

  Object.entries(categories).forEach(([catKey, ids]) => {
    const container = document.getElementById(`kw-${catKey}`);
    if (!container) return;
    const summary = container.parentElement.querySelector('summary');
    if (!summary) return;
    const checked = container.querySelectorAll('input[type=checkbox]:checked').length;
    const countSpan = summary.querySelector('.details-summary-count');
    if (countSpan) {
      countSpan.textContent = `(${checked} selected)`;
    }
  });
}

function buildCounts(countRows, selectedCountries, selectedKeywordIds) {
  // countRows: {year, keyword, country, count}
  const yearSet = new Set();
  const countsByKwAndCountry = {}; // {keyword: {country: {year: count}}}
  
  selectedKeywordIds.forEach(k => {
    countsByKwAndCountry[k] = {};
    selectedCountries.forEach(c => {
      countsByKwAndCountry[k][c] = {};
    });
  });
  
  for (const r of countRows) {
    // Exclude 2026 and Russia data from 2013 and earlier
    const year = Math.floor(parseFloat(r.year));
    if (year === 2026) continue;
    if (r.country === 'Russia' && year <= 2013) continue;
    
    if (!selectedCountries.includes(r.country)) continue;
    if (!selectedKeywordIds.includes(r.keyword)) continue;
    const y = String(year);
    yearSet.add(y);
    if (!countsByKwAndCountry[r.keyword][r.country][y]) {
      countsByKwAndCountry[r.keyword][r.country][y] = 0;
    }
    countsByKwAndCountry[r.keyword][r.country][y] += r.count;
  }
  
  const years = Array.from(yearSet).map(y=>+y).sort((a,b)=>a-b);
  return { years, countsByKwAndCountry };
}

function drawPlot(years, countsByKwAndCountry, keywordMap, selectedCountries, totalSpeechesByYearCountry, normalized, selectedKeywordIds, eventLines) {
  const traces = [];
  const colors = { 'China': '#EF553B', 'Russia': '#636EFA' };
  
  Object.keys(countsByKwAndCountry).forEach(kid => {
    selectedCountries.forEach(country => {
      // For Russia, only plot years where it has actual data to avoid gaps
      let xData = years;
      let yData = years.map(y => {
        let count = countsByKwAndCountry[kid][country][String(y)] || 0;
        if (normalized && totalSpeechesByYearCountry[country] && totalSpeechesByYearCountry[country][String(y)]) {
          const total = totalSpeechesByYearCountry[country][String(y)];
          return total > 0 ? (count / total) * 100 : 0;
        }
        return count;
      });
      
      if (country === 'Russia') {
        // Filter to only include years with data
        const dataPoints = years
          .map((y, i) => ({ year: y, count: yData[i] }))
          .filter(p => p.count > 0);
        xData = dataPoints.map(p => p.year);
        yData = dataPoints.map(p => p.count);
      }
      
      traces.push({
        x: xData,
        y: yData,
        mode: 'lines+markers',
        name: `${keywordMap[kid]} (${country})`,
        line: { width: 2 },
        marker: { size: 6 },
        legendgroup: kid,
        legendgrouptitle: { text: keywordMap[kid] }
      });
    });
  });
  
  // Build shapes and annotations for event lines
  const shapes = [];
  const annotations = [];
  selectedKeywordIds.forEach(kid => {
    const keywordText = keywordMap[kid];
    const matchingEvents = eventLines.filter(e => e.keyword === keywordText);
    matchingEvents.forEach((evt, eventIndex) => {
      shapes.push({
        type: 'line',
        x0: evt.year,
        x1: evt.year,
        y0: 0,
        y1: 1,
        yref: 'paper',
        line: {
          color: '#888',
          width: 2,
          dash: 'dash'
        }
      });
      
      // Stagger events horizontally to avoid overlap, keep below title
      let xAnchor = eventIndex % 2 === 0 ? 'left' : 'right';
      let xOffset = eventIndex % 2 === 0 ? 40 : -40;
      
      annotations.push({
        x: evt.year,
        y: 0.95,
        yref: 'paper',
        xanchor: xAnchor,
        text: evt.event,
        showarrow: true,
        arrowhead: 2,
        arrowsize: 1,
        arrowwidth: 1,
        arrowcolor: '#888',
        ax: xOffset,
        ay: -50,
        bgcolor: '#2a3f5f',
        bordercolor: '#888',
        borderwidth: 1,
        font: { color: '#cfe9ff', size: 11 },
        align: 'center'
      });
    });
  });
  
  const layout = {
    title: normalized ? 'Percentage of speeches per year mentioning selected keywords' : 'Number of speeches per year containing selected keywords',
    xaxis: { title: 'Year' },
    yaxis: { title: normalized ? 'Percentage of speeches (%)' : 'Number of speeches' },
    hovermode: 'x unified',
    margin: { b: 50, l: 60, r: 20, t: 140 },
    legend: { orientation: 'v', xanchor: 'left', x: 1.02 },
    autosize: true,
    shapes: shapes,
    annotations: annotations
  };
  Plotly.react('kw-chart', traces, layout, { responsive: true });
}

async function initKeywordViz() {
  const cache = await loadCache('../data/viz_cache.json');

  const keywordMap = cache.keywords;
  const countRows = cache.counts;

  // Load events data
  const eventsResponse = await fetch('./events.csv').then(r => r.text());
  const eventLines = parseEventsCsv(eventsResponse);

  createKeywordsCheckboxes(keywordMap, eventLines);

  // Build total speeches per year per country from cache
  const totalSpeechesByYearCountry = { China: {}, Russia: {} };
  for (const t of cache.total_speeches) {
    const year = Math.floor(parseFloat(t.year));
    if (year === 2026) continue;
    if (t.country === 'Russia' && year <= 2013) continue;
    
    const y = String(year);
    totalSpeechesByYearCountry[t.country][y] = t.total_speeches;
  }

  // Track selected countries and mode
  let selectedCountries = { China: true, Russia: true };
  let normalizedMode = true;
  
  const chinaBtn = document.getElementById('country-china-btn');
  const russiaBtn = document.getElementById('country-russia-btn');
  const rawBtn = document.getElementById('mode-raw-btn');
  const adjustedBtn = document.getElementById('mode-adjusted-btn');
  
  function updateButtonStyles() {
    if (selectedCountries.China) {
      chinaBtn.classList.remove('inactive');
    } else {
      chinaBtn.classList.add('inactive');
    }
    
    if (selectedCountries.Russia) {
      russiaBtn.classList.remove('inactive');
    } else {
      russiaBtn.classList.add('inactive');
    }
    
    if (normalizedMode) {
      rawBtn.classList.add('inactive');
      adjustedBtn.classList.remove('inactive');
    } else {
      rawBtn.classList.remove('inactive');
      adjustedBtn.classList.add('inactive');
    }
  }
  
  chinaBtn.addEventListener('click', () => {
    selectedCountries.China = !selectedCountries.China;
    updateButtonStyles();
    refresh();
  });
  
  russiaBtn.addEventListener('click', () => {
    selectedCountries.Russia = !selectedCountries.Russia;
    updateButtonStyles();
    refresh();
  });
  
  rawBtn.addEventListener('click', () => {
    normalizedMode = false;
    updateButtonStyles();
    refresh();
  });
  
  adjustedBtn.addEventListener('click', () => {
    normalizedMode = true;
    updateButtonStyles();
    refresh();
  });

  function refresh() {
    const countriesToShow = [];
    if (selectedCountries.China) countriesToShow.push('China');
    if (selectedCountries.Russia) countriesToShow.push('Russia');
    
    const selectedKs = getSelectedKeywordIds();
    if (selectedKs.length === 0 || countriesToShow.length === 0) {
      Plotly.purge('kw-chart');
      document.getElementById('kw-chart').innerHTML = '<div class="kw-viz-note">Select one or more keywords and countries to show trend</div>';
      return;
    }
    const { years, countsByKwAndCountry } = buildCounts(countRows, countriesToShow, selectedKs);
    if (years.length === 0) {
      Plotly.purge('kw-chart');
      document.getElementById('kw-chart').innerHTML = '<div class="kw-viz-note">No data for this selection</div>';
      return;
    }
    drawPlot(years, countsByKwAndCountry, keywordMap, countriesToShow, totalSpeechesByYearCountry, normalizedMode, selectedKs, eventLines);
  }

  // auto-update when any keyword checkbox changes
  document.getElementById('keywords-list').addEventListener('change', () => {
    updateSelectionCounts();
    refresh();
  });

  // Check Taiwan by default if it exists
  const taiwanId = Object.entries(keywordMap).find(([id, name]) => name === 'Taiwan')?.[0];
  if (taiwanId) {
    const taiwanCheckbox = document.getElementById('kw_' + taiwanId);
    if (taiwanCheckbox) {
      taiwanCheckbox.checked = true;
    }
  }
  
  updateSelectionCounts();
  updateButtonStyles();
  refresh();
}

window.addEventListener('load', initKeywordViz);
