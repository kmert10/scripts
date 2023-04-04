import spotipy
import spotifyconfig as CONFIG

'''
Gathers user's all `Liked Songs` into one playlist.
TODO: If count of tracks exceed playlist limit, create a new playlist to continue. 

Params:
  - sp : spotipy.Spotify client (Authenticated)
'''
def GatherAllLikedSongs(sp):
    user = sp.current_user()['id']

    # Create a new playlist for the Liked Songs
    liked_songs_playlist = sp.user_playlist_create(user, 'Liked Songs', public=True)

    # Add all of the Liked Songs to the new playlist
    liked_songs = []
    results = sp.current_user_saved_tracks(limit=50)
    while results['items']:
        for item in results['items']:
            liked_songs.append(item['track']['uri'])
        results = sp.current_user_saved_tracks(limit=50, offset=len(liked_songs))

    # Add the Liked Songs to the playlist in batches of 100
    for i in range(0, len(liked_songs), 100):
        sp.playlist_add_items(liked_songs_playlist['id'], liked_songs[i:i+100])

'''
Creates enough playlists to fit all tracks in the collection.

Params:
  - sp : spotipy.Spotify client (Authenticated)
  - trackCount : Number of total tracks in the collection

Returns:
  - playlist_collection : List of playlists created
'''
def CreateCollectionPlaylists(sp: spotipy.Spotify, trackCount):
    # Calculate the number of playlists needed to store all the tracks
    num_playlists = (trackCount + CONFIG.PLAYLIST_TRACK_LIMIT - 1) // CONFIG.PLAYLIST_TRACK_LIMIT

    # Create the collection of playlists
    playlist_collection = []
    for i in range(num_playlists):
        playlist_name = f'Playlist Collection {i+1}'
        playlist = sp.user_playlist_create(sp.me(), playlist_name, public=True)
        playlist_collection.append(playlist)

    return playlist_collection
