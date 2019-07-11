import json
import random


#  Since We have more than one place with the same longitude and latitude, We want to be able to see all the places
#  on the map. In order to do so, We need to change the longitude and latitude a little bit.

def main():
    with open('places_with_data_and_lon_lat.json', 'r') as JSON:
        json_dictionary = json.load(JSON)
    for key in json_dictionary.keys():
        places = json_dictionary[key]["places"]
        for place in places:
            place["longitude"] += random.uniform(0.00001, 0.00009)
            place["latitude"] += random.uniform(0.00001, 0.00009)
    with open("places_with_data_and_lon_lat.json", 'w', encoding='utf-8') as json_file:
        json.dump(json_dictionary, json_file, ensure_ascii=False, indent=4)
    json_file.close()


if __name__ == '__main__':
    main()
