# Deezer to Spotify Playlist Transfer Tool

This Python script will transfer your Deezer playlists to Spotify. It is heavily based on (and was originally a fork of) [@iloveicedgreentea's repo](https://github.com/iloveicedgreentea/GPM-to-Spotify) for doing the same thing with Google Play Music.

**_This script is very clanky, so beware & treat it with care._**

My reasons for coding this are basically the same as the motives behind the original repo:

1. I was moving to Spotify and there was no way I would transfer loads of songs by hand
2. Couldn't find much in the way of open source that actually did this
3. Anything that claimed to do this either cost money, was not trustworthy, or both

This runs locally and absolutely zero information is sent to me or anyone else. Hopefully this saves someone time and money.

**NOTE**: _Unlike the base repository_, the code to transfer the "Favourite Tracks" library is contained within `main.py`, instead of a seperate file.

This script adds the songs to Spotify playlists in the order they were added to the Deezer playlists. However, adding songs one-after-another without a pause leads to Spotify getting confused as to the order a group of songs were added in. For this reason, the program asks whether or not it should pause for a set amount of time (currently 0.95 seconds) to better ensure the integrity of "sort by addition".

The script will ask if, when it encounters a failed track, it should pause at that point in the song addition process. This is to allow for all tracks - including ones that have to be added manually - to be added in their original order.

## Requirements

- Python 3.7
- Pipenv
- Deezer and Spotify accounts

## Setup

1. Go to the [Spotify developer page](https://developer.spotify.com/dashboard/) and make a new app. Add your redirect URL as `http://localhost:8080/`
2. Go to the [Deezer developer page](https://developers.deezer.com/myapps) and make a new app. Add the domain as `localhost` and the redirect URL as `http://localhost:8080/authfinish`
3. `cp .env.example .env`
4. Populate .env with Spotify client ID, secret, redirect url, and username (found when you login online)
5. Populate .env with Deezer app ID and secret key

## Usage

```bash
pipenv install
pipenv run python3 main.py
```

You may want to redirect output to a file. This spits out a ton of logs to stdout. Up to you.

```bash
pipenv run python3 main.py > main.log
```

## Docker usage

### build

```bash
docker build . -t dts
```

### usage

normal usage :

```bash
docker run -it --name dts --network host \
 -e SPOTIFY_client_id='0000000'\
 -e SPOTIFY_client_secret='0000000'\
 -e SPOTIFY_redirect_uri='http://localhost:8080/'\
 -e SPOTIFY_username='default'\
 -e DEEZER_application_id='default'\
 -e DEEZER_secret_key='default' \
 dts
```

please change environnement variable or rebuild with an good .env file (or use the development version)

developement :

```bash
docker run -it --name dts --network host \
 -v "$PWD":/usr/src/myapp \
 -w /usr/src/myapp \
 dts
```

(have the good .env in the workspace)

## Known Issues

Spotify requests sometimes time out.
Spotify doesn't care about unique playlist names. You can have duplicates so be aware if you run this multiple times.

This will not transfer songs that were uploaded. Spotify does not offer cloud storage. Uploaded songs will error.

If songs are missing, it's likely they don't exist on Spotify. Its also possible it was not found by search because it relies on the songs having the same name structure.

Spotify seems to give random 500s, can't do much about it. Seems to be rare. The script will error the failed tracks.

You might hit a rate limit. I tried on a premium account with thousands of songs and was okay.

Some improvements could be made but this would take more time than it is worth considering I needed to transfer some songs once. Feel free to open a PR with code improvements!

Feel free to fork and/or open a GH issue

## Credits

### Original Repository

This repository is based on [iloveicedgreentea/GPM-to-Spotify](https://github.com/iloveicedgreentea/GPM-to-Spotify), without which I would have never got around to doing this.

### Other Credits

Thanks to [@helpsterTee](https://github.com/helpsterTee), whose [code](https://github.com/helpsterTee/spotify-playlists-2-deezer/blob/b6e3621b4b778ab11a8ce59d0973c603fda99e2d/spotify-restore.py#L143-L200) I modified for Deezer authentication. That code is in the file [`_deezer_auth_code.py`](/_deezer_auth_code.py), and has a different license (specified within the file) to the rest of the repository.

### Libraries

- [deezer-python](https://github.com/browniebroke/deezer-python)
- [spotipy](https://github.com/plamere/spotipy)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
