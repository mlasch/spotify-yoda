#!/usr/bin/env python3

import requests
import json
import base64
import configparser

from urllib.parse import urlencode, \
                        urlparse, \
                        parse_qs,\
                        quote_plus
from time import sleep
from pprint import pprint

config = configparser.ConfigParser()
config.read('example.ini')


class OAuth2(object):
    def __init__(self, api_state):
        self.api_state = api_state

    def get_state(self):
        return self.api_state

    def refresh_token(self):
        print("REFRESH TOKEN")
        payload = {'grant_type': 'refresh_token',
                    'refresh_token': self.api_state['refresh_token']}
        headers = { 'Authorization': 'Basic {}'.format(
                            base64.b64encode(
                                self.api_state['client_id'].encode('ascii') + \
                                b':' + \
                                self.api_state['client_secret'].encode('ascii')).decode('utf-8')
                            ), 
                    'Accept': 'application/json', 
                    'Content-Type': 'application/x-www-form-urlencoded' }

        r = requests.post("https://accounts.spotify.com/api/token", 
                data=urlencode(payload), headers=headers)
        
        print(r.status_code)
        print(r.text)

        if r.status_code != 200:
            return False
        # 400 if refresh token is unvalid

        new_token  = json.loads(r.text)
        self.api_state['access_token'] = new_token['access_token']

        return True

    def request_token(self, code, state):
        print(code)
        print(state)
        payload = {'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': 'https://localhost/api'}
    
        headers = { 'Authorization': 'Basic {}'.format(
                            base64.b64encode(
                                self.api_state['client_id'].encode('ascii') + \
                                b':' + \
                                self.api_state['client_secret'].encode('ascii')).decode('utf-8')
                            ), 
                    'Accept': 'application/json', 
                    'Content-Type': 'application/x-www-form-urlencoded' }
    
        r = requests.post("https://accounts.spotify.com/api/token", 
                data=urlencode(payload), headers=headers)
    
        #print(payload)
        #print(headers)

        print(r.status_code, r.text)
        if r.status_code == 200:
            new_tokens = json.loads(r.text)
            self.api_state['access_token'] = new_tokens['access_token']
            self.api_state['refresh_token'] = new_tokens['refresh_token']
    
    def authorize(self, redirect_uri="https://localhost/api"):
        scope = "user-read-currently-playing"
        state = "some_state"
        client_id = self.api_state['client_id']
        cont = "https://accounts.spotify.com/authorize?" + \
            "response_type=code&" + \
            "scope={}&".format(scope) + \
            "redirect_uri={}&".format(quote_plus(redirect_uri)) + \
            "state={}&".format(state) + \
            "client_id={}".format(client_id)
        
        url = "https://accounts.spotify.com/login?continue={}".format(quote_plus(cont))
        print("No API token available or expired, go to:")
        print(url)
        code_url = input('Paste the redirected url here > ') 
        url_parsed = urlparse(code_url)
        query = parse_qs(url_parsed.query)
    
        return self.request_token(query['code'][0], query['state'][0])

    def get_token(self):
        return self.api_state['access_token']
    

class SpotifyAPI(object):
    def __init__(self, auth):
        self.auth = auth
    
    def currently_playing(self):
        r = requests.get("https://api.spotify.com/v1/me/player/currently-playing",
                headers = { 'Authorization': 'Bearer {}'.format(self.auth.get_token()),
                            'Accept': 'application/json',
                            'Content-Type': 'application/json'})
        
        print(r.status_code, "Access with TOKEN: {}".format(self.auth.get_token()))
        
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
    
    
if __name__ == "__main__":
    oauth2 = OAuth2(dict(config['DEFAULT']))
    
    print(dict(config['DEFAULT']))
    
    api = SpotifyAPI(oauth2)

    try:
        while True:
            play = api.currently_playing()
            print(play)
            
            if play != {}:
               title_id = play['item']['id']
               title = play['item']['name']

               album = play['item']['album']['name']
               artists = play['item']['artists']
            
               print(title_id)
               print(title)

               for artist in artists:
                   print(artist['name'], end=", ")
                    
               print(album)
            
            sleep(5)

    except KeyboardInterrupt:
        state = oauth2.get_state()
        config['DEFAULT'] = state
        with open('example.ini', 'w') as configfile:
            config.write(configfile)

