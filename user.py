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


class User:
    """The user class"""

    def auth_youtube(self):
        """initialize and authenticate with Youtube"""
        # Get credentials and create an API client
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

        return googleapiclient.discovery.build(
            self.api_service_name, self.api_version, credentials=credentials
        )

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
        self.playlists = self.spotify.playlists(self.spotify_user_id)
        self.spotify_playlist_ids = [playlist.id for playlist in self.playlists.items]
