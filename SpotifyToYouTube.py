# Before running the code read the README
import contextlib
from tekore import Spotify, request_client_token, scope
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import time
import json
import pdb


class User:
    """The user class"""

    def __init__(
        self,
        spotify_user_id=None,
        spotify_json="client_codes_Spotify.json",
    ):
        """initialize User stats"""
        self.scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.client_secrets_file = "client_secret_YouTube.json"
        self.spotify_user_id = spotify_user_id
        self.spotify_json = spotify_json
        with open("client_codes_Spotify.json") as f:
            client_codes = json.load(f)

        self.app_token = request_client_token(
            str(client_codes["client_id"]), str(client_codes["client_secret"])
        )
        self.spotify = Spotify(self.app_token)

    def auth_youtube(self):
        """initialize and authenticate with Youtube"""
        # Get credentials and create an API client
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, self.scopes
        )
        try:
            credentials = flow.run_local_server()
        except OSError:
            print("The server is still running, trying again")
            os.kill(os.getpid(8080), 9)
            credentials = flow.run_local_server()

        self.youtube = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=credentials
        )


class Song(User):
    """a class for a song"""

    def __init__(self, spotify_playlist_id=None, playlist_id_youtube=None):
        """initializer doc string"""
        super().__init__()
        self.spotify_playlist_id = spotify_playlist_id
        self.playlist_id_youtube = playlist_id_youtube

    def get_songs_spotify(self, playlist_id_spotify):
        """Gets the songs from a spotify playlist"""
        playlist = self.spotify.playlist_items(playlist_id_spotify, as_tracks=True)
        print(playlist)
        playlist = playlist["tracks"]["items"]
        print(playlist)
        with contextlib.suppress(IndexError):
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

        for songId in songIds:
            track = self.spotify.track(songId, market=None)
            artist = track.artists
            artist = artist[0]
            print(f"{track.name} by {artist.name}")
            self.get_song_youtube(
                f"{track.name} by {artist.name}", self.youtube_playlist_id
            )

    # Searches the name of the song by the artist and get the first video on the lists id
    def get_song_youtube(self, full):
        """Gets the song from youtube"""
        request = self.youtube.search().list(part="snippet", maxResults=1, q=full)
        response = request.execute()

        response = response.get("items")
        response = response[0]
        response = response.get("id")
        self.video_id = response.get("videoId")
        time.sleep(1)
        playlist = Playlist(self.playlist_id_spotify, self.spotify)
        playlist.place_in_playlist(self.video_id, self.playlist_id_youtube, full)


class Playlist(User):
    """A class with playlist related state properties"""

    def __init__(self, spotify_id, spotify):
        super().__init__()
        self.spotify_id = spotify_id
        self.youtube_id = None
        self.spotify_playlist = spotify.playlist_items(self.spotify_id, as_tracks=True)

        self.tracks = self.spotify_playlist["items"]
        import pdb

        pdb.set_trace()
        ## find out what the name is

        self.name = self.spotify_playlist.name

    def get_youtube_id(self, youtubeplaylists):
        """Gets the youtube playlist id"""
        if self.youtube_id is None and self.name in youtubeplaylists:
            self.youtube_id = youtubeplaylists.as_dict[self.name]
        return self.youtube_id

    def place_in_playlist(self, full):
        song = Song()
        song.get_song_youtube(full)
        request = self.youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": self.youtube_id,
                    "position": 0,
                    "resourceId": {"kind": "youtube#video", "videoId": song.video_id},
                }
            },
        )

        try:
            request.execute()
            self.attempts = 0

        except googleapiclient.errors.HttpError as e:
            print(e)
            self.attempts += 1
            if self.attempts > 6 or self.attempts == 6:
                print(f"{full} failed to add to playlist. The song has been skipped")
                with open("response.txt", "w") as f1:
                    f1.write(str(full))
                    f1.write("\n")


class SpotifyPlaylists(User):
    """the spotify playlists class"""

    def __init__(self):
        """A class with playlist related state properties"""
        super().__init__()

        self.spotify_playlist_ids = []
        self.playlists = self.spotify.playlists(self.spotify_user_id)
        self.spotify_playlist_ids.extend(
            playlist.id for playlist in self.playlists.items
        )


class YoutubePlaylists(User):
    """Class for all the users Youtube playlists"""

    def __init__(self):  # sourcery skip: identity-comprehension
        super().__init__()

        self.as_dict = self.get_youtube_playlists()
        self.playlist_ids = [playlist_id for playlist_id in self.as_dict]
        self.playlist_names = [playlist_name for playlist_name in self.as_dict]

    def get_youtube_playlists(self):
        """Gets all the users Youtube playlists"""
        youtube_playlist_names = []
        youtube_playlist_ids = []
        next_page = False
        page = 1
        while next_page:
            request = self.youtube.playlists().list(
                part="snippet", maxResults=50, mine=True, pageToken=page
            )
            response = request.execute()
            if response["pageInfo"] > 50:
                next_page = True
                page += 1
            else:
                next_page = False
            page_results = response["items"]
            for page_result in page_results:
                youtube_playlist_names.append(page_result["snippet"]["title"])
                youtube_playlist_ids.append(page_result["id"])

        if len(youtube_playlist_ids) == 0 or len(youtube_playlist_names) == 0:
            self.as_dict = {}
        else:
            self.as_dict = zip(youtube_playlist_names, youtube_playlist_ids)
        return self.as_dict

    def create(self, playlist_name):
        """Creates a new Youtube playlist"""
        if playlist_name in self.playlist_names:
            print("Playlist already exists")
            return self.playlist_ids[self.playlist_names.index(playlist_name)]
        request = self.youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": playlist_name,
                },
                "status": {"privacyStatus": "public"},
            },
        )
        response = request.execute()
        return response.get("id")
