document.addEventListener("DOMContentLoaded", () => {
  const credentialsForm = document.getElementById("credentialsForm");
  const credentialsSection = document.getElementById("credentialsSection");
  const resultsSection = document.getElementById("resultsSection");
  const errorSection = document.getElementById("errorSection");
  const resetBtn = document.getElementById("resetBtn");
  const retryBtn = document.getElementById("retryBtn");

  credentialsForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    // const clientId = document.getElementById("clientId").value.trim();
    // const clientSecret = document.getElementById("clientSecret").value.trim();
    const clientId = "29d0a164e4914d018d98bf0b2c69ef78";
    const clientSecret = "c1798841a2d14c4aa2b8de02623bb686";
    const artistName = document.getElementById("artistName").value.trim();

    if (!clientId || !clientSecret || !artistName) {
      showError("Please enter Artist Name, Client ID, and Client Secret.");
      return;
    }

    await fetchAnalytics(clientId, clientSecret, artistName);
  });

  resetBtn.addEventListener("click", () => {
    showCredentialsSection();
    credentialsForm.reset();
  });

  retryBtn.addEventListener("click", () => {
    showCredentialsSection();
  });

  // --------------------------------------------
  // FETCH ANALYTICS FROM API
  // --------------------------------------------
  async function fetchAnalytics(clientId, clientSecret, artistName) {
    const submitBtn = credentialsForm.querySelector('button[type="submit"]');
    const btnText = submitBtn.querySelector(".btn-text");
    const loader = submitBtn.querySelector(".loader");

    submitBtn.disabled = true;
    btnText.textContent = "Loading...";
    loader.style.display = "inline-block";

    try {
      const response = await fetch("/api/analytics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          artist_name: artistName,
          client_id: clientId,
          client_secret: clientSecret,
        }),
      });

      const data = await response.json();

      if (!response.ok) throw new Error(data.error);

      displayResults(data);
      console.log("FULL JSON RESPONSE:", data);

      showResultsSection();
    } catch (error) {
      showError(error.message);
    } finally {
      submitBtn.disabled = false;
      btnText.textContent = "Get Analytics";
      loader.style.display = "none";
    }
  }

  // --------------------------------------------
  // DISPLAY RESULTS ON PAGE
  // --------------------------------------------
  function displayResults(data) {
    const artist = data.artist;
    const mtJoyStats = document.getElementById("mtJoyStats");

    // ---------------- ARTIST MAIN INFO ----------------
    mtJoyStats.innerHTML = `
        ${
          artist.image
            ? `<div class="artist-header">
                 <img src="${artist.image}" class="artist-image">
                 <div class="artist-info"><h3>${artist.name}</h3></div>
               </div>`
            : `<h3>${artist.name}</h3>`
        }

        <div class="stat-row"><span class="stat-label">Followers</span>
          <span class="stat-value">${formatNumber(artist.followers)}</span>
        </div>

        <div class="stat-row"><span class="stat-label">Popularity</span>
          <span class="stat-value">${artist.popularity}/100</span>
        </div>        
    `;

    // ---------------- LATEST ALBUM ----------------
    const album = data.latest_album;
    const latestAlbum = document.getElementById("latestAlbum");

    latestAlbum.innerHTML = `
        <div class="album-header">
            ${
              album.image
                ? `<img src="${album.image}" class="album-image">`
                : ""
            }
            <div class="album-info">
                <h3>${album.name}</h3>
                <p class="album-date">${album.release_date}</p>
            </div>
        </div>

        <h4>Tracks</h4>
        <ul class="track-list">
            ${album.tracks
              .map(
                (t) =>
                  `<li>${t.name} <span style="color:#999">(${t.duration})</span></li>`
              )
              .join("")}
        </ul>
    `;

    // ---------------- POPULAR ARTISTS ----------------
    const popularArtists = document.getElementById("popularArtists");
    popularArtists.innerHTML = data.popular_artists
      .map((a) => `<span class="artist-tag">${a}</span>`)
      .join("");

    // ---------------- RANDOM ARTIST ----------------
    const randomArtist = document.getElementById("randomArtist");
    const rand = data.random_artist;

    if (!rand) {
      randomArtist.innerHTML = "<p>No random artist available.</p>";
      return;
    }

    randomArtist.innerHTML = `
        ${
          rand.image
            ? `<img src="${rand.image}" class="artist-image" style="margin-bottom:20px;">`
            : ""
        }
        <h3>${rand.name}</h3>

        <div class="stat-row"><span class="stat-label">Followers</span>
          <span class="stat-value">${formatNumber(rand.followers)}</span>
        </div>

        <div class="stat-row"><span class="stat-label">Popularity</span>
          <span class="stat-value">${rand.popularity}/100</span>
        </div>

        <h4>Top Tracks</h4>
        <ul class="track-list">${rand.top_tracks
          .map((t) => `<li>${t}</li>`)
          .join("")}</ul>
    `;
  }

  // --------------------------------------------
  // HELPERS
  // --------------------------------------------
  function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }

  function showCredentialsSection() {
    credentialsSection.style.display = "flex";
    resultsSection.style.display = "none";
    errorSection.style.display = "none";
  }

  function showResultsSection() {
    credentialsSection.style.display = "none";
    resultsSection.style.display = "block";
    errorSection.style.display = "none";
  }

  function showError(message) {
    credentialsSection.style.display = "none";
    resultsSection.style.display = "none";
    errorSection.style.display = "flex";
    document.getElementById("errorMessage").textContent = message;
  }
});
