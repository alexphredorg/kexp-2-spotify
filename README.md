# kexp-2-spotify
Hacky tools to scrape KEXP playlists to spotify

Order of operations:
* scrapeKexpPlaylist.py: Finds all tracks from a show name and saves them out to tracks.json.  Order is preserved.
* findSpotifyTracks.py: Finds the Spotify track ID for each song and updates tracks.json.  This takes a while.  There are hacks in the code to fix up simple track name issues.
* saveSpotifyPlaylist.py: This creates a new Spotify playlist and adds every track in tracks.json to it.

The two Spotify tracks depend on the excellent Spotipy library.  You'll need to change the client_id and client_secret keys.
