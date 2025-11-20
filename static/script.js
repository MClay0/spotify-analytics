document.addEventListener('DOMContentLoaded', () => {
    const credentialsForm = document.getElementById('credentialsForm');
    const credentialsSection = document.getElementById('credentialsSection');
    const resultsSection = document.getElementById('resultsSection');
    const errorSection = document.getElementById('errorSection');
    const resetBtn = document.getElementById('resetBtn');
    const retryBtn = document.getElementById('retryBtn');

    credentialsForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const clientId = document.getElementById('clientId').value.trim();
        const clientSecret = document.getElementById('clientSecret').value.trim();

        if (!clientId || !clientSecret) {
            showError('Please enter both Client ID and Client Secret');
            return;
        }

        await fetchAnalytics(clientId, clientSecret);
    });

    resetBtn.addEventListener('click', () => {
        showCredentialsSection();
        document.getElementById('credentialsForm').reset();
    });

    retryBtn.addEventListener('click', () => {
        showCredentialsSection();
    });

    async function fetchAnalytics(clientId, clientSecret) {
        const submitBtn = credentialsForm.querySelector('button[type="submit"]');
        const btnText = submitBtn.querySelector('.btn-text');
        const loader = submitBtn.querySelector('.loader');

        // Show loading state
        submitBtn.disabled = true;
        btnText.textContent = 'Loading...';
        loader.style.display = 'inline-block';

        try {
            const response = await fetch('/api/analytics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    client_id: clientId,
                    client_secret: clientSecret
                })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Failed to fetch analytics');
            }

            displayResults(data);
            showResultsSection();

        } catch (error) {
            showError(error.message);
        } finally {
            submitBtn.disabled = false;
            btnText.textContent = 'Get Analytics';
            loader.style.display = 'none';
        }
    }

    function displayResults(data) {
        // Display Mt. Joy Stats
        const mtJoyStats = document.getElementById('mtJoyStats');
        mtJoyStats.innerHTML = `
            ${data.mt_joy.image ? `
                <div class="artist-header">
                    <img src="${data.mt_joy.image}" alt="${data.mt_joy.name}" class="artist-image">
                    <div class="artist-info">
                        <h3>${data.mt_joy.name}</h3>
                    </div>
                </div>
            ` : `<h3>${data.mt_joy.name}</h3>`}
            <div class="stat-row">
                <span class="stat-label">Followers</span>
                <span class="stat-value">${formatNumber(data.mt_joy.followers)}</span>
            </div>
            <div class="stat-row">
                <span class="stat-label">Popularity</span>
                <span class="stat-value">${data.mt_joy.popularity}/100</span>
            </div>
            <h4 style="margin: 20px 0 10px 0; color: #666;">Top Tracks</h4>
            <ul class="track-list">
                ${data.mt_joy.top_tracks.map(track => `<li>${track}</li>`).join('')}
            </ul>
        `;

        // Display Latest Album
        const latestAlbum = document.getElementById('latestAlbum');
        latestAlbum.innerHTML = `
            <div class="album-header">
                ${data.latest_album.image ? `
                    <img src="${data.latest_album.image}" alt="${data.latest_album.name}" class="album-image">
                ` : ''}
                <div class="album-info">
                    <h3>${data.latest_album.name}</h3>
                    <p class="album-date">${data.latest_album.release_date}</p>
                </div>
            </div>
            <h4 style="margin: 20px 0 10px 0; color: #666;">Tracks</h4>
            <ul class="track-list">
                ${data.latest_album.tracks.map(track =>
                    `<li>${track.name} <span style="color: #999;">(${track.duration})</span></li>`
                ).join('')}
            </ul>
        `;

        // Display Popular Artists
        const popularArtists = document.getElementById('popularArtists');
        popularArtists.innerHTML = data.popular_artists.map(artist =>
            `<span class="artist-tag">${artist}</span>`
        ).join('');

        // Display Random Artist
        const randomArtist = document.getElementById('randomArtist');
        if (data.random_artist) {
            randomArtist.innerHTML = `
                ${data.random_artist.image ? `
                    <img src="${data.random_artist.image}" alt="${data.random_artist.name}" class="artist-image" style="margin-bottom: 20px;">
                ` : ''}
                <h3 style="margin-bottom: 20px;">${data.random_artist.name}</h3>
                <div class="stat-row">
                    <span class="stat-label">Followers</span>
                    <span class="stat-value">${formatNumber(data.random_artist.followers)}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Popularity</span>
                    <span class="stat-value">${data.random_artist.popularity}/100</span>
                </div>
                <h4 style="margin: 20px 0 10px 0; color: #666; text-align: left;">Top Tracks</h4>
                <ul class="track-list">
                    ${data.random_artist.top_tracks.map(track => `<li>${track}</li>`).join('')}
                </ul>
            `;
        } else {
            randomArtist.innerHTML = '<p>No random artist available</p>';
        }
    }

    function formatNumber(num) {
        return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    }

    function showCredentialsSection() {
        credentialsSection.style.display = 'flex';
        resultsSection.style.display = 'none';
        errorSection.style.display = 'none';
    }

    function showResultsSection() {
        credentialsSection.style.display = 'none';
        resultsSection.style.display = 'block';
        errorSection.style.display = 'none';
    }

    function showError(message) {
        credentialsSection.style.display = 'none';
        resultsSection.style.display = 'none';
        errorSection.style.display = 'flex';
        document.getElementById('errorMessage').textContent = message;
    }
});
