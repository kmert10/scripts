import spotipy
import spotifysecrets as AUTH
import spotifyconfig as CONFIG
import spotifyutils as UTILS
from pathlib import Path
from spotipy.oauth2 import SpotifyOAuth

scope='user-library-read playlist-read-private playlist-modify-private'
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope, client_id=AUTH.clientId, client_secret=AUTH.clientSecret, redirect_uri=AUTH.redirectURI))
user = sp.me()

collection = set()

# CONFIG.CleanupFiles()
if (Path(CONFIG.TRACKS_FROM_PLAYLISTS).is_file()):
    with open(CONFIG.TRACKS_FROM_PLAYLISTS) as file:
        while line := file.readline():
            if (line.rstrip() != ''):
                collection.add(line.rstrip())
else:
    playlists = sp.user_playlists(user['id'])
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
                            collection.add(track_uri)
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

collection_track_count = len(collection)
print("~~~~~~~ Collection Track Count :" + str(collection_track_count))

# Calculate the number of playlists needed to store all the tracks
num_playlists = (collection_track_count + CONFIG.PLAYLIST_TRACK_LIMIT - 1) // CONFIG.PLAYLIST_TRACK_LIMIT

# Create the collection of playlists
playlist_collection = []
for i in range(num_playlists):
    playlist_name = f'Playlist Collection {i+1}'
    playlist = sp.user_playlist_create(user['id'], playlist_name, public=False)
    playlist_collection.append(playlist)

print("~~~~~~~ Created Playlist Count :" + str(len(playlist_collection)))

batch_size = 5
current_playlist = 0
current_track = 0
collection = list(collection)

for i in range(num_playlists):
    start_idx = i * CONFIG.PLAYLIST_TRACK_LIMIT
    end_idx = (i+1) * CONFIG.PLAYLIST_TRACK_LIMIT
    print("~~~~~~~~~~ INDX : (" + str(start_idx) + ", " + str(end_idx) + ")")
    tracks_batch = collection[start_idx:end_idx]
    for y in range(0, len(tracks_batch), batch_size):
        try:
            start = y
            end = y + batch_size if y + batch_size < len(tracks_batch) else len(tracks_batch) - 1
            track_batch = tracks_batch[y:y + batch_size]
            # print("LEN TRACKS BATCH : " + str(len(tracks_batch)) + " INDX : (" + str(start) + ", " + str(end) + ")")
            sp.playlist_add_items(playlist_collection[i]['id'], track_batch)
        except Exception as e:
            print("\n".join(track_batch))
    

# def attempt1():
#     batchSize=50
#     list_tracks = list(collection)
#     tracks_left = len(list_tracks)
#     for i in range(tracks_left, 0, batchSize * -1):
#         lower_bound = 0
#         if (i - batchSize > 0):
#             lower_bound = i - batchSize
#         else:
#             lower_bound = 0
#         batch = list_tracks[lower_bound:i]    
#         try:
#             sp.user_playlist_add_tracks(user['id'], playlist_id=all_playlist['id'], tracks=batch)
#         except Exception as e:
#             if ("400" in str(e)):
#                 CONFIG.WriteToFile(CONFIG.ERRORS_FILE, ' '.join(map(str, batch)))
#             elif ("413" in str(e)):
#                 playlist_iteration += 1
#                 all_playlist = sp.user_playlist_create(user['id'], name=playlist_name + str(playlist_iteration), public=False)
#                 sp.user_playlist_add_tracks(user['id'], playlist_id=all_playlist['id'], tracks=batch)
#             else:
#                 print(str(e))