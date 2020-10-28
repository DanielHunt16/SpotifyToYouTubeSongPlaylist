# Before running the code read the README
from tekore import Spotify, request_client_token, scope
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import time
import json

scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
api_service_name = "youtube"
api_version = "v3"
client_secrets_file = "client_secret_YouTube.json"

# Get credentials and create an API client
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
credentials = flow.run_console()
youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

with open("client_codes_Spotify.json") as f:
    client_codes = json.load(f)

# Initializes Spotify API client codes 
client_id = str(client_codes["client_id"])
client_secret = str(client_codes["client_secret"])
app_token = request_client_token(client_id, client_secret)
playlist_id_youtube = input("Enter the YouTube id")
attempts = 0


# Gets the name of the song and the artist from a spotify playlist
def get_song_spotify(app_token):
    global attempts
    spotify = Spotify(app_token)
    playlist_id_spotify = input("Enter the spotify playlist id")
    playlist = spotify.playlist_items(playlist_id_spotify, as_tracks=True)
    print(playlist)
    playlist = playlist["items"]
    print(playlist)
    try:
        i = 0
        songIds = []
        whileLoop = True
        
        # Gets the song ids from the returned dictionary
        while whileLoop:
            subPlaylist = playlist[i]
            subPlaylist.pop("added_at", None)
            subPlaylist.pop("added_by", None)
            subPlaylist.pop("is_local", None)
            subPlaylist.pop("primary_color", None)
            subPlaylist = subPlaylist["track"]
            subPlaylist.pop("album", None)
            subPlaylist.pop("artists", None)
            subPlaylist.pop("available_markets", None)
            subPlaylist = subPlaylist["id"]
            print(subPlaylist)
            songIds.append(subPlaylist)
            i += 1

    except IndexError:
        pass

    for i in range(len(songIds)):
        track = spotify.track(songIds[i], market=None)
        artist = track.artists
        artist = artist[0]
        print(f"{track.name} by {artist.name}")
        get_song_youtube(f"{track.name} by {artist.name}")


# Searches the name of the song by the artist and get the first video on the lists id
def get_song_youtube(full):
    request = youtube.search().list(
        part="snippet",
        maxResults=1,
        q=full
    )
    response = request.execute()

    response = response.get("items")
    response = response[0]
    response = response.get("id")
    videoid = response.get("videoId")
    time.sleep(1)
    place_in_playlist(videoid, playlist_id_youtube, full)


# Using the id from the previous function places that in the playlist
def place_in_playlist(videoid, playlistid, full):
    global attempts
    request = youtube.playlistItems().insert(
        part="snippet",
        body={
            "snippet": {
                "playlistId": playlistid,
                "position": 0,
                "resourceId": {
                    "kind": "youtube#video",
                    "videoId": videoid
                }
            }
        }
    )

    try:
        response = request.execute()
        attempts = 0

    except googleapiclient.errors.HttpError as e:
        print(e)
        attempts += 1
        if attempts > 6 or attempts == 6:
            print(full + " failed to add to playlist. The song has been skipped")
            with open("response.txt", "w") as f1:
                f1.write(str(full))
                f1.write("\n")
        else:
            pass


get_song_spotify(app_token)
