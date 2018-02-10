from django.http import HttpResponse
import urllib
from django.shortcuts import redirect
from django.shortcuts import render
import requests
import base64
import json
import spotipy
import spotipy.util as util
import os


def get_id_and_secret():
    """
    Reads client id and secret from a file on the local file system.
    """
    try:
        with open('secret', 'r') as file:
            text = file.read()
            client_id = text.split('\n')[0]
            client_secret = text.split('\n')[1]
            print(client_id)
            return client_id, client_secret
    except Exception as e:
        print('cannot find file with id and secret')
        return '', ''


CLIENT_ID, CLIENT_SECRET = get_id_and_secret()

# Redirect URI and scopes used for our application
REDIRECT_URI = 'http://localhost:8000/frogify/queue'
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SCOPE = ('playlist-modify-public playlist-modify-private '
         'user-read-currently-playing user-modify-playback-state '
         'user-read-private playlist-read-private playlist-modify-public '
         'playlist-modify-private ugc-image-upload user-top-read '
         'user-read-recently-played')

# Base url and version number
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)

# Auth query parameters for getting auth token
auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}


def index(request):
    """
    Index route
    """
    return HttpResponse("Hello, world. You're at the polls index.")

"""
Login route. Redirects to a spotify authentication url.
"""
def login(request):

    url = "&".join(["{}={}".format(key, val) for key, val in auth_query_parameters.items()])


def login(request):
    """
    Login route. Redirects to a spotify authentication url.
    """
    url = "&".join(["{}={}".format(key, val) for key, val in auth_query_parameters.items()])

    auth_url = "{}/?{}".format("https://accounts.spotify.com/authorize", url)
    return redirect(auth_url)


def queue(request):
    """
    Redirect uri used upon login. Source: https://github.com/drshrey/spotify-flask-auth-example/blob/master/main.py
    """
    print(repr(SCOPE))
    auth_code = request.GET['code']

    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_code),
        "redirect_uri": REDIRECT_URI
    }

    data_str = "{}:{}".format(CLIENT_ID, CLIENT_SECRET)

    b64_auth_str = base64.urlsafe_b64encode(data_str.encode()).decode()

    headers = {"Authorization": "Basic {}".format(b64_auth_str)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    response_data = json.loads(post_request.text)


    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]
    sp = spotipy.Spotify(auth=access_token)
    playlists = sp.user_playlists('jmkovachi')
    #playlist_id = playlists['items'][10]['id']
    playlist_items = []
    for item in playlists['items']:
        playlist_items.append({
            'href' : item['href'],
            'name' : item['name'],
            })
    #print(playlists['items'][10])
    #print(sp.user_playlist('jmkovachi', playlist_id=playlists['items'][0]['id'], fields='tracks,next'))

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}

    # Get profile data
    #print('{}/users/{}/playlists/{}/tracks'.format(SPOTIFY_API_URL, 'jmkovachi', playlist_id))

    #user_profile_api_endpoint = '{}/users/{}/playlists/{}/tracks'.format(SPOTIFY_API_URL, 'jmkovachi', playlist_id)
    """user_profile_api_endpoint = playlist_hrefs[0]
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)"""

    #print(profile_data)

    print(playlist_items)

    return render(request, 'public/createRoom.html', {'playlists' : playlist_items})

