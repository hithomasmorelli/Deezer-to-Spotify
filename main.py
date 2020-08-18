#!/usr/bin/env python3
from spotipy import Spotify, SpotifyOAuth, client
from _deezer_auth_code import authorize as deezer_authorize
from deezer import Client as Deezer
from dotenv import load_dotenv
from os import getenv
import logging
import json
from sys import exit
from time import sleep


# env
def load_env():
    load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(lineno)d -- %(message)s")


# helper function for playlist import y/n choice
def chooseYesNo(statement):
    choice = None
    statement = "> " + statement + "?"
    statement = statement.replace("\n", "\n> ")
    while choice == None:
        answer = input(statement + " [y/n]: ")
        if answer == "y":
            choice = True
        elif answer == "n":
            choice = False
        else:
            print("> Please provide a valid response.")
    
    return choice


# function for sorting playlist tracks
def getTimeAdd(track):
    return track["time_add"]

#################
# spotify
#################
class Spotify_client:
    def __init__(self, *args, **kwargs):
        client_id = getenv('SPOTIFY_client_id')
        client_secret = getenv('SPOTIFY_client_secret')
        self.username = getenv('SPOTIFY_username')
        redirect_uri = getenv('SPOTIFY_redirect_uri')
        scope = 'playlist-modify-private user-library-modify'

        # login
        logging.info("Starting Spotify client")
        auth_manager = SpotifyOAuth(client_id=client_id, client_secret=client_secret, scope=scope, redirect_uri=redirect_uri, username=self.username)
        self.sp_client = Spotify(auth_manager=auth_manager)

    def create_playlist(self, playlist_name):
        logging.debug(f'playlist_name: {playlist_name}')
        return self.sp_client.user_playlist_create(user=self.username, name=playlist_name, public=False)

    def search_track(self, search_string):
        logging.debug(f'search_string: {search_string}')
        return self.sp_client.search(search_string, limit=1)

    def add_to_playlist(self, playlist_id, track_ids):
        logging.debug(f'playlist_id: {playlist_id}, track_ids: {track_ids}')
        return self.sp_client.user_playlist_add_tracks(self.username, playlist_id, track_ids)
    
    def add_to_saved_tracks(self, track_ids):
        logging.debug(f'track_ids: {track_ids}')
        return self.sp_client.current_user_saved_tracks_add(track_ids)
  

#################
# Deezer
#################
class Deezer_client:
    def __init__(self):
        deezer_app_id = getenv("DEEZER_application_id")
        deezer_secret_key = getenv("DEEZER_secret_key")
        scope = "basic_access,manage_library"

        # login
        logging.info("Starting Deezer client")
        self.deezer_client = Deezer(access_token=deezer_authorize(deezer_app_id, deezer_secret_key, scope))
    
    def get_playlists(self):
        # get a list of the user's playlists
        playlists = self.deezer_client.get_user("me").get_playlists()

        return playlists


#################
# Common
#################
def main():
    
    '''
    Playlists data structure is a list of dicts - each playlist, "name" field for playlist name and "tracks" list for all tracks
    Tracks is a list, each with a track ID
    We can grab the name field to know what playlists to create and the track ID to convert/search
    '''

     # load env
    logging.debug('Loading env')
    load_env()

    # initialize Deezer
    logging.debug('Loading Deezer')
    deezer = Deezer_client()

    # initialize spotify
    logging.debug('Loading Spotify')
    spot = Spotify_client()

    # when a track fails, should we pause until it's added (in order to preserve "order of addition"),
    # or should we just write it to `errored-tracks.log`?
    waitAfterFailed = chooseYesNo("When the program experiences a failed track, should it pause at\n"
                                + "that point in the addition process, to allow the song to be manually added")

    # Get a full dump of all Deezer playlists
    logging.info('Getting details of Deezer playlists')
    playlists = deezer.get_playlists()

    # we're going to build a 2d array of playlists, and a seperate array for favourite tracks
    playlists_tracks = {}
    favourite_tracks = []

    # loop over the playlists
    for playlist in playlists:
        if (
            (playlist.is_loved_track and chooseYesNo("Import Favourite Tracks"))
            or (not playlist.is_loved_track and chooseYesNo(f'Import playlist "{playlist.title}"'))
        ):
            # only get here if the user wants us to import the playlist
            name = playlist.title

            if not playlist.is_loved_track:
                playlists_tracks[name] = []

            # search tracks, add them to the array
            for track in playlist.get_tracks():
                try:
                    artist = track.get_artist().name
                    title = track.title
                    time_add = track.time_add

                    # search by artist and title
                    logging.info(f'Searching "{artist} {title}"')
                    search_result = spot.search_track(f'{artist} {title}')
                    logging.debug(search_result)
                    #todo: This search relies on the naming structure being similar. Can be improved with regex
                    track_uri = search_result.get('tracks').get('items')[0].get('uri')
                    logging.debug(track_uri)

                    # add track to the array
                    if playlist.is_loved_track:
                        logging.info(f'Adding {track_uri} to favourite tracks array')
                        favourite_tracks.append({
                            "title": title,
                            "artist": artist,
                            "track_uri": track_uri,
                            "time_add": time_add
                        })
                    else:
                        logging.info(f'Adding {track_uri} to playlist array')
                        playlists_tracks[name].append({
                            "title": title,
                            "artist": artist,
                            "track_uri": track_uri,
                            "time_add": time_add
                        })

                # cheap way to fix this, almost certainly means the track doesn't exist on spotify
                except IndexError:
                    if waitAfterFailed:
                        logging.info("Index out of range: This track may not exist or was not found. Adding to array with track_uri:None")
                        if not playlist.is_loved_track:
                            playlists_tracks[name].append({
                                "title": title,
                                "artist": artist,
                                "track_uri": None,
                                "time_add": time_add
                            })
                        else:
                            favourite_tracks.append({
                                "title": title,
                                "artist": artist,
                                "track_uri": None,
                                "time_add": time_add
                            })
                    else:
                        logging.info("Index out of range: This track may not exist or was not found. Adding to log")
                        with open('./errored-tracks.log', 'a') as file:
                            file.writelines(f'playist: {name} -- {artist} - {title}\n')
                # cheap fix for random 500 errors
                except client.SpotifyException:
                    if waitAfterFailed:
                        logging.info("500 error during search, adding to array with track_uri:None")
                        if not playlist.is_loved_track:
                            playlists_tracks[name].append({
                                "title": title,
                                "artist": artist,
                                "track_uri": None,
                                "time_add": time_add
                            })
                        else:
                            favourite_tracks.append({
                                "title": title,
                                "artist": artist,
                                "track_uri": None,
                                "time_add": time_add
                            })
                    else:
                        logging.info("500 error during search - track added to log")
                        with open('./errored-tracks.log', 'a') as file:
                            file.writelines(f'playist: {name} -- {artist} - {title}\n')
                except Exception:
                    # there was some other error, but we gotta carry on
                    if waitAfterFailed:
                        logging.info("An unknown error occured, adding to array with track_uid:None")
                        if not playlist.is_loved_track:
                            playlists_tracks[name].append({
                                "title": title,
                                "artist": artist,
                                "track_uri": None,
                                "time_add": time_add
                            })
                        else:
                            favourite_tracks.append({
                                "title": title,
                                "artist": artist,
                                "track_uri": None,
                                "time_add": time_add
                            })
                    else:
                        logging.info("An unknown error occured - track added to log")
                        with open('./errored-tracks.log', 'a') as file:
                            file.writelines(f'playist: {name} -- {artist} - {title}\n')


    # should we sleep after each song addition to spotify?
    # useful if wanting to preserve "order of addition" - if songs
    # are added too quickly, spotify muddles up the order
    sleeping = chooseYesNo("Should the program pause after each song addition")
    SLEEP_AMOUNT = 0.95

    # do we have any (non-favourite-tracks) playlists to add?
    if len(playlists_tracks) != 0:
        # add tracks to playlists
        for name, tracks in playlists_tracks.items():
            logging.info(f'Making new playlist "{name}"...')
            new_playlist_id = spot.create_playlist(name).get('id')
            logging.info(f'Playlist created: {name} -- ID: {new_playlist_id}')

            # sort track array in order of time added
            logging.info('Sorting playlist tracks by time added')
            tracks.sort(key=getTimeAdd)

            # loop tracks, add them to the new playlist
            for track in tracks:
                try:
                    title = track["title"]
                    artist = track["artist"]
                    track_uri = track["track_uri"]

                    if track_uri is not None:
                        # add track to the new playlist
                        logging.info(f'Adding "{title}" ({artist}) [{track_uri}] to {name}')
                        #todo: speed could be improved with async
                        playlist_add = spot.add_to_playlist(new_playlist_id, [track_uri])
                        logging.info('Song added')
                        logging.debug(playlist_add)

                        # sleep after each song to allow spotify to properly sort them by time added
                        if sleeping:
                            sleep(SLEEP_AMOUNT)
                    else:
                        # track failed search, give a chance to add now
                        input(f'> Please add "{title}" ({artist}) to {name} manually, then press Enter to continue...')

                # cheap fix for random 500 errors
                except client.SpotifyException:
                    if waitAfterFailed:
                        logging.info("500 error - track may have been added anyway")
                        input(f'> Please add "{title}" ({artist}) to {name} manually (if it is not already added), then press Enter to continue...')
                    else:
                        logging.info("500 error - failed track written to log. It might have been added anyway, check later")
                        with open('./errored-tracks.log', 'a') as file:
                            file.writelines(f'playist: {name} -- {artist} - {title}\n')
                except Exception:
                    # any other weird exception
                    if waitAfterFailed:
                        logging.info("An unknown error occured")
                        input(f'> Please add "{title}" ({artist}) to {name} manually (if it is not already added), then press Enter to continue...')
                    else:
                        logging.info("An unknown error occured - track added to log")
                        with open('./errored-tracks.log', 'a') as file:
                            file.writelines(f'playist: {name} -- {artist} - {title}\n')

    # do we have any favourite tracks to add?
    if len(favourite_tracks) != 0:
        logging.info("Sorting favourite tracks by time added")
        favourite_tracks.sort(key=getTimeAdd)

        # loop tracks, add to "liked songs"
        for track in favourite_tracks:
            try:
                title = track["title"]
                artist = track["artist"]
                track_uri = track["track_uri"]

                if track_uri is not None:
                    # add track to "liked songs"
                    logging.info(f'Adding "{title}" ({artist}) [{track_uri}] to Liked Songs')
                    liked_songs_add = spot.add_to_saved_tracks([track_uri])
                    logging.info('Song added')
                    logging.debug(liked_songs_add)

                    # sleep after each song to allow spotify to properly sort them by time added
                    if sleeping:
                        sleep(SLEEP_AMOUNT)
                else:
                    # track failed search, give a chance to add now
                    input(f'> Please add "{title}" ({artist}) to Liked Songs manually, then press Enter to continue...')
            
            # cheap fix for random 500 errors
            except client.SpotifyException:
                if waitAfterFailed:
                    logging.info("500 error - track may have been added anyway")
                    input(f'> Please add "{title}" ({artist}) to Liked Songs manually (if it is not already added), then press Enter to continue...')
                else:
                    logging.info("500 error - failed track written to log. It might have been added anyway, check later")
                    with open('./errored-tracks.log', 'a') as file:
                        file.writelines(f'playist: Liked Songs -- {artist} - {title}\n')
            except Exception:
                # any other weird exception
                if waitAfterFailed:
                    logging.info("An unknown error occured")
                    input(f'> Please add "{title}" ({artist}) to {name} manually (if it is not already added), then press Enter to continue...')
                else:
                    logging.info("An unknown error occured - track added to log")
                    with open('./errored-tracks.log', 'a') as file:
                        file.writelines(f'playist: {name} -- {artist} - {title}\n')


if __name__ == "__main__":
   main()
   print("Finished\nPlease check errored-tracks.log for missing tracks")