import json
from googletrans import Translator


def translate_place_name(place_name):
    str_i_went_to = "הלכתי ל"
    translator = Translator(service_urls=['translate.google.com', 'translate.google.co.il'])
    translation = translator.translate(str_i_went_to + place_name, dest='en', src='iw')
    text = translation.text
    return text[10:]


def main():
    with open('places_with_data.json', 'r') as JSON:
        json_dictionary = json.load(JSON)
    for key in json_dictionary.keys():
        places = json_dictionary[key]["places"]
        for i in range(len(places)):
            places[i] = (places[i], translate_place_name(places[i]))
    with open("places_with_data.json", 'w', encoding='utf-8') as json_file:
        json.dump(json_dictionary, json_file, ensure_ascii=False, indent=4)
    json_file.close()


if __name__ == '__main__':
    main()