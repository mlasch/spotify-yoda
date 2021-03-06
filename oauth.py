import requests
import base64
import json
import configparser

from urllib.parse import urlencode, \
                        urlparse, \
                        parse_qs,\
                        quote_plus

class ConfigPersist(object):
    def __init__(self, filename='default.ini'):
        self.filename = filename
        self.config = configparser.ConfigParser()
        self.config.read(self.filename)

    def get_state(self):
        return self.config['DEFAULT']

    def update_token(self, access_token = None, refresh_token = None):
        if access_token:
            self.config['DEFAULT']['access_token'] = access_token

        if refresh_token:
            self.config['DEFAULT']['refresh_token'] = refresh_token

        # write changes to config file 
        with open(self.filename, 'w') as fh:
            self.config.write(fh)

class OAuth2(object):
    def __init__(self, config_persist):
        self.config_persist = config_persist

    def refresh_token(self):
        print("REFRESH TOKEN")
        payload = {'grant_type': 'refresh_token',
                    'refresh_token': self.config_persist.get_state()['refresh_token']}
        headers = { 'Authorization': 'Basic {}'.format(
                            base64.b64encode(
                                self.config_persist.get_state()['client_id'].encode('ascii') + \
                                b':' + \
                                self.config_persist.get_state()['client_secret'].encode('ascii')).decode('utf-8')
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
        #self.config_persist.get_state()['access_token'] = new_token['access_token']
        self.config_persist.update_token(access_token = new_token['access_token'])

        return True

    def request_token(self, code, state):
        """ Get refresh and access token """

        payload = {'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': 'https://localhost/api'}
    
        headers = { 'Authorization': 'Basic {}'.format(
                            base64.b64encode(
                                self.config_persist.get_state()['client_id'].encode('ascii') + \
                                b':' + \
                                self.config_persist.get_state()['client_secret'].encode('ascii')).decode('utf-8')
                            ), 
                    'Accept': 'application/json', 
                    'Content-Type': 'application/x-www-form-urlencoded' }
    
        r = requests.post("https://accounts.spotify.com/api/token", 
                data=urlencode(payload), headers=headers)

        print(r.status_code, r.text)
        if r.status_code == 200:
            new_tokens = json.loads(r.text)
            self.config_persist.update_token(access_token = new_tokens['access_token'], 
                                             refresh_token = new_tokens['refresh_token'])

    def authorize(self, redirect_uri="https://localhost/api"):
        scope = "user-read-currently-playing"
        state = "some_state"
        client_id = self.config_persist.get_state()['client_id']
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
        return self.config_persist.get_state()['access_token']