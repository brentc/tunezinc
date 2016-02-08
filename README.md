# TuneZinc

Synchronize your Google Music Playlists with Spotify

## Installation

1. git clone git@github.com:brentc/tunezinc.git
1. mkvirtualenv TuneZinc
1. pip install requirements.txt

## Configuration 

Set the following environment variables:

* `GMUSIC_USERNAME` Your google username
* `GMUSIC_PASSWORD` Your google password
* `GMUSIC_PLAYLISTS` a '`;`' separated list of playlist names you want to sync

You will need to register a Spotify application to authenticate with spotify. Go to 
[My Applications](https://developer.spotify.com/my-applications/#!/applications) and "Create An 
App":
    
* Application Name: TuneZinc
* Description: _Some Description_
* Redirect URIs: `http://example.com/tunezinc/`

Save the app and configure the following environment variables:
    
* `SPOTIFY_USERNAME` Your spotify username
* `SPOTIFY_CLIENT_ID` Your new app's Client ID
* `SPOTIFY_CLIENT_SECRET` Your new app's Client Secret

## Usage

```bash
python tunezinc.py
```

The first time you run it, it will prompt you to oAuth authenticate with Spotify by open a browser,
granting access and pasting the redirected URL back to the console.

You may also need to do a similar process with Google Music if it needs to get details from any 
tracks you uploaded via All Access (even though you must still provide your username and password as
an environment variable)

## TODO

See [docs/TODO](docs/TODO.md) for thoughts on what's missing/needed. 

## Contributing

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

## History

* Feb 7, 2016 - First working version

## Credits

Brent Charbonneau

## License

The MIT License (MIT)

Copyright (c) 2016 Brent Charbonneau

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
