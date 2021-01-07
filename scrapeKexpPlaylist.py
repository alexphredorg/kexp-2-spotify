import json
import requests
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("showname", help="KEXP show name to scrape")
args = parser.parse_args()

showid_list = []

print("Getting show list")
show_list_url = "https://api.kexp.org/v2/shows/"
params = dict(
    format='json',
    limit='5000'
)
resp = requests.get(url=show_list_url, params=params)
show_list = resp.json()

# build the showid_list in reverse order of how we downloaded the list
for result in show_list["results"]:
    showid = result.get("id")
    name = result.get("program_name")
    date = result.get("start_time")
    if name == args.showname:
        print(showid, name, date)
        showid_list.insert(0, showid)

show_playlist_url = "https://api.kexp.org/v2/plays/"
track_list = []

# now download tracks for each show
for showid in showid_list:
    print("Getting tracks for show %d" % showid)
    params = dict(
        show_ids=showid,
        ordering='-airdate',
        format='json',
        limit='1000'
    )
    resp = requests.get(url=show_playlist_url, params=params)
    data = resp.json()
    for playlist_result in data["results"]:
        artist = playlist_result.get("artist")
        song = playlist_result.get("song")
        album = playlist_result.get("album")
        track_info = dict(
            artist=artist,
            song=song,
            album=album
        )
        #print(track_info)
        if song != None:
            track_list.append(track_info)

# write the output
with open("tracks.json", "w", encoding="utf-8") as outfile:
    json.dump(track_list, outfile)
    print("Wrote tracks.json")



