# Spotify Analytics

A Python script that analyzes Mt. Joy using the Spotify Web API and discovers new music. The script retrieves band statistics, their latest album details, finds popular artists from new releases, and randomly selects one for detailed analysis.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create a Spotify App:**
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/applications)
   - Click "Create an App"
   - Fill in the app name and description
   - Note down your Client ID and Client Secret

3. **Set up credentials (choose one option):**

   **Option A: Environment file (recommended)**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your credentials
   SPOTIFY_CLIENT_ID=your_actual_client_id
   SPOTIFY_CLIENT_SECRET=your_actual_client_secret
   ```

   **Option B: Manual input**
   - Just run the script and it will prompt you for credentials

4. **Run the script:**
   ```bash
   python driver.py
   ```
