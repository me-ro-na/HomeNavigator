document.addEventListener('DOMContentLoaded', function() {
    const profileLink = document.getElementById('profile-link');
    const profileDropdown = document.getElementById('profile-dropdown');

    profileLink.addEventListener('click', function(event) {
        event.stopPropagation();
        profileDropdown.classList.toggle('show');
    });

    document.addEventListener('click', function(event) {
        if (!profileLink.contains(event.target)) {
            profileDropdown.classList.remove('show');
        }
    });

    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');

    searchInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();
            const query = searchInput.value.trim();
            if (query) {
                performSearch(query);
            }
        }
    });

    searchButton.addEventListener('click', function() {
        const query = searchInput.value.trim();
        if (query) {
            performSearch(query);
        }
    });

    document.getElementById('recent-searches-list').addEventListener('click', function(event) {
        if (event.target.classList.contains('search-query')) {
            const query = event.target.innerText;
            searchInput.value = query;
            performSearch(query);
        }
    });
});

function performSearch(query) {
    fetch('/search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query: query })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            updateSearchHistory(data.search_history);
            const searchInput = document.getElementById('search-input');
            searchInput.value = '';
        }
    });
}

function updateSearchHistory(searchHistory) {
    const recentSearchesList = document.getElementById('recent-searches-list');
    recentSearchesList.innerHTML = ''; // 기존 검색 기록 초기화
    searchHistory.forEach(query => {
        const listItem = document.createElement('li');
        listItem.innerHTML = `<span class="search-query">${query}</span>`;
        recentSearchesList.appendChild(listItem);
    });
}
