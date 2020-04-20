# SpotifyToYouTubeSongPlaylist
Gets your Spotify Playlist with all the songs and adds it to a youtube playlist

THIS IS JUST A SCRIPT YOU WILL STILL NEED TO SETUP THE SPOTIFY API AND YOUTUBE API

Before running the code:

1. Setup the API's by following the links below.

2. Pip install the Tekore package follow the link below.

3. Download the JSON file for the google API and call it 'client_secret_YouTube.json'

4. Download the InserIntoJsonFile.py and run it.

5. It will put the client id and the client secret into the correct format for the main python file.

6. Open the main python file

7. On line 32 add the id for the YouTube playlist. It needs to be an already existing playlist 

8. On line 42 add the id for the Spotify playlist

9. You should then be able to run the python file and it should work.

The Script uses Spotify and YouTube API linked below:

To set up the YouTube API follow this quickstart link for python:https://developers.google.com/youtube/v3/quickstart/python

To set up the Spotify API follow this quickstart link: https://developer.spotify.com/documentation/web-api/quick-start/

To connect to the Spotify API it uses the Tekore packages: https://pypi.org/project/tekore/

Note: from testing on the google console API you can only add about 60 songs on to the playlist a day if the app is unauthorised that equates to about 250 requests if the app is unauthorised. It resets daily at midnight PDT.

Video of the program execution: https://www.reddit.com/r/Python/comments/g51467/python_program_to_convert_spotify_playlist_into/
