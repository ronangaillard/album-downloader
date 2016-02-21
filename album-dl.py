#!/usr/bin/python

import os
import sys
import requests
import re
import xml.etree.cElementTree as ET
import youtube_dl
from mutagen.easymp4 import EasyMP4
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TIT2
import eyed3
import json
import base64
import unicodedata
import string
import argparse

LAST_FM_API_KEY = '739148a56b222644ce68c68e3851b55a'

validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)


def parse_arg():
    parser = argparse.ArgumentParser(description='Download full music album from the web')
    parser.add_argument('-a', dest='artist', action='store',
                    help='the artist of the album to be downloaded', required=True)
    parser.add_argument('-A', dest='album', action='store',
                    help='the album to be downloaded', required=True)
    parser.add_argument('--version', action='version', version='Album Downloader Version 0.1 by Ronan Gaillard')
    return parser.parse_args()   


def removeDisallowedFilenameChars(filename):
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in cleanedFilename if c in validFilenameChars)


def get_url_of_song(songname):
    payload = {'search_query': songname}
    r = requests.get('http://www.youtube.com/results', params=payload)
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', r.text)
    return "http://www.youtube.com/watch?v=" + search_results[0]
    
 
def download_video(videourl, artist, album, song, track_number, nb_of_tracks):
    #Adds a 0 for the 9 first songs to make a nice file name ;)        
    if len(track_number) == 1:
        formatted_track_number = '0' + track_number
    else:
        formatted_track_number = track_number
        
    #Create directories of artis and album if not exists
    artist_directory = u'C:\\Users\\Ronan\\Music\\' + artist
    album_directory = u'C:\\Users\\Ronan\\Music\\' + artist + '\\' + album
    song = unicode(song)
    absolute_file_path = album_directory + '\\' + formatted_track_number + ' ' +  removeDisallowedFilenameChars(song) +'.m4a' #making a filesafe name

    command_line = 'youtube-dl '
    command_line += '-o temp.%(ext)s '
    command_line += '-f bestaudio '
    command_line += '--exec "ffmpeg -i {} -vn -c:a libvo_aacenc -y temp.m4a " '
    command_line += videourl
    

    
    if not os.path.exists(artist_directory):
        os.makedirs(artist_directory)
        
    if not os.path.exists(album_directory):
        os.makedirs(album_directory)
        
    
        
    print command_line
    
    result = -1
    retry = 0
    
    while result != 0 and retry < 5: 
        result = os.system(command_line)
       
        retry += 1
        
    if retry == 5:
        print 'FATAL ERROR : Unable to download : ' +song
        return
        
    if os.path.exists(absolute_file_path):
        os.remove(absolute_file_path)
    
    print 'moving from temp.m4a to ' + absolute_file_path
    os.rename("temp.m4a", absolute_file_path)
        
    print '\t\tTagging : ' + absolute_file_path
    audio = MP4(absolute_file_path)
    audio['\xa9ART'] = artist #artist
    audio['\xa9alb'] = album
    audio['\xa9nam'] = song
    audio['aART'] = artist #album artist
    audio['trkn'] = [(int(track_number), nb_of_tracks)]
    audio.save()

#to deal with xml encoded in UTF-8
reload(sys)
sys.setdefaultencoding('utf-8')

args = parse_arg()

print 'Desired artist : ' + args.artist
print 'Desired artist : ' + args.album

print 'Contacting Last.fm to get album info...'
payload = {'api_key': LAST_FM_API_KEY, 'artist': args.artist, 'album': args.album}

response = requests.get('http://ws.audioscrobbler.com/2.0/?method=album.getInfo', payload)
print 'Done, parsing...'
tree = ET.ElementTree(ET.fromstring(response.text))
print 'Album information :'
#print response.
album = tree.find('album/name').text
artist = tree.find('album/artist').text
nb_of_tracks = len(tree.find('album/tracks'))
print 'Album :', album
print 'Artist :', artist
print 'Number of tracks :', nb_of_tracks
print 'Album songs :'
for song in tree.find('album/tracks'):
    song_name = song.find('name').text
    track_number = song.attrib['rank']
    print '\t' + track_number + ' - ' + song_name
    print '\t\tGetting url of song...'
    songurl = get_url_of_song(artist + ' ' + song_name)
    print '\r\t\tDownloading song...'
    download_video(songurl, artist, album, song_name, track_number, nb_of_tracks)
    
    
    
