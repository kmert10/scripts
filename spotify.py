import os
import spotipy
import spotifysecrets as AUTH
import spotifyconfig as CONFIG
from pathlib import Path
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

scope='user-library-read playlist-read-private playlist-modify-private'
auth_manager = SpotifyClientCredentials(client_id=AUTH.clientId, client_secret=AUTH.clientSecret)
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=AUTH.clientId, client_secret=AUTH.clientSecret, redirect_uri=AUTH.redirectURI))

user = sp.me()
playlists = sp.user_playlists(user['id'])

all_playlist_tracks = set()

TRACKS_FROM_PLAYLISTS = 'tracks_from_playlists.txt'
TRACKS_FROM_LIKED = 'tracks_from_liked.txt'
ERRORS_FILE = 'errors.txt'

CONFIG.CleanupFiles()

while playlists:
    with open(CONFIG.TRACKS_FROM_PLAYLISTS, 'a') as file_out:
        for i, playlist in enumerate(playlists['items']):
            print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
            current_playlist = sp.user_playlist(user['id'], playlist_id=playlist['id'], fields='tracks,next,name')
            print(u'Writing {0} tracks'.format(current_playlist['tracks']['total']))
            current_tracks = current_playlist['tracks']
            while True:
                for item in current_tracks['items']:
                    if 'track' in item:
                        track = item['track']
                    else:
                        track = item
                    try:
                        track_uri = track['uri'].split(":")[2]
                        all_playlist_tracks.add(track_uri)
                        file_out.write(track_uri + '\n')
                    except KeyError:
                        print(u'Skipping track {0} by {1} (local only?)'.format(track['name'], track['artists'][0]['name']))
                    except:
                        print('Skipping')
                # 1 page = 50 results
                # check if there are more pages
                if current_tracks['next']:
                    current_tracks = sp.next(current_tracks)
                else:
                    break
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None

print(len(all_playlist_tracks))


playlist_name = "All Playlists Pt. "
playlist_iteration = 1
all_playlist = sp.user_playlist_create(user=user['id'], name=playlist_name + str(playlist_iteration), public=False)

batchSize=50
list_tracks = list(all_playlist_tracks)
tracks_left = len(list_tracks)
for i in range(tracks_left, 0, batchSize * -1):
    lower_bound = 0
    if (i - batchSize > 0):
        lower_bound = i - batchSize
    else:
        lower_bound = 0
    batch = list_tracks[lower_bound:i]    
    try:
        sp.user_playlist_add_tracks(user['id'], playlist_id=all_playlist['id'], tracks=batch)
    except Exception as e:
        if ("400" in str(e)):
            CONFIG.WriteToFile(CONFIG.ERRORS_FILE, ' '.join(map(str, batch)))
        elif ("413" in str(e)):
            playlist_iteration += 1
            all_playlist = sp.user_playlist_create(user['id'], name=playlist_name + str(playlist_iteration), public=False)
            sp.user_playlist_add_tracks(user['id'], playlist_id=all_playlist['id'], tracks=batch)
        else:
            print(str(e))
