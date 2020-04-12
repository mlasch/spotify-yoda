#!/usr/bin/env python3

import configparser
import json
import requests

from threading import Thread, Event
from time import sleep
from pprint import pprint

from flask import Flask
from flask import jsonify

from storage import Storage
from poll import OAuth2, SpotifyAPI

config = configparser.ConfigParser()
config.read('example.ini')


def do_poll(stop_event, s, oauth2):
    try:
        last_track_id = s.get_last_track_id()
    except IndexError:
        last_track_id = ''
    
    api = SpotifyAPI(oauth2)

    while not stop_event.is_set():
        try:
            play = api.currently_playing()
        except requests.exceptions.ConnectionError as e:
            # TODO do error handling properly
            print(e)
            play = {}
        
        if play != {}:
            track_id = play['item']['id']
            title = play['item']['name']
            album = play['item']['album']['name']
            album_url = max(play['item']['album']['images'], key=lambda img:img['width'])['url']
            artists = ",".join([artist['name'] for artist in play['item']['artists']])

            
            #for artist in artists:
            #    print(artist['name'], end=", ")
                
            if last_track_id != track_id:
                print("Inserted {}, {}, {}, {}, {}".format(track_id, title, artists, album, album_url))
                s.insert(track_id, title, artists, album, album_url)
                last_track_id = track_id
        stop_event.wait(5)


def start_server(s):
    
    app = Flask(__name__)
    
    @app.route("/")
    def root():
        return app.send_static_file('index.html')

    @app.route("/tracks/<start>/<end>")
    def tracks(start, end):
        try:
            start = int(start)
            end = int(end)
        except ValueError:
            return "ValueError"

        if start > end and start > 0:
            return "Start should be smaller than end"

        track_list = s.get_tracks(start, end)
        return jsonify(track_list)


    app.run(host="0.0.0.0")


if __name__ == "__main__":
    s = Storage()
    oauth2 = OAuth2(dict(config['DEFAULT']))
    
    try:
        stop_event = Event()

        t = Thread(target=do_poll, args=(stop_event, s, oauth2))
        t.start()

        start_server(s)
        stop_event.set()
        
        #t.join(1)

    except KeyboardInterrupt:
        stop_event.set()
        #t.join()

        # save current tokens
        state = oauth2.get_state()
        config['DEFAULT'] = state
        with open('example.ini', 'w') as configfile:
            config.write(configfile)
       
        print("cleaned up")

