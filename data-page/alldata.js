// Data page search and filtering functionality
let allData = [];
let currentSearchResults = [];
let currentPage = 1;
const resultsPerPage = 4;

async function loadData() {
    try {
        const response = await fetch('../data/China_Russia_speeches.json');
        allData = await response.json();
    } catch (error) {
        console.error('Error loading data:', error);
        document.getElementById('searchResults').innerHTML = '<p class="error-message">Error loading data. Please refresh the page.</p>';
    }
}

// Search and filter functionality
function performSearch() {
    const searchTerm = document.getElementById('keywordSearch').value.trim();
    const caseSensitive = document.getElementById('caseSensitiveCheckbox').checked;
    const wholeWord = document.getElementById('wholeWordCheckbox').checked;
    const selectedCountry = document.querySelector('input[name="countryFilter"]:checked').value;
    const resultsContainer = document.getElementById('searchResults');

    if (!searchTerm) {
        resultsContainer.innerHTML = '';
        return;
    }

    let searchRegex;
    try {
        if (wholeWord) {
            const pattern = `\\b${searchTerm}\\b`;
            searchRegex = new RegExp(pattern, caseSensitive ? 'g' : 'gi');
        } else {
            searchRegex = new RegExp(searchTerm, caseSensitive ? 'g' : 'gi');
        }
    } catch (error) {
        resultsContainer.innerHTML = '<p class="error-message">Invalid search pattern.</p>';
        return;
    }

    let results = allData.filter(item => {
        const content = (item.title + ' ' + item.content).toLowerCase();
        const pattern = caseSensitive ? searchTerm : searchTerm.toLowerCase();
        const matchesKeyword = caseSensitive ? 
            (item.title + ' ' + item.content).includes(pattern) : 
            content.includes(pattern);
        
        const matchesCountry = selectedCountry === 'all' || item.country === selectedCountry;
        
        return matchesKeyword && matchesCountry;
    });

    displayResults(results, searchTerm, caseSensitive);
}

// Display search results
function displayResults(results, searchTerm, caseSensitive) {
    currentSearchResults = results;
    currentPage = 1;
    showResultsPage(currentPage, searchTerm, caseSensitive);
}

// Show a specific page of results
function showResultsPage(pageNum, searchTerm, caseSensitive) {
    const resultsContainer = document.getElementById('searchResults');

    if (currentSearchResults.length === 0) {
        resultsContainer.innerHTML = `<p class="no-results">No results found for "${searchTerm}". Try different keywords.</p>`;
        return;
    }

    const startIndex = (pageNum - 1) * resultsPerPage;
    const endIndex = startIndex + resultsPerPage;
    const pageResults = currentSearchResults.slice(startIndex, endIndex);
    const totalPages = Math.ceil(currentSearchResults.length / resultsPerPage);

    let html = `<p class="results-count">Found <strong>${currentSearchResults.length}</strong> speech(es) containing "${searchTerm}"</p>`;
    html += `<p class="pagination-info">Page ${pageNum} of ${totalPages}</p>`;
    html += '<div class="results-list">';

    pageResults.forEach((item, index) => {
        const title = escapeHtml(item.title);
        const country = escapeHtml(item.country);
        const date = escapeHtml(item.date);
        const content = escapeHtml(item.content);
        
        // Count occurrences
        const contentLower = item.content.toLowerCase();
        const searchLower = searchTerm.toLowerCase();
        const count = (contentLower.match(new RegExp(searchLower, 'g')) || []).length;

        html += `
            <div class="result-item">
                <div class="result-header">
                    <h4 class="result-title">${title}</h4>
                    <span class="result-country">${country}</span>
                </div>
                <p class="result-date">Date: ${date}</p>
                <p class="result-count">Keyword appears <strong>${count}</strong> time(s)</p>
                <details class="result-preview">
                    <summary>View Content Preview</summary>
                    <div class="preview-content">${getPreview(content, searchTerm, caseSensitive)}</div>
                </details>
            </div>
        `;
    });

    html += '</div>';

    // Add pagination controls with current, previous, and next page numbers
    html += '<div class="pagination-controls">';
    const pagesToShow = [];
    
    if (pageNum > 1) {
        pagesToShow.push(pageNum - 1);
    }
    pagesToShow.push(pageNum);
    if (pageNum < totalPages) {
        pagesToShow.push(pageNum + 1);
    }
    
    pagesToShow.forEach(pageNumber => {
        if (pageNumber === pageNum) {
            html += `<button class="pagination-btn pagination-btn-active">${pageNumber}</button>`;
        } else {
            html += `<button class="pagination-btn" onclick="goToPage(${pageNumber})">${pageNumber}</button>`;
        }
    });
    html += '</div>';

    resultsContainer.innerHTML = html;
}

// Go to a specific page
function goToPage(pageNum) {
    currentPage = pageNum;
    const searchTerm = document.getElementById('keywordSearch').value.trim();
    const caseSensitive = document.getElementById('caseSensitiveCheckbox').checked;
    showResultsPage(currentPage, searchTerm, caseSensitive);
}

// Go to next page
function goToNextPage() {
    const totalPages = Math.ceil(currentSearchResults.length / resultsPerPage);
    if (currentPage < totalPages) {
        currentPage++;
        const searchTerm = document.getElementById('keywordSearch').value.trim();
        const caseSensitive = document.getElementById('caseSensitiveCheckbox').checked;
        showResultsPage(currentPage, searchTerm, caseSensitive);
    }
}

// Go to previous page
function goToPreviousPage() {
    if (currentPage > 1) {
        currentPage--;
        const searchTerm = document.getElementById('keywordSearch').value.trim();
        const caseSensitive = document.getElementById('caseSensitiveCheckbox').checked;
        showResultsPage(currentPage, searchTerm, caseSensitive);
    }
}

// Get preview of content with keyword highlighted
function getPreview(content, searchTerm, caseSensitive) {
    const words = content.split(' ');
    const preview = words.slice(0, 100).join(' ');
    
    let highlightedPreview = preview;
    if (caseSensitive) {
        highlightedPreview = preview.replace(
            new RegExp(`(${searchTerm})`, 'g'),
            '<mark>$1</mark>'
        );
    } else {
        highlightedPreview = preview.replace(
            new RegExp(`(${searchTerm})`, 'gi'),
            '<mark>$1</mark>'
        );
    }
    
    return highlightedPreview + (words.length > 100 ? '...' : '');
}

// Escape HTML special characters
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('keywordSearch').addEventListener('input', performSearch);
    document.getElementById('keywordSearch').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') performSearch();
    });

    document.getElementById('caseSensitiveCheckbox').addEventListener('change', performSearch);
    document.getElementById('wholeWordCheckbox').addEventListener('change', performSearch);

    document.querySelectorAll('input[name="countryFilter"]').forEach(radio => {
        radio.addEventListener('change', performSearch);
    });

    document.getElementById('clearSearchBtn').addEventListener('click', () => {
        document.getElementById('keywordSearch').value = '';
        document.getElementById('caseSensitiveCheckbox').checked = false;
        document.getElementById('wholeWordCheckbox').checked = false;
        document.getElementById('searchResults').innerHTML = '';
    });

    // Load data on page load
    loadData();
});
