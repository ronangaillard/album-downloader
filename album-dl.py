#!/usr/bin/python

#Application name	GetAlbumInf
#API key	739148a56b222644ce68c68e3851b55a
#Shared secret	6359190e1015fea04aa8ea1ae75f93a3
#Registered to	CelteekFm

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


def get_url_of_song(songname):
    payload = {'search_query': songname}
    r = requests.get('http://www.youtube.com/results', params=payload)
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', r.text)
    return "http://www.youtube.com/watch?v=" + search_results[0]
    
def my_hook(d):
    if d['status'] == 'finished':
        print('\t\tDone downloading, now converting ...')
#A list of functions that get called on download
#                       progress, with a dictionary with the entries
#                       * status: One of "downloading", "error", or "finished".
#                                 Check this first and ignore unknown values.
#                       If status is one of "downloading", or "finished", the
#                       following properties may also be present:
#                       * filename: The final filename (always present)
#                       * tmpfilename: The filename we're currently writing to
#                       * downloaded_bytes: Bytes on disk
#                       * total_bytes: Size of the whole file, None if unknown
#                       * total_bytes_estimate: Guess of the eventual file size,
#                                               None if unavailable.
#                       * elapsed: The number of seconds since download started.
#                       * eta: The estimated time in seconds, None if unknown
#                       * speed: The download speed in bytes/second, None if
#                                unknown
#                       * fragment_index: The counter of the currently
#                                         downloaded video fragment.
#                       * fragment_count: The number of fragments (= individual
#                                         files that will be merged)
        
class MyLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)
        
def download_file(url, filename):
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r: 
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
 
def download_video(videourl, artist, album, song, track_number, nb_of_tracks):
    #Adds a 0 for the 9 first songs to make a nice file name ;)        
    if len(track_number) == 1:
        formatted_track_number = '0' + track_number
    else:
        formatted_track_number = track_number
        
    #Create directories of artis and album if not exists
    artist_directory = u'C:\\Users\\Ronan\\Music\\' + artist
    album_directory = u'C:\\Users\\Ronan\\Music\\' + artist + '\\' + album
    absolute_file_path = album_directory + '\\' + formatted_track_number + ' ' + song +'.m4a'
    
    command_line = 'youtube-dl '
    #command_line += '-x ' #extract audio
    #command_line += '--audio-format aac ' #format is mp3
    #command_line += '-o "' + absolute_file_path +'" ' #file output
    #command_line += '--audio-quality 0 ' #best audio quality
    command_line += '-o temp.%(ext)s '
    command_line += '--exec "ffmpeg -i {} -vn -c:a libvo_aacenc -y temp.m4a " '
    command_line += videourl
    

    
    if not os.path.exists(artist_directory):
        os.makedirs(artist_directory)
        
    if not os.path.exists(album_directory):
        os.makedirs(album_directory)
        
    
        
    print command_line
    os.system(command_line)
    
    os.rename("temp.m4a", absolute_file_path)
    #print '\t\tGetting url of mp3...'
    #response = requests.get('http://www.youtubeinmp3.com/fetch/?format=text&video=http://www.youtube.com/watch?v=i62Zjga8JOM')
    #url = response.text[response.text.index('Link:')::]
    #url = url[6::]
    #print url
    
    #print '\t\tDownloading mp3...'
    #download_file(videourl, absolute_file_path)
    #ydl_opts = {
    #    'format': 'bestaudio/best',
    #    'outtmpl': absolute_file_path,
    #    'postprocessors': [{
    #        'key': 'FFmpegExtractAudio',
    #        'preferredcodec': 'mp3',
    #        'preferredquality': '320',
    #    }],
    #    'logger': MyLogger(),
    #    'progress_hooks': [my_hook],
    #}
    #with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #    ydl.download([videourl])
        
    print '\t\tTagging : ' + absolute_file_path
    audio = MP4(absolute_file_path)
    audio['\xa9ART'] = artist #artist
    audio['\xa9alb'] = album
    audio['\xa9nam'] = song
    audio['aART'] = artist #album artist
    audio['trkn'] = [(int(track_number), nb_of_tracks)]
    audio.save()
    

        
    #print 'id31 -v -a "' + artist + '" -t "' + song + '" -l "'+ album + '" -n ' + track_number + ' "' + absolute_file_path + '"'
    
    #os.system('id31 -v -a "' + artist + '" -t "' + song + '" -l "'+ album + '" -n ' + track_number + ' "' + absolute_file_path + '"')
#to deal with xml encoded in UTF-8
reload(sys)
sys.setdefaultencoding('utf-8')

print 'Contacting Last.fm to get album info...'
response = requests.get('http://ws.audioscrobbler.com/2.0/?method=album.getInfo&api_key=739148a56b222644ce68c68e3851b55a&artist=daft%20punk&album=discovery')
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
    
    
    
