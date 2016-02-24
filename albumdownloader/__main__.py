#!/usr/bin/python

import os
import sys
import requests
import re
import xml.etree.cElementTree as ET
from mutagen.easymp4 import EasyMP4
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TIT2
import json
import base64
import unicodedata
import string
import argparse
from subprocess import Popen, PIPE, STDOUT
from os.path import expanduser



LAST_FM_API_KEY = '739148a56b222644ce68c68e3851b55a'
temp_folder = ''
app_folder = ''

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
    
def clean_temp_folder():
    global temp_folder 

    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
        
    for the_file in os.listdir(temp_folder):
        file_path = os.path.join(temp_folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception, e:
            pass

def update_status(song_title, track_number, status, type=None):
    sys.stdout.write("\033[2K") # Clear to the end of line
    line_to_print = ''

    if type == 'success':
        line_to_print = bcolors.OKGREEN

    if type == 'error':
        line_to_print = bcolors.FAIL

    if type == 'warning':
        line_to_print = bcolors.WARNING

    line_to_print += '\r' + track_number + ' - ' + song_title + '  : ' + status

    if type != None:
        line_to_print += bcolors.ENDC

    printf(line_to_print)

def parse_arg():
    parser = argparse.ArgumentParser(description='Download full music album from the web')
    parser.add_argument('-a', dest='artist', action='store',
                    help='the artist of the album to be downloaded', required=True)
    parser.add_argument('-A', dest='album', action='store',
                    help='the album to be downloaded', default=None)
    parser.add_argument('--version', action='version', version='Album Downloader Version 0.2.1 by Ronan Gaillard')
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
        try:
            r = requests.get('http://www.youtube.com/results', params=payload)

            if r.status_code == requests.codes.ok:
                success = True
        except Exception as inst:
            update_status(song ,track_number, 'Retrying to fetch video url', 'warning')
        retry += 1

    if retry >= 5:
        return None

    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', r.text)
    return "http://www.youtube.com/watch?v=" + search_results[0]


def download_video(videourl, artist, album, song, track_number, nb_of_tracks):
    clean_temp_folder() #clean temp folder to avoid that youtube-dl thinks the video has already been downloaded
    #Adds a 0 for the 9 first songs to make a nice file name ;)
    if len(track_number) == 1:
        formatted_track_number = '0' + track_number
    else:
        formatted_track_number = track_number


    song = unicode(song)
    artist_directory = ''
    album_directory = ''
    absolute_file_path = ''
    home = expanduser("~")
    #Create directories of artist and album if not exists
    if sys.platform == 'win32':
        artist_directory = home + u'\\Music\\' + artist
        album_directory = home + u'\\Music\\' + artist + '\\' + album
        absolute_file_path = album_directory + '\\' + formatted_track_number + ' ' +  removeDisallowedFilenameChars(song) +'.m4a' #making a filesafe name
    else:
        artist_directory = home + u'/Music/' + artist
        album_directory = home + u'/Music/' + artist + '/' + album
        absolute_file_path = album_directory + '/' + formatted_track_number + ' ' +  removeDisallowedFilenameChars(song) +'.m4a' #making a filesafe name

    command_line = 'youtube-dl '
    command_line += '-o "'+temp_folder+'temp.%(ext)s" '
    command_line += '-f bestaudio '
    if sys.platform == 'win32': #needs win fix because of a bug in youtube-dl which does not put double quotes around filename on windows
        command_line += '--exec "'+ app_folder + 'win_fix.bat ffmpeg -i {} -vn -c:a libvo_aacenc -y '+temp_folder+'temp.m4a " '
    else:
        command_line += '--exec "ffmpeg -i {} -vn -c:a aac -strict -2 -y '+temp_folder+'temp.m4a " '
    command_line += videourl

    #print command_line

    if not os.path.exists(artist_directory):
        os.makedirs(artist_directory)

    if not os.path.exists(album_directory):
        os.makedirs(album_directory)

    result = -1
    retry = 0

    while result != 0 and retry < 5: 
        #result = os.system(command_line)
        youtubedl_command = Popen(command_line, stdout=PIPE, stderr=STDOUT, shell=True)
        stdout, nothing = youtubedl_command.communicate()    

        with open(temp_folder + 'album-dl.log', 'w') as log:
            log.write(stdout)

        result = youtubedl_command.returncode
        
        retry += 1
        
        update_status(song ,track_number, 'Retrying to download', 'warning')
        
    if retry == 5:
        update_status(song ,track_number, 'FATAL ERROR : Unable to download', 'error')
        return
    
    update_status(song ,track_number, 'Moving to right folder')
        
    try:
        os.remove(absolute_file_path)
    except OSError as e:
        if os.path.isfile(absolute_file_path): 
            update_status(song ,track_number, 'Unable to replace song, the file alredy exists and cannot be deleted, skipping', 'error')
            return
        
    os.rename(temp_folder+"temp.m4a", absolute_file_path)
        
    update_status(song ,track_number, 'Tagging song')
    audio = MP4(absolute_file_path)
    audio['\xa9ART'] = artist #artist
    audio['\xa9alb'] = album
    audio['\xa9nam'] = song
    audio['aART'] = artist #album artist
    audio['trkn'] = [(int(track_number), nb_of_tracks)]
    audio.save()
    
    update_status(song ,track_number, 'Done !', 'success')
    
def check_for_bat_file():
###For windows only : checks if the bat file containing the bat fix is present
###Very dirty...
    if not os.path.isfile(app_folder + 'win_fix.bat'):
        content = '@echo off\r\n'
        content += 'set str=%*\r\n'
        content += 'set str=%str:\'="%\r\n'
        content += '%str%'
        
        f = open(app_folder + 'win_fix.bat', 'w')
        f.write(content)
        f.close()

#Lists top albums of the given artist
def list_albums(artist):
    album_list = []
    payload = {'api_key': LAST_FM_API_KEY, 'artist': artist}
    response = requests.get('http://ws.audioscrobbler.com/2.0/?method=artist.getTopAlbums', payload)
    
    album_tree = ET.ElementTree(ET.fromstring(response.text))
    
    if album_tree.getroot().attrib['status'] != 'ok':
        #Then album has not been found
        error_code = int(album_tree.find('error').attrib['code'])
        printf(bcolors.FAIL + 'Error : ' + album_tree.find('error').text + bcolors.ENDC)
        exit()

    for album in album_tree.findall('topalbums/album'):
        album_list.append( album.find('name').text.encode(sys.stdout.encoding, errors='replace'))
        #album_list.append('hello')
    
    return [album_tree.find('topalbums').attrib['artist'], album_list]          


def main(args=None):
    home = expanduser("~")
    global temp_folder 
    global app_folder
    
    if sys.platform == 'win32':
        app_folder = home + '\\albumdownloader\\'
        temp_folder = app_folder + 'temp\\'  
 
    else:
        app_folder = home + '/.albumdownloader/'
        temp_folder = app_folder + 'temp/'
        

    if not os.path.exists(app_folder):
        os.makedirs(app_folder)

    if sys.platform == 'win32':
        check_for_bat_file()
        
    #to deal with xml encoded in UTF-8
    reload(sys)
    sys.setdefaultencoding('utf-8')

    args = parse_arg()
    
    if args.album == None:
        [corrected_artist, album_list] = list_albums(args.artist)
        print 'Here are the top albums for', corrected_artist
        
        for i in range(0,9):
            print album_list[i]
        
        print'\nYou can download them using the -A option'
        
        return

    print 'Contacting Last.fm to get album info...'
    payload = {'api_key': LAST_FM_API_KEY, 'artist': args.artist, 'album': args.album}
    response = requests.get('http://ws.audioscrobbler.com/2.0/?method=album.getInfo', payload)
    tree = ET.ElementTree(ET.fromstring(response.text))
    
    if tree.getroot().attrib['status'] != 'ok':
        #Then album has not been found
        error_code = int(tree.find('error').attrib['code'])
        printf(bcolors.FAIL + 'Error : ' + tree.find('error').text + bcolors.ENDC)
        exit()

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
        update_status(song_name , track_number , 'Getting url of song...')
        songurl = get_url_of_song(artist + ' ' + song_name)
        if songurl == None:
            update_status(song, track_number , 'Unable to fetch url of song video after multiple retries', 'error')
            break
        update_status(song_name, track_number , 'Downloading and converting song')
        download_video(songurl, artist, album, song_name, track_number, nb_of_tracks)
        printf('\n')
        


if __name__ == "__main__":
    main()
    
