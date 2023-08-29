# Description
__Ytldl2__ is a script, which helps to download and keep updated your offline copy of YouTube Music.

## Example output:
```ps
C:\Users\user\Desktop>ytldl2 --debug lib -d "d:\!YT2" -p my_password update
Library update started...

Got following home items:
Videos: 26 items.
Channels: ['Supercell', 'YOASOBI', 'ReoNa', 'Aimer', 'Epica', 'LiSA', 'Kanako Ito']
Playlists: ['Your Likes', 'My Supermix', 'My Mix 1', 'My Mix 2', 'My Mix 3', 'My Mix 4', 'My Mix 5', 'My Mix 6', 'My Mix 7', 'Archive Mix', 'Replay Mix']

They will be filtered with following filters:
Videos: []
Channels: ['YOASOBI']
Playlists: ['My Supermix', 'My Mix 1', 'My Mix 2', 'My Mix 3', 'My Mix 4', 'My Mix 5', 'My Mix 6', 'Your Likes', 'Archive Mix', 'Replay Mix']

Starting to download batch of 45 songs, limit=None:
Filtered: [SX_ViT4Ra7k] (米津玄師  - Lemon  Kenshi Yonezu), reason: it is video, not a song
Downloaded: [l-rQzfIRxO0] (MYTH & ROID - Cracked Black).


             ╷
  Result     │ Count
╶────────────┼───────╴
  Downloaded │  20
  Filtered   │  25
  Errors     │   0
╶────────────┼───────╴
  Total      │  45
```

### __Songs__ and __videos__
YouTube has two types of music: actual _songs_ and _videos_. _Song_ is a real song, with all appropriate tags. On the other side, video_ is just a video, which can possibly contain valid song, but doesn't contain _Artist_ and _Lyrics_ tags. You don't want to have such _video_ in your library, because it can contain any unwanted pieces, such as noise or silence.

Script will skip all _videos_, downloading only _songs_. Songs are being downloaded as _m4a_ files with filled tags: _Title_, _Artist_, _URL_. Also, _Lyrics_ tag is included, if YouTube has it available.

### Data directory
Scipt using `your_library/.ytldl2` directory for storing persistent data. Generally, you don't want to change it contents. It contains following items:

- Cache.

    Every processed video will be put into persistent cache. Previously downloaded songs won't download again. You can manually remove unwanted song from your library folder without having it downloaded again.

- Auth.

    After launching first time, script will ask you to login at YouTube website. Auth data will be stored at library/.ytldl2 folder, encrypted with provided password.

- Config.

    It contains following library parameters:
    - Home items filter.
        
        By default script will download _songs_ only from `Your Likes`, `My Supermix` and `My Mix *` playlists, skipping all videos and channels. It's rather reasonable defaults: these playlists keep every song you like and they update daily. It's a good idea to launch script at least once a day to keep your library updated.
    
        You can populate it with your favorite playlists, channels and videos and you are ready to go. If you want to retain everything, set field to `null` (example: `"channels": null`), but it isn't recommended.

### Logs directory
Scipt stores last log into `your_library/.logs` directory. To make script log everything, run script with `--debug` argument.
