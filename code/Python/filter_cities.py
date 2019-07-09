import os
import json


global places_list, suspecious_places_list


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


def filter_songs_without_places():
    # Totally 33854 files filtered here (55073 files left)
    global places_list
    directory = 'lyrics'
    for song_file in os.listdir(directory):
        place_found = False
        file = open(directory + '/' + song_file)
        song_text = file.read()
        song_text.replace("-", " ")  # Replace - with space in order to find places name easily
        for place in places_list:
            if place in song_text:
                place_found = True
                break
        if not place_found:
            os.remove(directory + '/' + song_file)
        else:
            os.rename(directory + '/' + song_file, directory + '/' + song_file.replace(' ', '_'))


def run_tagger_and_delete():
    # This function will run the tagger and will remove files without places (I_LOC)
    directory = 'lyrics'
    for song_file in os.listdir(directory):
        new_song_file = "'" + song_file.replace("'", "'\\''") + "'"
        file_name = directory + '/' + new_song_file
        song_file_tagged = new_song_file.replace('.txt', '_tagged.txt')
        if not (os.path.isfile('lyrics_tagged/' + song_file_tagged) or os.path.isfile('suspecious_tagged/' + song_file_tagged)):
            os.system('cp ' + file_name + ' ../tagger/tagger/a.txt')
            os.chdir('../tagger/tagger/')
            os.system('java -Xmx1200m -cp trove-2.0.2.jar:morphAnalyzer.jar:opennlp.jar:gnu.jar:chunker.jar:splitsvm.jar:duck1.jar:tagger.jar:. NewDemo ./ a.txt a_tagged.txt')
            tagged_file = 'a_tagged.txt'
            file = open(tagged_file)
            os.chdir('../../Project')
            if 'I_LOC' not in file.read():
                os.remove(directory + '/' + song_file)
                file.close()
            else:
                file.close()
                os.system('cp ../tagger/tagger/a_tagged.txt lyrics_tagged/' + song_file_tagged)
                os.system('mv --backup lyrics/' + new_song_file + ' lyrics_after/' + new_song_file)
        else:
            os.system('mv --backup lyrics/' + new_song_file + ' lyrics_after/' + new_song_file)  # temporary here todo: delete


def filter_songs_with_i_loc():
    #  This function will filter songs with I_LOC, We want to check that the I_LOCs are actually in
    #  the places list, otherwise We'll delete It. For example: We found that שבגדה tagged גדה as I_LOC
    #  and It's not in the places list.
    global places_list, suspecious_places_list
    directory = 'lyrics_tagged'
    songs_with_places_dictionary = {}
    for song_file_tagged in os.listdir(directory):
        file_name = directory + '/' + song_file_tagged
        file = open(file_name)
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
        if len(found_places_array) == 0:
            os.remove(file_name)
            try:
                os.remove('lyrics/'+song_file_tagged.replace('_tagged', ''))
            except FileNotFoundError as e:
                pass
        a_set = set(found_places_array)
        b_set = set(suspecious_places_list)
        if a_set & b_set:
            new_song_file = "'" + file_name.replace("'", "'\\''") + "'"
            new_song_file_tagged = "'" + song_file_tagged.replace("'", "'\\''") + "'"
            os.system('mv --backup ' + new_song_file + ' suspecious_tagged/' + new_song_file_tagged)
        else:
            song_file_name_non_tagged = song_file_tagged.replace('_tagged.txt', '.txt')
            last_underscore_place = song_file_name_non_tagged.rindex("_")
            cleared_file_name = song_file_name_non_tagged[0:last_underscore_place]
            cleared_file_name = cleared_file_name.replace("_", " ")
            songs_with_places_dictionary[cleared_file_name] = found_places_array
            with open("places.json", 'a', encoding='utf-8') as json_file:
                json.dump(songs_with_places_dictionary, json_file, ensure_ascii=False, indent=4)
            json_file.close()
            songs_with_places_dictionary = {}


def main():
    global places_list
    create_places_ds()
    create_suspecious_places_ds()
    filter_songs_without_places()
    run_tagger_and_delete()
    filter_songs_with_i_loc()


if __name__ == '__main__':
    main()
