import contextlib
from unicodedata import name
from tekore import Spotify, request_client_token, scope

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import time
import json
import os
from googleapiclient.errors import HttpError
from http_requests import prevent_429
import arrow
from song import Song

from playlist import Playlist


class User:
    """The user class"""

    def auth_youtube(self):
        """initialize and authenticate with Youtube"""
        # Get credentials and create an API client
        # check if the cache is recent enough to use
        refresh_token = None
        if os.path.exists("youtube_auth_cache.json"):
            with open("youtube_auth_cache.json") as f:
                cache = json.load(f)
                if (arrow.get(cache["last_updated"]) - arrow.now()).days < 7:

                    refresh_token = cache["refresh_token"]

        port = os.environ.get("PORT", 8080)
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            self.client_secrets_file, self.scopes
        )
        try:
            credentials = flow.run_local_server(port=port)
        except OSError:
            port = int(port) + 1
            print(f"The server is still running, trying port {port}")

            credentials = flow.run_local_server(port=port)

        auth = googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=credentials
        )

        with open("youtube_auth_cache.json", "w") as f:

            keys = [_attr for _attr in dir(credentials) if not _attr.startswith("_")]
            auth_dict = {key: str(getattr(credentials, key)) for key in keys}
            auth_dict["last_updated"] = arrow.now().isoformat()
            json.dump(auth_dict, f)
        return auth

    def __init__(
        self,
        spotify_user_id=1246244579,
        spotify_json="client_codes_Spotify.json",
    ):
        """initialize User Info"""
        self.auth_status = False
        self.scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]

        self.api_service_name = "youtube"
        self.api_version = "v3"
        self.client_secrets_file = "client_secret_YouTube.json"
        self.spotify_user_id = spotify_user_id
        self.spotify_json = spotify_json
        with open("client_codes_Spotify.json") as f:
            client_codes = json.load(f)

        self.app_token = prevent_429(
            func=request_client_token,
            client_id=str(client_codes["client_id"]),
            client_secret=str(client_codes["client_secret"]),
        )
        self.spotify = Spotify(self.app_token)
        self.youtube = self.auth_youtube()
        if os.path.exists("spotify_playlist_cache.json"):
            with open("spotify_playlist_cache.json") as f:
                try:
                    playlists = json.load(f)
                except Exception:
                    playlists = {}
                if (
                    len(playlists) > 1
                    and (arrow.get(playlists.get("last_updated")) - arrow.now()).days
                    < 7
                ):
                    self.playlists = playlists
                    self.spotify_playlist_ids = [
                        playlist["item"]["id"] for playlist in self.playlists["items"]
                    ]

        else:
            self.playlists = self._get_current_spotify()

    def _get_current_spotify(self):  # sourcery skip: dict-assign-update-to-union
        next_page = True
        limit = 50
        offset = 0
        playlists = {"playlists": []}

        while next_page:
            pl = self.spotify.playlists(
                self.spotify_user_id, limit=limit, offset=offset
            )
            pl_json = json.loads(pl.json())

            if pl.offset + limit >= pl.total:
                next_page = False
            playlists["playlists"].extend(pl_json["items"])
            offset += limit
        self.spotify_playlist_ids = [
            playlist["id"] for playlist in playlists["playlists"]
        ]

        for pl in playlists["playlists"]:
            tracks = []
            playlist = Playlist(spotify_id=pl["id"], spotify=self.spotify)

            for tune in playlist.tracks:
                song = Song(
                    spotify_playlist_id=pl["id"],
                    spotify=self.spotify,
                    spotify_meta_data=tune,
                )
                tracks.append(
                    {
                        "artist_name": song.artist_name,
                        "track_name": song.track_name,
                        "album_name": song.album_name,
                        "track_id": pl["id"],
                    }
                )
            pl["tracks"] = tracks

        with open("spotify_playlist_cache.json", "w") as f:
            playlists["last_updated"] = arrow.now().isoformat()
            json.dump(playlists, f)
        return playlists
