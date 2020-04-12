# Spotify song logger
This tools logs all songs played by an account and saves them in a local database. Spotify themselves do not offer such a feature to search all song played.

## Usage

The `client_id` and `client_secret` should be generated on the Spotify Developers Dashboard. `access_token` and `refresh_token` can be initialized with a random string, the will be overwritten with new values from the OAuth2 sequence.

**default.ini**
```
client_id = <xxx>
client_secret = <yyy>
access_token = <foo>
refresh_token = <bar>
```

```
./server.py
```
