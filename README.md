# Spotify played song logger

This tools logs all songs played by an account and saves them in a database. Spotify themselves do not offer a feature to search all played songs ever.

## Usage

The `client_id` and `client_secret` should be generated on the Spotify Developers Dashboard. `access_token` and `refresh_token` can be initialized with a random string, the will be overwritten with new values from the OAuth2 sequence.

**example.ini**
```
client_id = <xxx>
client_secret = <yyy>
access_token = <foo>
refresh_token = <bar>
```

```
./poll.py
```
