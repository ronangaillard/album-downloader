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
from subprocess import Popen, PIPE, STDOUT

LAST_FM_API_KEY = '739148a56b222644ce68c68e3851b55a'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)

def printf(text):
    sys.stdout.write(text)

def update_status(song, track_number, status, type=None):
    sys.stdout.write("\033[2K") # Clear to the end of line
    line_to_print = ''
    
    if type == 'success':
        line_to_print = bcolors.OKGREEN
        
    if type == 'error':
        line_to_print = bcolors.FAIL
        
    if type == 'warning':
        line_to_print = bcolors.WARNING
        
    line_to_print += '\r' + track_number + ' - ' + song_name + '  : ' + status
    
    if type != None:
        line_to_print += bcolors.ENDC
        
    printf(line_to_print)

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
    success = False
    retry = 0
    r = None
    
    while not success and retry <5:
        payload = {'search_query': songname}
        r = requests.get('http://www.youtube.com/results', params=payload)
        
        if r.status_code == requests.codes.ok:
            success = True
            
        retry += 1
        
    if retry >= 5:
        return None
        
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
        
    result = -1
    retry = 0
    
    while result != 0 and retry < 5: 
        #result = os.system(command_line)
        youtubedl_command = Popen(command_line, stdout=PIPE, stderr=STDOUT)
        stdout, nothing = youtubedl_command.communicate()    

        with open('album-dl.log', 'w') as log:
            log.write(stdout)
        
        result = youtubedl_command.returncode
       
        retry += 1
        
        update_status(song ,track_number, 'Retrying to download', 'warning')
        
    if retry == 5:
        update_status(song ,track_number, 'FATAL ERROR : Unable to download', 'error')
        return
        
    if os.path.exists(absolute_file_path):
        os.remove(absolute_file_path)
    
    update_status(song ,track_number, 'Moving to right folder')
    os.rename("temp.m4a", absolute_file_path)
        
    update_status(song ,track_number, 'Tagging song')
    audio = MP4(absolute_file_path)
    audio['\xa9ART'] = artist #artist
    audio['\xa9alb'] = album
    audio['\xa9nam'] = song
    audio['aART'] = artist #album artist
    audio['trkn'] = [(int(track_number), nb_of_tracks)]
    audio.save()
    
    update_status(song ,track_number, 'Done !', 'success')

#to deal with xml encoded in UTF-8
reload(sys)
sys.setdefaultencoding('utf-8')

args = parse_arg()

print 'Contacting Last.fm to get album info...'
payload = {'api_key': LAST_FM_API_KEY, 'artist': args.artist, 'album': args.album}
response = requests.get('http://ws.audioscrobbler.com/2.0/?method=album.getInfo', payload)
tree = ET.ElementTree(ET.fromstring(response.text))

print 'Album information :'
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
    update_status(song, track_number , 'Getting url of song...')
    songurl = get_url_of_song(artist + ' ' + song_name)
    if songurl == None:
        update_status(song, track_number , 'Unable to fetch url of song video after multiple retries', 'error')
        break
    update_status(song, track_number , 'Downloading and converting song')
    download_video(songurl, artist, album, song_name, track_number, nb_of_tracks)
    printf('\n')
    
    
    
