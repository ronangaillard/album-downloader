# album-dl

album-dl is a small python utility that helps you download full music albums from the web easily.

### Version
0.2.1

### Usage
```sh
$ __main__.py [-h] -a ARTIST [-A ALBUM] [--version]
```
Arguments:
* -h, --help  show this help message and exit
* -a ARTIST   the artist of the album to be downloaded
* -A ALBUM    the album to be downloaded (if not filled, nothing will be downloaded but the script will show most popular albums of filled artist)
* --version   show program's version number and exit

Example :

```sh
$ album-dl -a "Daft Punk" -A "Discovery"
```

Album will be stored in your default music folder with a nice folder architecture : "~/Music/ARTIST/ALBUM" on UNIX like systems or in "C:\Users\YOUR_NAME\Music\ARTIST\ALBUM" on Windows.

Music files will be tagged with the right information (artist, album and song name), and files will be in the aac format.

You can also only precise the artist name to view its most popular albums :

```sh
$ album-dl -a "Daft Punk"
```

### Tech

album-dl uses a number of open source projects to work properly:

* [youtube-dl] - a python app to download video from YouTube
* [ffmpeg] - the well-known free media converter
* [mutagen] - a python app to tag music files
* [request] - a python library to easily make web requests
* [Last.fm API] -to retrieve album info like track list for instance

And of course album-dl itself is open source with a [public repository][https://bitbucket.org/ronangaillard/album-downloader]
 on BitBucket .

### Installation

You need python, as well as pip, and ffmpef installed of course.

#### On Linux :

```sh
$ sudo apt-get install python python-pip ffmpeg
```

You can then install album-dl using pip :
```sh
$ pip install album-dl
```

#### On Mac OS :

```sh
$ brew install python python-pip ffmpeg
```

You can then install album-dl using pip :
```sh
$ pip install album-dl
```


#### On Windows :

Install python and pip from [here][https://www.python.org/downloads/windows/] and ffmpeg from [here][https://www.ffmpeg.org/download.html]

You can then install album-dl using pip :
```sh
$ pip install album-dl
```

### Bugs

There are no known bugs, but there may be issues with the encoder selected with ffmpeg, code needs to dynamicaly choose the encoder

### History

* 0.2.1 : Fixed version number issue
* 0.2.0 : Added viewing of top albums of a choosen artist, fixed a bug that would make the script crash if album was not found on last.fm