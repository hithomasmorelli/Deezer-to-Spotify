# Deezer to Spotify Playlist Transfer Tool

This Python script will (soon) transfer your Deezer playlists to Spotify. It is heavily based on [@iloveicedgreentea's repo](https://github.com/iloveicedgreentea/GPM-to-Spotify) for doing the same thing with Google Play Music.

My reasons for coding this are basically the same as the motives behind the original repo:

1) I was moving to Spotify and there was no way I would transfer loads of songs by hand
2) Couldn't find much in the way of open source that actually did this
3) Anything that claimed to do this either cost money, was not trustworthy, or both

This runs locally and absolutely zero information is sent to me or anyone else. Hopefully this saves someone time and money.

## Requirements

* Python 3.7
* Pipenv
* Deezer and Spotify accounts

## Setup
1) Go to the [developer page](https://developer.spotify.com/dashboard/), make an app/client_id. Add your redirect URL as `http://localhost/`
2) `mv .env.example .env`
3) Populate .env with client_id, secret, redirect url, and username (found when you login online)


## Usage
```bash
pipenv install
pipenv run python3 main.py
```

You may want to redirect output to a file. This spits out a ton of logs to stdout. Up to you.
```bash
pipenv run python3 main.py >main.log
```

### Transferring thumbs up to library
GPM and Spotify have a similar way of storing "liked" music but it requires a different way to process it.

Heres a quick way to transfer it:

1) Play your thumbs up playlist
2) Open the queue, save queue to a playlist
3) Note the name you gave it, enter it below

```bash
pipenv run python3 thumbs_up.py [name of thumbs up playlist]
```

## Known Issues
Spotify doesn't care about unique playlist names. You can have duplicates so be aware if you run this multiple times.

This will not transfer songs that were uploaded. Spotify does not offer cloud storage. Uploaded songs will be a line item in `errored-tracks.log` as the playlist name (since there is no song name to get)

If songs are missing, it's likely they don't exist on Spotify. Its also possible it was not found by search because it relies on the songs having the same name structure. Check `errored-tracks.log` and search them manually.

Spotify seems to give random 500s, can't do much about it. Seems to be rare. The script will write the failed tracks to `errored-tracks.log`

You might hit a rate limit. I tried on a premium account with thousands of songs and was okay.

There might be issues with GPM and playlists with over 1k songs. This has not been tested

Some improvements could be made such as combining the two main python files, adding flags, etc but this would take more time than it is worth considering I needed to transfer some songs once.


Feel free to fork and/or open a GH issue

## Credits
[gmusicapi](https://github.com/simon-weber/gmusicapi)

[spotipy](https://github.com/plamere/spotipy)

python-dotenv
