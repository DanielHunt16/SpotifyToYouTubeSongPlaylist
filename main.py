from youtube_playlist import YoutubePlaylists
from playlist import Playlist
from user import User

import os


def __main__():
    """Main function"""
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    user = User()

    youtube_playlists = YoutubePlaylists(user.youtube)

    for spotify_playlist_id in user.spotify_playlist_ids:
        playlist = Playlist(
            spotify_playlist_id,
            user.spotify,
            youtube=user.youtube,
            youtube_playlists=youtube_playlists,
        )

        playlist.place_songs_in_playlist()


if __name__ == "__main__":
    __main__()
