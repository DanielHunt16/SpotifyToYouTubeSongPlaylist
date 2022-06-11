from SpotifyToYouTube import User, SpotifyPlaylists, YoutubePlaylists, Playlist, Song
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import json


def __main__():
    """Main function"""
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    user = User()
    user.auth_youtube()
    spotify_playlists = SpotifyPlaylists()
    youtube_playlists = YoutubePlaylists()
    spotify_playlist_ids = spotify_playlists.spotify_playlist_ids
    for spotify_playlist_id in spotify_playlist_ids:
        playlist = Playlist(spotify_playlist_id, user.spotify)
        youtube_playlist_id = playlist.get_youtube_id(youtube_playlists)
        if youtube_playlist_id is None:
            youtube_playlist_id = youtube_playlists.create(playlist.name)
        playlist.place_in_playlist(youtube_playlist_id)


if __name__ == "__main__":
    __main__()
