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

from song import Song


class Playlist:
    """A class with playlist related state properties"""

    def __init__(self, spotify_id, spotify, youtube=None, youtube_playlists=None):
        self.spotify_id = spotify_id
        self.spotify_playlist = spotify.playlist(spotify_id)
        self.tracks = self.spotify_playlist.tracks.items
        self.name = self.spotify_playlist.name
        self.youtube = youtube
        self.youtube_id = None
        self.youtube_playlist_id = youtube_playlists.create(name=self.name)
        self.spotify = spotify

    def place_songs_in_playlist(self):
        for tune in self.tracks:
            names = tune.track.artists
            if len(names) > 1:
                artist_name = f"{names[0].name} featuring {names[1].name}"
            else:
                artist_name = names[0].name

            song = Song(
                spotify_playlist_id=self.spotify_id,
                playlist_id_youtube=self.youtube_id,
                youtube=self.youtube,
                artist_name=artist_name,
                track_name=tune.track.name,
                spotify=self.spotify,
            )
            song_youtube_id = song.get_song_youtube()
            # checks if the song is already in the playlist

            request = self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": self.youtube_playlist_id,
                        "position": 0,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": song_youtube_id,
                        },
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
                    print(
                        f"{song.full_name} failed to add to playlist. The song has been skipped"
                    )
                    with open(f"{self.name}_response.txt", "w") as f1:
                        f1.write(str(song.full_name))
                        f1.write("\n")
