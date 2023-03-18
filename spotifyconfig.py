import os
import spotipy
import spotifysecrets as AUTH
import spotifyconfig as CONFIG
from pathlib import Path
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

TRACKS_FROM_PLAYLISTS = 'tracks_from_playlists.txt'
TRACKS_FROM_LIKED = 'tracks_from_liked.txt'
ERRORS_FILE = 'errors.txt'

scope='user-library-read playlist-read-private playlist-modify-private'
auth_manager = SpotifyClientCredentials(client_id=AUTH.clientId, client_secret=AUTH.clientSecret)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=AUTH.clientId, client_secret=AUTH.clientSecret, redirect_uri=AUTH.redirectURI))

user = sp.me()
playlists = sp.user_playlists(user['id'])
for i, playlist in enumerate(playlists['items']):
    try:
        print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
        current_playlist = sp.user_playlist(user['id'], playlist_id=playlist['id'], fields='tracks,next,name')
    except Exception as e:
        print(e)

def CleanupFiles():
    tracks_from_playlists = Path(TRACKS_FROM_PLAYLISTS)
    if tracks_from_playlists.is_file():
        os.remove(tracks_from_playlists)

    tracks_from_liked = Path(TRACKS_FROM_LIKED)
    if tracks_from_liked.is_file():
        os.remove(tracks_from_liked)

    errors = Path(ERRORS_FILE)
    if errors.is_file():
        os.remove(errors)

def WriteToFile(file, text):
    with open(file, 'a') as file_out:
        file_out.write(text + '\n')