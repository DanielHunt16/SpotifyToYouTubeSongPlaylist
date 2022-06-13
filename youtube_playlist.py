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
import arrow
from http_requests import prevent_429


class YoutubePlaylists:
    """Class for all the users Youtube playlists"""

    def __init__(self, youtube):  # sourcery skip: identity-comprehension
        self.youtube = youtube
        self.time_to_wait = 1
        self.last_time_created = arrow.now().isoformat()
        self.as_dict, self.ids, self.names = self.get_youtube_playlists()

    def get_youtube_playlists_from_cache(self):
        """Gets the youtube playlists from the cache"""
        if not os.path.exists("youtube_playlists.json"):
            return None
        try:
            with open("youtube_playlists.json") as f:
                youtube_playlist_cache = json.load(f)
                if youtube_playlist_cache["playlist_count"] > 0:
                    return None
                return youtube_playlist_cache
        except json.JSONDecodeError:
            return None

    def get_youtube_playlists(self):
        """Gets all the users Youtube playlists"""

        # try to get the playlists from the cache
        youtube_playlists = self.get_youtube_playlists_from_cache()
        time_since_cached = (
            arrow.get(youtube_playlists.get("last_updated")) - arrow.now()
        )
        if (
            youtube_playlists is not None
            and len(youtube_playlists) > 0
            and youtube_playlists["playlist_count"] > 0
        ):
            return (
                youtube_playlists,
                [playlist["id"] for playlist in youtube_playlists],
                [playlist["name"] for playlist in youtube_playlists],
            )
        if time_since_cached.days > 1 or youtube_playlists["playlist_count"] == 0:
            youtube_playlists, _ids, _names = self._get_current_youtube()
            return (
                youtube_playlists,
                _ids,
                _names,
            )

    def _get_current_youtube(self):
        names = []
        ids = []
        next_page = True
        page = 1
        while next_page:
            request = self.youtube.playlists().list(
                part="snippet", maxResults=50, mine=True, pageToken=page
            )

            response = prevent_429(func=request.execute)
            if response["pageInfo"] > 50:
                next_page = True
                page += 1
            else:
                next_page = False
            page_results = response["items"]

            for page_result in page_results:
                names.append(page_result["snippet"]["title"])
                ids.append(page_result["id"])
        youtube_playlist_dict = dict(zip(names, ids))
        if youtube_playlist_dict:
            youtube_playlist_dict["last_updated"] = arrow.now().isoformat()
            youtube_playlist_dict["playlist_count"] = len(youtube_playlist_dict)
            # save the playlist names and ids to a json file
            with open("youtube_playlists.json", "w") as f:
                json.dump(youtube_playlist_dict, f)
        return youtube_playlist_dict, ids, names

    def create(self, name):
        """Creates a new Youtube playlist"""
        if name in self.names:
            print(f"Playlist {name} already exists")
            return self.as_dict[name]

        request = self.youtube.playlists().insert(
            part="snippet,status",
            body={
                "snippet": {
                    "title": name.title().replace(" ", "-"),
                },
                "status": {"privacyStatus": "public"},
            },
        )
        try:
            response = request.execute()
            self.last_time_created = arrow.now().isoformat()
            return response.get("id")
        except HttpError:
            print("An HTTP error occurred:\n")
            # calculate the time to wait
            self.time_to_wait = (
                arrow.now() - arrow.get(self.last_time_created)
            ).seconds * 0.5
            print(f"Waiting {self.time_to_wait} seconds before trying again")
            time.sleep(self.time_to_wait)
            self.create(name)
