import sqlite3
import csv
import pprint

sqlite_file = "/Users/nehaludyavar/Documents/Udacity Courses/P3 - Wrangle OpenStreetMap Data/Vancouver OSM/vancouver_osm.db"
NODES_CSV = "nodes.csv"

conn = sqlite3.connect(sqlite_file)
cur = conn.cursor()

cur.execute('''DROP TABLE IF EXISTS nodes;''')
conn.commit()

cur.execute('''
    CREATE TABLE IF NOT EXISTS nodes(id INTEGER PRIMARY KEY, lat REAL,
    lon REAL, user TEXT, uid INTEGER, version TEXT, changeset INTEGER, timestamp DATE)
''')
conn.commit()


def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key: unicode(value, 'utf-8') for key, value in row.iteritems()}



with open(NODES_CSV, 'rb') as csvfile:
    csv_reader = UnicodeDictReader(csvfile)
    SQL = """INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp)
          VALUES (:id, :lat, :lon, :user, :uid, :version, :changeset, :timestamp)"""
    with sqlite3.connect(sqlite_file) as conn:
        cur = conn.cursor()
        cur.executemany(SQL, csv_reader)
        conn.commit()
