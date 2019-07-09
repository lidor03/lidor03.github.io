import os
import json


def which_places_in_the_song(name_of_song, old_file_name, file_name, new_song_file):
    songs_with_places_dictionary = {}
    places_input = input()
    places_list = places_input.split(',')
    if len(places_input) == 0:
        os.remove(old_file_name)
    else:
        songs_with_places_dictionary[name_of_song] = places_list
        os.system('mv --backup ' + file_name + ' lyrics_tagged_was_suspecious/' + new_song_file)
        with open("places.json", 'a', encoding='utf-8') as json_file:
            json.dump(songs_with_places_dictionary, json_file, ensure_ascii=False, indent=4)
        json_file.close()


def main():
    directory = 'suspecious_tagged'
    for song_file in os.listdir(directory):
        new_song_file = "'" + song_file.replace("'", "'\\''") + "'"
        file_name = directory + '/' + song_file
        song_file_name_non_tagged = song_file.replace('_tagged.txt', '.txt')
        if os.path.isfile('lyrics_after/' + song_file_name_non_tagged):
            os.system('kate ' + directory + '/' + new_song_file)
            last_underscore_place = song_file_name_non_tagged.rindex("_")
            cleared_file_name = song_file_name_non_tagged[0:last_underscore_place]
            cleared_file_name = cleared_file_name.replace("_", " ")
            which_places_in_the_song(cleared_file_name, file_name, directory + '/' + new_song_file, new_song_file)


if __name__ == '__main__':
    main()
