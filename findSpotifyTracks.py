import sys

import spotipy
import spotipy.util as util

import json
import string

import argparse

global trans_table
trans_table = str.maketrans('', '', string.punctuation)

def remove_punctuation(s):
    return s.translate(trans_table)

def truncate_at_ampersand(s):
    index = s.find('&')
    if index > 0:
        s = s[0:index]
    index = s.find(' x ')
    if index > 0:
        s = s[0:index]
    return s

def truncate_at_feat(s):
    index = s.find('feat')
    if index > 0:
        s = s[0:index-1]
    return s

def remove_between_parens(s):
    """Returns a copy of 'input_str' with any parenthesized text removed. Nested parentheses are handled."""
    result = ''
    paren_level = 0
    for ch in s:
        if ch == '(':
            paren_level += 1
        elif (ch == ')') and paren_level:
            paren_level -= 1
        elif not paren_level:
            result += ch
    return result

def build_spotify_query(artist, song):
    # get artist and song
    artist = truncate_at_ampersand(artist)
    song = remove_between_parens(song)
    song = remove_punctuation(song)

    # build query
    return 'artist:"%s" track:"%s"' % (artist, song)

def load_tracks():
    with open('tracks.json') as infile:
        track_list = json.load(infile)
        return track_list

def save_tracks(track_list):
    with open("tracks.json", "w") as outfile:
        json.dump(track_list, outfile)

parser = argparse.ArgumentParser()
parser.add_argument("username", help="Spotify username")
parser.add_argument("--hidecached", help="Don't display tracks already found on Spotify", action="store_true")
parser.add_argument("--showquery", help="Show the query string being passed to Spotify", action="store_true")
args = parser.parse_args()

scope = 'playlist-modify-public,playlist-modify-private'
token = util.prompt_for_user_token(
            args.username, 
            scope, 
            client_id='CLIENT_ID',
            client_secret='CLIENT_SECRET',
            redirect_uri='http://localhost:8080')

track_list = load_tracks()

if token:
    sp = spotipy.Spotify(auth=token)
    sp.trace = False
    user_id = sp.current_user()["id"]

    updates = 0
    for i in range(0, len(track_list)):
        track = track_list[i]

        artist = track["artist"]
        song = track["song"]

        # skip ones that we've already found on Spotify
        if "spotify_id" in track:
            if not args.hidecached:
                print(song, "by", artist, " -> ", track["spotify_id"], " (cached)")
            continue

        # execute spotify search
        q = build_spotify_query(artist, song)
        results = sp.search(q)
        search_results = results["tracks"]["items"]
        if args.showquery:
            print("Query:", q)
            for result in search_results:
                print("Result:", result["name"], "by", result["artists"][0]["name"])

        if len(search_results) > 0:
            spotify_id = search_results[0]["id"]
            spotify_song = search_results[0]["name"]
            spotify_artist = search_results[0]["artists"][0]["name"]
            #print(search_results[0])
            print(song, "by", artist, " -> ", spotify_song, "by", spotify_artist, "id", spotify_id)
            #print(q, " -> ", track_id)
            track["spotify_id"] = spotify_id
            track["spotify_song"] = spotify_song
            track["spotify_artist"] = spotify_artist
            track_list[i] = track
            updates = updates + 1
            if updates % 100 == 0:
                save_tracks(track_list)
        else:
            print(track["song"], "by", track["artist"], " -> ", "Not Found")

    save_tracks(track_list)
else:
    print("Can't get token for", args.username)
