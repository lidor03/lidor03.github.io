import os
import json
from googletrans import Translator

global suspected_cities_translate, suspected_names, places_list, suspecious_places_list


def create_places_ds():
    global places_list
    dictionary_file = open('Dictionary.txt')
    places_list = []
    line = dictionary_file.readline()
    while "LOC" in line:
        places_list.append(line[4:(len(line) - 1)])
        line = dictionary_file.readline()
    dictionary_file.close()


def create_suspecious_places_ds():
    global suspecious_places_list
    suspecious_file = open('Suspecious_places.txt', encoding='utf-8-sig')
    suspecious_places_list = []
    line = suspecious_file.readline()
    while line:
        suspecious_places_list.append(line.replace('\n', ''))
        line = suspecious_file.readline()
    suspecious_file.close()


def cretate_suspected_cities_translate_ds():
    global suspected_cities_translate
    suspected_cities_file = open('Suspecious_places_not_names.txt', encoding='utf-8-sig')
    suspected_cities_translate = {}
    line = suspected_cities_file.readline()
    while line:
        splitted_line = line.split(":")
        suspected_cities_translate[splitted_line[0]] = splitted_line[1].replace("\n", "")  # cleaning \n
        line = suspected_cities_file.readline()
    suspected_cities_file.close()


def cretate_suspected_names_ds():
    global suspected_names
    suspected_names_file = open('Suspecious_names.txt', encoding='utf-8-sig')
    suspected_names = []
    line = suspected_names_file.readline()
    while line:
        suspected_names.append(line.replace('\n', ''))
        line = suspected_names_file.readline()
    suspected_names_file.close()


def suspecious_first_name_exists(song_string):
    for name in suspected_names:
        if name in song_string:
            return True
    return False


def find_suspecious_cities(song_string):
    suspecious_cities = []
    for suspected_city in suspected_cities_translate.keys():
        if suspected_city in song_string:
            suspecious_cities.append(suspected_city)
    return suspecious_cities


def find_place_to_cut(str, index):
    if str[index] == '\n':
        return index
    return find_place_to_cut(str, index - 1)


def translate_song(song_string):
    translator = Translator(service_urls=['translate.google.com', 'translate.google.co.il'])
    if len(song_string) > 2500:
        place_to_cut = find_place_to_cut(song_string, 2200)
        translation = translator.translate(song_string[0:place_to_cut].replace("\n", ". "), dest='en', src='iw')
        translation2 = translator.translate(song_string[place_to_cut+1:].replace("\n", ". "), dest='en', src='iw')
        text = translation.text + translation2.text
    else:
        translation = translator.translate(song_string.replace("\n", ". "), dest='en', src='iw')
        text = translation.text
    return text


def translate_song_and_find_suspecious_places(song_string, suspecious_cities):
    cities_found = []
    text = translate_song(song_string)
    if "Sderot" in text:
        replaced_song_string = song_string.replace("שדרות", "רחובות")
        replaced_text = translate_song(replaced_song_string)
        if "Rehovot" not in replaced_text:
            text = replaced_text

    for city in suspecious_cities:
        if suspected_cities_translate[city] in text:
            cities_found.append(city)
    return cities_found


def create_cities_data_for_song(tagged_file_name):
        file = open("suspecious_tagged/" + tagged_file_name)
        dictionary_list = []
        line = file.readline()
        #  Skip over the first cell in the array - הרכבת הממשלה
        while line:
            if line.startswith('\t'):
                splitted = line.replace('\t', '').split(': ')
                dictionary = {splitted[0]: splitted[1].replace('\n', '')}
                line = file.readline()
                while line and ':' in line:
                    splitted = line.replace('\t', '').split(': ')
                    if len(splitted) > 1:
                        dictionary[splitted[0]] = splitted[1].replace('\n', '')
                    line = file.readline()
                dictionary_list.append(dictionary)
            line = file.readline()
        found_places_array = []
        came_from_I_LOC = False
        str = ""
        for block_data in dictionary_list:
            if block_data.get('NER') == 'I_LOC':
                place = block_data.get('Lemma')
                if not came_from_I_LOC:
                    try:
                        place = place[place.rindex('^') + 1:]
                    except ValueError as e:
                        pass
                else:
                         place = str + ' ' + place
                if place in places_list:
                    if place not in found_places_array:
                        found_places_array.append(place)
                else:
                    came_from_I_LOC = True
                    str = place
            else:
                came_from_I_LOC = False
                str = ""

        a_set = set(found_places_array)
        b_set = set(suspecious_places_list)
        return list(a_set - b_set)


def decide_for_suspecious():
    songs_with_places_dictionary = {}
    directory = 'suspecious_tagged'
    for song_file in os.listdir(directory):
        new_song_file = "'" + song_file.replace("'", "'\\''") + "'"
        file_name = directory + '/' + new_song_file
        song_file_name_non_tagged = song_file.replace('_tagged.txt', '.txt')
        if (os.path.isfile('lyrics_after/' + song_file_name_non_tagged)):
            song_file_non_tagged = open('lyrics_after/' + song_file_name_non_tagged)
            song_string = song_file_non_tagged.read()
            if suspecious_first_name_exists(song_string):
                song_file_non_tagged.close()
                continue
            else:
                print("in else")
                suspecious_cities = find_suspecious_cities(song_string)
                cities_found = translate_song_and_find_suspecious_places(song_string, suspecious_cities)
                not_suspecious_cities = create_cities_data_for_song(song_file)
                if len(not_suspecious_cities) > 0 and len(cities_found) > 0:
                    cities_found.extend(not_suspecious_cities)
                    song_cities = cities_found
                    print("both not empty ", song_cities)
                elif len(not_suspecious_cities) > 0:
                    song_cities = not_suspecious_cities
                    print("not suspecious ", song_cities)
                elif len(cities_found) > 0:
                    song_cities = cities_found
                    print("suspecious ", song_cities)
                else:
                    print("in else")
                    os.remove('lyrics_after/' + song_file_name_non_tagged)
                    try:
                        os.remove(directory + '/' + song_file)
                    except FileNotFoundError as e:
                        pass
                    continue
                last_underscore_place = song_file_name_non_tagged.rindex("_")
                cleared_file_name = song_file_name_non_tagged[0:last_underscore_place]
                cleared_file_name = cleared_file_name.replace("_", " ")
                songs_with_places_dictionary[cleared_file_name] = song_cities
                os.system('mv --backup ' + file_name + ' lyrics_tagged_was_suspecious/' + new_song_file)
                with open("places.json", 'a', encoding='utf-8') as json_file:
                    json.dump(songs_with_places_dictionary, json_file, ensure_ascii=False, indent=4)
                json_file.close()
                songs_with_places_dictionary = {}
        else:
            os.remove(directory + "/" + song_file)
            continue

def main():
    create_places_ds()
    cretate_suspected_cities_translate_ds()
    cretate_suspected_names_ds()
    create_suspecious_places_ds()
    decide_for_suspecious()


if __name__ == '__main__':
    main()
