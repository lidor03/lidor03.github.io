#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import json
import os
import re
import sys
import time

import requests

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from musixmatch import Musixmatch


def get_spotify_client():
    client_credentials_manager = SpotifyClientCredentials('YOUR_SPOTIFY_USER',
                                                          'YOUR_SPOTIFY_PASSWORD')
    spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    return spotify


def create_dictionary_from_json():
    json_dictionary = {}
    with open("places.json", 'r', encoding='utf-8') as json_file:
        json_str = json_file.read()
        splitted = re.findall("\{(.*?)\}", json_str, re.DOTALL)
        for splitted_str in splitted:
            tmp_str = splitted_str.replace("\n", "")
            tmp_str = tmp_str.replace("    ", "")
            artist_and_places = tmp_str.split(": ")
            places = ast.literal_eval(artist_and_places[1])
            places = [n.strip() for n in places]
            full_song_name = artist_and_places[0].replace("\"", "")
            full_song_name = full_song_name.replace("'", "")
            json_dictionary[full_song_name] = {"places": places}
    json_file.close()
    return json_dictionary


def get_artist_name(json_dictionary):
    directory = 'lyrics'
    for song_file in os.listdir(directory):
        last_underscore_place = song_file.rindex("_")
        cleared_file_name = song_file[0:last_underscore_place]
        cleared_file_name = cleared_file_name.replace("_", " ")
        cleared_file_name = cleared_file_name.replace("\"", "")
        cleared_file_name = cleared_file_name.replace("'", "")
        if cleared_file_name in json_dictionary.keys():
            first_underscore_place = song_file.index("_")
            artist_name = song_file[0:first_underscore_place]
            json_dictionary[cleared_file_name]["artist"] = artist_name
    return json_dictionary


def get_artist_id_spotify(json_dictionary):
    spotify = get_spotify_client()
    artists_dictionary = {}
    for key in json_dictionary.keys():
        artist = json_dictionary[key]["artist"]
        results = spotify.search(artist, type='artist')
        if results["artists"]["total"] > 0:
            artist_uri = results["artists"]["items"][0]["uri"]
            if artist not in artists_dictionary.keys():
                artists_dictionary[artist] = artist_uri
            json_dictionary[key]["artist_uri"] = artists_dictionary[artist]
    return json_dictionary


def add_data_from_stereo_ve_mono(artist, song_name, key, json_dictionary):
    time.sleep(0.5)
    r = requests.post("http://stereo-ve-mono.com/wp-admin/admin-ajax.php",
                      data={'action': "advancesearch_ajax", 'artist': "", 'title': "", 'participant': "",
                            'label': "", 'catalog': "", 'song': song_name, 'sendid': "0", 'singer': artist,
                            'editionfrom': "", 'editionto': "", 'page': '1'})
    spllited = re.findall("\<h3>(.*?)\</h3>", r.text)
    if len(spllited) == 0:
        r = requests.get("http://stereo-ve-mono.com/?s=" + key.replace(" ", "+"))
        spllited = re.findall("\<h3><a(.*?)\</a></h3>", r.text)
        if len(spllited) == 0:
            return False
    year = sys.maxsize
    for data in spllited:
        str = (re.findall("\((\d+)\)", data))
        if len(str) > 0:
            found_year = (int(str[0]))
            if year > found_year:
                year = found_year
    if year == sys.maxsize:
        return False
    json_dictionary[key]["year"] = year
    return True


def add_data_from_musixmatch(artist, song_name, key, json_dictionary):
    musixmatch = Musixmatch('YOUR_MUSIXMATCH_ID')
    song_data = (musixmatch.matcher_track_get(q_artist=artist, q_track=song_name, _format="json"))
    if song_data["message"]["header"]["status_code"] == 200:
        album_id = song_data["message"]["body"]["track"]["album_id"]
        album_data = musixmatch.album_get(album_id=album_id, _format="json")
        if album_data["message"]["header"]["status_code"] == 200:
            release_date = album_data["message"]["body"]["album"]["album_release_date"]
            if len(release_date) < 4 or "invalid" in release_date:
                return
            else:
                year = release_date[0:4]
                json_dictionary[key]["year"] = year
    else:
        return


def get_years_from_other_resource(json_dictionary, key):
    artist = json_dictionary[key]["artist"]
    song_name = key.replace(artist + " ", "")
    if add_data_from_stereo_ve_mono(artist, song_name, key, json_dictionary):
        return
    else:
        add_data_from_musixmatch(artist, song_name, key, json_dictionary)


def get_data_for_songs(json_dictionary):
    #  We'll take the following fields from the spotify query:
    #  Year, album photo and link to song preview (if available)
    i = 0
    spotify = get_spotify_client()
    for key in json_dictionary.keys():
        if "artist_uri" in json_dictionary[key]:
            results = spotify.search(key)
            if results["tracks"]["total"] > 0:
                release_year = sys.maxsize
                for item in results["tracks"]["items"]:
                    for artist in item["artists"]:
                        if artist["uri"] == json_dictionary[key]["artist_uri"]:
                            year = item["album"]["release_date"][0:4]
                            if release_year > int(year):
                                release_year = int(year)
                                if "images" in item["album"]:
                                    if len(item["album"]["images"]) > 1:
                                        json_dictionary[key]["album_photo"] = item["album"]["images"][0]["url"]
                                    else:
                                        json_dictionary[key]["album_photo"] = item["album"]["images"]["url"]
                                if "preview_url" in item:
                                    json_dictionary[key]["preview_url"] = item["preview_url"]
                                #  Song uri - to create playlist of songs about place
                                json_dictionary[key]["song_uri"] = item["uri"]
                            json_dictionary[key]["year"] = release_year
            else:
                get_years_from_other_resource(json_dictionary, key)
        else:
            get_years_from_other_resource(json_dictionary, key)
        i += 1
        if i % 100 == 0:
            with open("places_with_data.json", 'w', encoding='utf-8') as json_file:
                json.dump(json_dictionary, json_file, ensure_ascii=False, indent=4)
            json_file.close()
        with open("places_with_data.json", 'w', encoding='utf-8') as json_file:
            json.dump(json_dictionary, json_file, ensure_ascii=False, indent=4)
        json_file.close()
        

def main():
    get_data_for_songs(get_artist_id_spotify(get_artist_name(create_dictionary_from_json())))


if __name__ == '__main__':
    main()
