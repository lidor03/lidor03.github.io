# Project - Topics in Digital humanities, BGU university

We created this project for the course topics in digital humanities in BGU university, guided by Dr. Yael Netzer.

Our project subject is places and cities by years in Hebrew songs.

We used Dr. Meni Adler tagger to create the tagged files.

All the code tried with Ubuntu 16.04 (and some python code also ran on Ubuntu 18.04 and Kubuntu 18.04), with Python 3.5, Java 11, Kate (for step 7) and all the relevant packages were installed also.

(The code will run on Windows but You'll need to change the code little bit)

In order to run the project You need:

1.  Download the files from github.

2.  Create folder for with two sub folders: Project and tagger (please note that It's important to follow the names, since the code is key sensitive).

3.  All the python files need to be placed in Project, Dr. Meni Adler tagger will be placed in tagger folder.

4.  In Project folder create the following folders: lyrics, lyrics_after, lyrics_tagged_was_suspecious and suspecious_tagged.

5.  Move all your songs to lyrics folder and start the process by running filter_cities file. Please note 2 things: A. You should provide songs with the following format name: artist name_song name_number.txt. B. The tagger running is very long process. You may use more than one computer in order to finish this process fastly. (The best option is using cloud computing service like Amazon AWS or equivalent) On i5 4th gen desktop computer with 16GB RAM, You'll be able to tag 4000-5000 songs in 24 hours. On i7 6th gen laptop computer with 8GB RAM, You'll be able to tag 2000-3000 songs in 24 hours.

6.  After You finished the process in step 5, You should run translate_to_english, this process is needed in order to find problematic names and places. It'll translate the songs to English and then You'll be able to solve some of the problems with words like "רחובות" or "שדרות".

7.  After step 6, You may need to iterate over some files manually, this done by the file filter_songs_manually. This step is important for names like Sofia, which can be a person name and also the capital city of Bulgaria. You should scan the file manually and search "LOC" and decide if It should be consider as place/city or not.

A. If You didn't found any place or city in the song, please press enter after closing the file and the process will continue to the next song.

B. If You found only one place or city, please enter It and press enter, then the process will continue.

C. Lastly, if You found more than one place or city, You need to enter them with , and without spaces (For example: תל אביב,ירושלים,באר שבע), then press enter and the process will continue.

8.  Now You have "JSON" file called places, in this file You'll find any song with the mentioned cities and places.

9.  Run add_aritst_to_json. In order to run this code, You need to supply developer user name for Spotify and Musixmatch. 
Please copy the songs lyrics to lyrics folder again.
The code will create a JSON file with the following information: 
Artist and song name as key and Artist, artist_uri (if available), album photo (if available), places, year (if available) and 
additional Spotify information like song_uri and link to preview of the song (if available) as fields. 
Please note that Musixmatch service for free, will allow only up to 2000 querys per day, and each query of song following by query about the album in order to find the year. 
When the process will finish, You'll have JSON file called places_with_data with all the data mentioned above.

10. Copy the JSON created in step 9 into the folders CreateCsvStatistics and CreateJSONLongitudeLatitude, then You'll have CSV statistics and JSON file with longitude and latitude.
11. Copy the file created in CreateJSONLongitudeLatitude, and run It with edit_longitude_latitude.py.

Finally, now You have all the data needed to the website!
