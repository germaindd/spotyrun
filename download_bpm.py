import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import subprocess
import re
import os
import sys

credentials = SpotifyClientCredentials("70aca742c29e4bf0b10705f38d99faa3", "2a73c2a476044f7b82f6771b1ed31c63")
sp = spotipy.Spotify(client_credentials_manager=credentials)
OUTPUT_PATH = ''
subprocess.run(['chmod', 'u+x', 'rubberband'])


class Track:
    def __init__(self, track_name, id, bpm=None):
        self.track_name = track_name
        self.id = id
        self.bpm = bpm

    def set_bpm(self, tempo: int):
        self.bpm = tempo

    def __str__(self):
        return "Track: {}, {} bpm".format(self.track_name, self.bpm)


def delete_originals(path: str):
    """remove .wav files to keep only mp3s"""
    subprocess.run('rm {}/*.wav'.format(path), shell=True)


def convert_bpm(tracks: list, target_bpm):
    """convert the bpm of given tracks"""
    subprocess.run(['mkdir', '{}/bpm_converted'.format(OUTPUT_PATH)])
    for track in tracks:
        # remove '.' in track name (spotdl does this so the os knows where the file extension is)
        filename = "{}.wav".format(track.track_name.replace('.', '').replace('"', ''))

        # when i convert my running playlist I have bpm's around 80-90 and 160-180. I want both of these categories to
        # be adjusted at the same factor otherwise the songs with bpm 80-90 are gonna end up going REALLY fast
        base_bpm = track.bpm
        if base_bpm < 100:
            base_bpm *= 2

        print("adjusting bpm {} to bpm {} using rubberband".format(track, target_bpm))

        path_to_executable = os.path.abspath(os.path.dirname(sys.argv[0]))
        subprocess.run(['{}/rubberband'.format(path_to_executable), '--quiet', '--tempo', '{}:{}'.format(base_bpm, target_bpm),
                        "{}/{}".format(OUTPUT_PATH, filename), '{}/bpm_converted/{}'.format(OUTPUT_PATH, filename)])

        print("converting to mp3")
        subprocess.run(['ffmpeg', '-y', '-loglevel', 'level+error', '-i', '{}/bpm_converted/{}'.format(OUTPUT_PATH, filename),
                        '{}/bpm_converted/{}.mp3'.format(OUTPUT_PATH, track.track_name)])
        print("\n")


def download_playlist(playlist_id, playlist_name: str):
    """downloads the entire playlist in .wav format with spotdl (and options)"""
    subprocess.run(['spotdl', '--playlist', playlist_id], stdout=subprocess.PIPE)
    subprocess.run(['spotdl', '--list', '{}.txt'.format(playlist_name.replace(' ', '-')), '--overwrite', 'force',
                    '--file-format', '{track_name}', '--trim-silence', '--folder', OUTPUT_PATH, '--output-ext', '.wav'],
                   stdout=subprocess.PIPE)

    print("\n------------------\nDownload finished\n------------------\n\n")


def add_song_bpm_to_tracks(tracks: list):
    """adds song bpm to list of tracks"""
    ids = list(map(lambda track: track.id, tracks))
    features_list = sp.audio_features(ids)
    for track, features in zip(tracks, features_list):
        track.set_bpm(features['tempo'])


def get_playlist_tracks(playlist_id):
    """songname, id"""
    playlist_tracks = sp.get_playlist_tracks(playlist_id)

    tracks = []
    offset = 0
    for item in playlist_tracks['items']:
        id = item['track']['id']
        name = item['track']['name']

        tracks.append(Track(name, id))

        # if there are multiple pages
        if playlist_tracks['next'] is not None:
            playlist_tracks = sp.get_playlist_tracks(playlist_id, offset=offset)
    return tracks


def get_playlist_id():
    # get id from URI
    playlist_input = input('enter playlist link: ')
    if 'spotify:playlist' in playlist_input:
        playlist_id = playlist_input.split(':')[-1]
    elif 'spotify.com/playlist' in playlist_input:
        query = re.search("/playlist/(.+)$", playlist_input)
        group1 = query.group(1)
        playlist_id = group1.split('?')[0]
    else:
        playlist_id = playlist_input
    return playlist_id


def main():
    global OUTPUT_PATH

    playlist_id = get_playlist_id()

    target_bpm = input('enter target bpm: ')
    OUTPUT_PATH = input('enter path of folder to output to (or press enter for current directory): ')

    if OUTPUT_PATH == '':
        OUTPUT_PATH = '.'
    elif OUTPUT_PATH[-1] == '/':
        OUTPUT_PATH = OUTPUT_PATH[:-1]

    subprocess.run(['mkdir', OUTPUT_PATH])

    playlist_api_response = sp.get_playlist(playlist_id)
    playlist_name = playlist_api_response['name']

    tracks = get_playlist_tracks(playlist_id)

    add_song_bpm_to_tracks(tracks)

    download_playlist(playlist_id, playlist_name)

    convert_bpm(tracks, target_bpm)

    delete_originals("{}/bpm_converted".format(OUTPUT_PATH))


if __name__ == "__main__":
    main()
