// Parse CSV and create visualizations
async function initializeVisualizations() {
    try {
        // Fetch the CSV file (replace 'data.csv' with your actual file path)
        const response = await fetch('data.csv');
        const csvText = await response.text();
        
        // Parse CSV
        const data = parseCSV(csvText);
        
        // Process data for each keyword
        const taiwanData = processKeywordData(data, 'Taiwan');
        const ukraineData = processKeywordData(data, 'Ukraine');
        const hongKongData = processKeywordData(data, 'Hong Kong');
        
        // Create charts
        createChart('taiwanChart', taiwanData, 'Taiwan');
        createChart('ukraineChart', ukraineData, 'Ukraine');
        createChart('hongKongChart', hongKongData, 'Hong Kong');
        
    } catch (error) {
        console.error('Error loading or processing data:', error);
    }
}

// Simple CSV parser
function parseCSV(csvText) {
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim());
        const row = {};
        headers.forEach((header, index) => {
            row[header] = values[index];
        });
        data.push(row);
    }
    
    return data;
}

// Process data for a specific keyword
// Expects CSV columns: date, speech_text, keyword_name, frequency (or similar)
function processKeywordData(data, keyword) {
    const aggregated = {};
    
    data.forEach(row => {
        // Adjust these property names based on your CSV structure
        if (row.keyword && row.keyword.trim().toLowerCase() === keyword.toLowerCase()) {
            const date = row.date;
            const frequency = parseFloat(row.frequency) || 0;
            
            if (aggregated[date]) {
                aggregated[date] += frequency;
            } else {
                aggregated[date] = frequency;
            }
        }
    });
    
    // Sort by date and convert to arrays
    const sortedDates = Object.keys(aggregated).sort();
    const frequencies = sortedDates.map(date => aggregated[date]);
    
    return {
        dates: sortedDates,
        frequencies: frequencies
    };
}

// Create a Plotly chart
function createChart(elementId, keywordData, keywordName) {
    const trace = {
        x: keywordData.dates,
        y: keywordData.frequencies,
        type: 'scatter',
        mode: 'lines+markers',
        name: keywordName,
        line: {
            color: '#6ec8ff',
            width: 2
        },
        marker: {
            size: 5,
            color: '#6ec8ff'
        }
    };
    
    const layout = {
        title: `${keywordName} Frequency Over Time`,
        xaxis: {
            title: 'Date',
            color: '#b0b8d4'
        },
        yaxis: {
            title: 'Frequency',
            color: '#b0b8d4'
        },
        plot_bgcolor: '#1a1f3a',
        paper_bgcolor: '#1a1f3a',
        font: {
            color: '#b0b8d4'
        },
        margin: {
            l: 50,
            r: 20,
            t: 40,
            b: 40
        }
    };
    
    const config = {
        responsive: true,
        displayModeBar: false
    };
    
    Plotly.newPlot(elementId, [trace], layout, config);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initializeVisualizations);
