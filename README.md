# SpotifyToYouTubeSongPlaylist
Gets your Spotify Playlist with all the songs and adds it to a youtube playlist

**THIS IS JUST A SCRIPT YOU WILL STILL NEED TO SETUP THE SPOTIFY API AND YOUTUBE API**

## Before running the code:

1. Setup the API's by following the links below.

2. Pip install the Tekore package follow the link below.

3. Download the JSON file for the google API and call it 'client_secret_YouTube.json'

4. Download the InserIntoJsonFile.py and run it.

5. It will put the client id and the client secret into the correct format for the main python file.

6. Run the python file.

7.When it runs go to the link and authorise the app and then copy the code into the program

8. When it asks for the YouTube id go to YouTube and got to a pre existing playlist and copy the url after "list=" and enter it.

9. When it asks for the Spotify playlist api id go to the playlist you want to convert to the YouTube playlist and go to more then share and copy the spotify URI It should look similar to this: "spotify:playlist:5EKf2UHdSIDE5oi8STVA8B"  

10. Then copy it into the box and delete "spotify:playlist:" and press enter.

11. It should then work.

## The Script uses Spotify and YouTube API linked below:

To set up the YouTube API follow this quickstart link for python [here](https://developers.google.com/youtube/v3/quickstart/python)

To set up the Spotify API follow this quickstart link [here](https://developer.spotify.com/documentation/web-api/quick-start/)

To connect to the Spotify API it uses the Tekore packages: https://pypi.org/project/tekore/

Note: from testing on the google console API you can only add about 60 songs on to the playlist a day if the app is unauthorised that equates to about 250 requests if the app is unauthorised. It resets daily at midnight PDT.

Video of the program execution: https://www.reddit.com/r/Python/comments/g51467/python_program_to_convert_spotify_playlist_into/

## Versions: 

**Does not work with tekore version 2.0.0 and up. (Was built around version 1.7.0) **

Works with current latest version of:
google-api-core (1.22.0)
google-api-python-client (1.10.0)
google-auth (1.20.1)
google-auth-httplib2 (0.0.4)
google-auth-oauthlib(0.4.1)

Python: 3.8

## Errors 

If you get: ModuleNotFoundError: No module named 'tekore.util' Then check using pip list that tekore is version is 1.7 or lower. 
