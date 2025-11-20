# Spotify Analytics

A web application that analyzes Mt. Joy using the Spotify Web API and discovers new music. The app retrieves band statistics, their latest album details, finds popular artists from new releases, and randomly selects one for detailed analysis.

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

## Running the Application

### Option 1: Web Interface (Recommended)

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Open in your browser:**
   - Navigate to: `http://localhost:5000`
   - Enter your Spotify Client ID and Client Secret in the web form
   - Click "Get Analytics" to view the results

3. **Stop the server:**
   - Press `Ctrl+C` in the terminal

### Option 2: Command Line Script

1. **Set up credentials:**
   ```bash
   # Copy the example file
   cp .env.example .env

   # Edit .env and add your credentials
   SPOTIFY_CLIENT_ID=your_actual_client_id
   SPOTIFY_CLIENT_SECRET=your_actual_client_secret
   ```

2. **Run the script:**
   ```bash
   python driver.py
   ```
