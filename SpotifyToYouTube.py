# Before running the code read the README
from tekore.util import request_client_token
from tekore import Spotify, util, scope
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
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
    client_secrets_file, scopes)
credentials = flow.run_console()
youtube = googleapiclient.discovery.build(
    api_service_name, api_version, credentials=credentials)

with open("client_codes_Spotify.json") as f:
    client_codes = json.load(f)

client_id = str(client_codes["client_id"])
client_secret = str(client_codes["client_secret"])

app_token = request_client_token(client_id, client_secret)
playlistid = ""  # YouTube Playlist id goes here
loopnum = 0
attempts = 0


#  Gets the name and artist of the songs in a spotify playlist and stores it in variable
def GetSongSpotify(app_token):
    global loopnum
    global attempts
    spotify = Spotify(app_token)
    playlist = spotify.playlist('')  # Spotify pLaylist id goes here
    WhileLoop = True
    while WhileLoop:
        try:
            track = spotify.playlist_tracks(playlist.id).items[loopnum].track
            song = track.name
            artist = track.artists
            artist = artist[0]
            artist = artist.name
            full = str(song) + ' by ' + str(artist)
            print(str(loopnum + 1) + '. ' + full)
            GetSongYouTube(full)

        except IndexError:
            WhileLoop = False
            print("Completed Successfully")


# searches the name of the song by the artist and get the first video on the lists id
def GetSongYouTube(full):
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
    time.sleep(3)
    PlaceInPlaylist(videoid, playlistid,full)


# Using the id from the previous function places that in the playlist
def PlaceInPlaylist(videoid, playlistid, full):
    global loopnum
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
        loopnum += 1
        attempts = 0

    except googleapiclient.errors.HttpError as e:
        print(e)
        attempts += 1
        if attempts > 6 or attempts == 6:
            print(full + " failed to add to playlist. The song has been skipped")
            with open("response.txt", "w") as f1:
                f1.write(str(full))
                f1.write("\n")

            loopnum += 1
        else:
            pass


GetSongSpotify(app_token)
