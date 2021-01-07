import sys

import spotipy
import spotipy.util as util

import json
import string
import argparse

def load_tracks():
    with open('tracks.json') as infile:
        track_list = json.load(infile)
        return track_list

def clear_playlist(sp, user, playlist_id):
    done = False

    while not done:
        tracks = sp.playlist_tracks(playlist_id, limit=100, offset=0)
        if len(tracks["items"]) == 0:
            done = True
            continue

        track_list = []
        print("  Removing %d tracks" % len(tracks["items"]))
        for item in tracks["items"]:
            #print(item["track"]["id"])
            track_list.append(item["track"]["id"])
        sp.user_playlist_remove_all_occurrences_of_tracks(user, playlist_id, track_list)

parser = argparse.ArgumentParser()
parser.add_argument("username", help="Spotify username")
parser.add_argument("--playlist", help="Playlist name", default="Inspired by KEXP")
parser.add_argument("--overwrite", help="Overwrite existing playlist", action="store_true")
parser.add_argument("--append", help="Append to existing playlist", action="store_true")
args = parser.parse_args()

scope = 'playlist-modify-public,playlist-modify-private'
token = util.prompt_for_user_token(
            args.username, 
            scope, 
            client_id='CLIENT_ID',
            client_secret='CLIENT_SECRET',
            redirect_uri='http://localhost:8080')

track_list = load_tracks()
playlist_id = None

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    user_id = sp.current_user()["id"]

    playlists = sp.user_playlists(user_id)
    for playlist in playlists["items"]:
        if playlist_id:
            continue
        if playlist["name"] == args.playlist:
            print("Found existing playlist with name %s" % args.playlist)
            if args.overwrite:
                playlist_id = playlist["id"]
                print("Cleaning up existing tracks in playlist")
                clear_playlist(sp, user_id, playlist_id)
            elif args.append:
                playlist_id = playlist["id"]
            else:
                print("Use --overwrite or --append to modify existing playlist")
                exit(0)

    if playlist_id == None:
        print("Creating playlist with name %s" % args.playlist)
        new_playlist = sp.user_playlist_create(user_id, args.playlist, public=True)
        playlist_id = new_playlist["id"]

    #print(playlist_id)

    playlist_tracks = []
    total_tracks = 0

    for track in track_list:
        # skip blanks
        if "spotify_id" in track:
            playlist_tracks.append(track["spotify_id"])
            total_tracks += 1

            # post what we have every 100 tracks
            if len(playlist_tracks) == 100:
                results = sp.user_playlist_add_tracks(user_id, playlist_id, playlist_tracks)
                playlist_tracks = []

    results = sp.user_playlist_add_tracks(user_id, playlist_id, playlist_tracks)

    print("Added %d tracks to playlist %s" % (total_tracks, args.playlist))
else:
    print("Can't get token for", args.username)
