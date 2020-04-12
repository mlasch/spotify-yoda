import requests
import json

class SpotifyAPI(object):
    def __init__(self, auth):
        self.auth = auth
    
    def currently_playing(self):
        r = requests.get("https://api.spotify.com/v1/me/player/currently-playing",
                headers = { 'Authorization': 'Bearer {}'.format(self.auth.get_token()),
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'})
        
        print(r.status_code, "With ACCESS-TOKEN: {}".format(self.auth.get_token()))
        
        if r.status_code == 401:
            if self.auth.refresh_token():
                return self.currently_playing()
            else:
                self.auth.authorize()
                return self.currently_playing()
        
        elif r.status_code == 200:
            return json.loads(r.text)

        elif r.status_code == 204:
            return {}
        else:
            raise RuntimeError
