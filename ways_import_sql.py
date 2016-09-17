import sqlite3
import csv
import pprint

sqlite_file = "/Users/nehaludyavar/Documents/Udacity Courses/P3 - Wrangle OpenStreetMap Data/Vancouver OSM/vancouver_osm.db"

WAYS_CSV = "ways.csv"

conn = sqlite3.connect(sqlite_file)                 # Connects to SQLite database

cur = conn.cursor()                                 # Creates cursor object

cur.execute('''DROP TABLE IF EXISTS ways;''')
""" Deletes ways table if it already exists """
conn.commit()                                       # Commits command

cur.execute('''
    CREATE TABLE IF NOT EXISTS ways(id INTEGER PRIMARY KEY, user TEXT, uid INTEGER,
    version TEXT, changeset INTEGER, timestamp DATE)
''')
""" Creates new ways table if it doesn't already exists using ways table
schema
"""
conn.commit()                                       # Commits command

def UnicodeDictReader(utf8_data, **kwargs):
    """ CSV reader that handles utf-8 encoding """
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key: unicode(value, 'utf-8') for key, value in row.iteritems()}



with open(WAYS_CSV, 'rb') as csvfile:
    csv_reader = UnicodeDictReader(csvfile)
    SQL = """INSERT INTO ways(id, user, uid, version, changeset, timestamp)
          VALUES (:id, :user, :uid, :version, :changeset, :timestamp)"""
    """ Imports CSV data into ways table using provided schema """
    with sqlite3.connect(sqlite_file) as conn:
        cur = conn.cursor()
        cur.executemany(SQL, csv_reader)
        conn.commit()
