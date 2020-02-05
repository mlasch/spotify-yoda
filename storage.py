from datetime import datetime

from peewee import SqliteDatabase, Model, CharField, DateTimeField

db = SqliteDatabase('tracks.db')

class Tracks(Model):
    track_id = CharField()
    title = CharField()
    artist = CharField()
    album = CharField()
    album_url = CharField()
    create_date = DateTimeField(default=datetime.now)

    class Meta:
        database = db # This model uses the "tracks.db" database.

class Storage(object):
    def __init__(self):

        db.connect()
        db.create_tables([Tracks])

    def get_last_track_id(self):
        return list(Tracks.select().order_by(Tracks.id.desc()).limit(1))[0].track_id

    def insert(self, track_id, title, artist, album, album_url):
        Tracks.create(track_id=track_id, title=title, artist=artist, album=album, album_url=album_url)

    def get_tracks(self, start, end):
        offset = start - 1
        limit = end - offset
        return [
                {   'track_id': track.track_id, 
                    'title': track.title,
                    'artist': track.artist,
                    'album': track.album,
                    'album_url': track.album_url
                } for track in Tracks.select().order_by(Tracks.id.desc()).limit(limit).offset(offset)]

if __name__ == '__main__':
    db.connect()
    db.create_tables([Tracks])
    
    for track in Tracks.select().order_by(Tracks.id.desc()):
        print(track.create_date, track.track_id, track.title, track.artist, track.album, track.album_url)


