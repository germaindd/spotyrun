Disclaimer: this is not a fully functional program. It is something i wrote in an afternoon. It has
many flaws.

### About this program

Essentially a little python script that you give three things: a spotify playlist, a target bpm (beats
per minute), and an output folder to write to. It'll download the spotify songs for you and speed them
up or slow them down so that they match the bpm you provided. This could be useful in conjunction with
http://sortyourmusic.playlistmachinery.com/ to make running playlists. Make a playlist in the 160-180
bpm range and then use this program to get a nice smooooth bpm all along your run and not stuff up your
rhythm every time the tempo changes.

#### Installation

This program has a couple dependencies that you'll have to install manually to get the program to work.

Here's a step by step:

1. Clone the repository

2. Go into the repository directory and run `pip install -r requirements.txt`

    I recommend using a virtual environment to install the dependencies and run the program (I've had some problems with it before)

3. install ffmpeg, if you have homebrew, just `brew install ffmpeg` otherwise you can download it [here](https://ffmpeg.org/download.html)

And you should be done.

#### Little bit more about this program

The program essentially just uses a bunch of third party python libraries to automate the process of 
downloading and conversion. It uses [spotdl](https://github.com/ritiek/spotify-downloader) to download the 
playlist you provide and then calls the spotify API to find out the bpm of each song (it uses spotipy
to do this, however i had to modify it as it hasn't been maintained for a while and there are some
missing endpoints - which is why there's a copy of the source in this repo. The repository can be found [here](https://github.com/plamere/spotipy)). Once the songs
are downloaded, it uses [rubberband](https://breakfastquay.com/rubberband/) (that executable you see in
the root folder that I've added for convenience) to do the time-stretching and pitch-changing of the 
audio files. Finally, it uses [ffmpeg](https://ffmpeg.org/) to convert everything back to .mp3 format
and bob's your uncle.

#### Contributing

Feel free to copy this code, modify it, or contribute to your hearts desire. Like I've said, it's a little
rough around the edges so it could use some polishing.

#### Another Disclaimer
Downloading copyright songs is illegal. This tool is for educational purposes only.
