import requests
import json
import os
import youtube_dl

from secrets import spotify_user_id
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors


class MakePlayList:
    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}

    def youtube_client(self):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secret.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        # from the Youtube DATA API
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube_client

    def liked_video(self):

        request = self.youtube_client.videos().list(
            part="snippet,contentDetails,statistics",
            myRating="like"
        )
        response = request.execute()

        for item in response["items"]:
            youtube_title = item["snippet"]["title"]
            youtube_link = "https://www.youtube.com/watch?v={}".format(
                item["id"])

            video = youtube.dl.YoutubeDL({}).extract_info(
                youtube_link, download=False)
            track = video["track"]
            artist = video["artist"]

            self.all_song_info[youtube_title] = {
                "youtube_link": youtube_link,
                "track": track,
                "artist": artist,
                "spotify_uri": self.spotify_uri(track, artist)
            }

    def make_playlist(self):

        request_body = json.dumps({
            "name": "Youtube videos",
            "description": "Playist from Youtube",
            "public": true
        })

        query = "https://api.spotify.com/v1/users/{}/playlists".format(
            self.user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()

        return response_json["id"]

    def spotify_uri(self, track, artist):

        query = "https://api.spotify.com/v1/search?query=track%3A{}+artist%3A{}&type=track&offset=0&limit=20".format(
            track,
            artist
        )
        response = requests.get(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]
        uri = songs[0]["uri"]

        return uri

    def add_song_to_playlist(self):

        self.liked_video()

        uri = []
        for song, info in self.all_song_info.items():
            uri.append(info["spotify_uri"])

        playlist_id = self.make_playlist
        request_data = json.dumps(uris)

        query = "https://api.spotify.com/v1/playlists/{}/tracks".format(
            playlist_id)

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(self.spotify_token)
            }
        )
        response_json = response.json()
        return response_json
