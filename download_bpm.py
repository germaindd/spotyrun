import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import sys
import subprocess
import re

credentials = SpotifyClientCredentials("70aca742c29e4bf0b10705f38d99faa3", "2a73c2a476044f7b82f6771b1ed31c63")
sp = spotipy.Spotify(client_credentials_manager=credentials)


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
    subprocess.run(['rm', '{}/*.wav'.format(path)], shell=True)


def convert_bpm(tracks: list, target_bpm):
    """convert the bpm of given tracks"""
    subprocess.run(['mkdir', 'converted'])
    for track in tracks:
        filename = "{}.wav".format(track.track_name.replace(',', ''))

        if track.bpm < 100:
            track.bpm *= 2

        print("adjusting bpm {} to bpm {}\n".format(track, target_bpm))
        subprocess.run(['rubberband', '--quiet', '--tempo', '{}:{}'.format(track.bpm, target_bpm),
                        filename, 'converted/{}'.format(filename)])
        subprocess.run(['ffmpeg', '-loglevel', 'level+error', '-i', 'converted/{}'.format(filename), 'converted/{}.mp3'.format(track.track_name)])
        print('\n')


def download_playlist(playlist_id, playlist_name: str):
    subprocess.run(['spotdl', '--playlist', playlist_id], stdout=subprocess.PIPE)
    subprocess.run(['spotdl', '--list', '{}.txt'.format(playlist_name.replace(' ', '-')), '--overwrite', 'force',
                    '--file-format', '{track_name}', '--trim-silence', '--folder', '.', '--output-ext', '.wav'],
                   stdout=subprocess.PIPE)


def add_song_bpm(sp: spotipy.Spotify, tracks: list):
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

        if playlist_tracks['next'] is not None:
            playlist_tracks = sp.get_playlist_tracks(playlist_id, offset=offset)
            print(playlist_tracks)
    return tracks


def main():
    playlist_id = sys.argv[1].split(':')[-1]
    target_bpm = sys.argv[2]

    playlist_dict = sp.get_playlist(playlist_id)
    playlist_name = playlist_dict['name']

    tracks = get_playlist_tracks(playlist_id)

    # add_song_bpm(sp, tracks)
    #
    # download_playlist(playlist_id, playlist_name)
    #
    # convert_bpm(tracks, target_bpm)



if __name__ == "__main__":
    main()
