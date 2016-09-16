import sqlite3
from pprint import pprint

sqlite_file = "/Users/nehaludyavar/Documents/Udacity Courses/P3 - Wrangle OpenStreetMap Data/Vancouver OSM/vancouver_osm.db"

conn = sqlite3.connect(sqlite_file)
cur = conn.cursor()

cafes = "SELECT nodes_tags.value, COUNT(*) as num \
         FROM nodes_tags \
            JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='coffee_shop') AS cafes \
            ON nodes_tags.id = cafes.id \
         WHERE nodes_tags.key = 'name' \
         GROUP BY nodes_tags.value \
         ORDER BY num DESC;"

cuisines = "SELECT nodes_tags.value, COUNT(*) as num \
            FROM nodes_tags \
                JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') AS restaurants \
                ON nodes_tags.id = restaurants.id \
            WHERE nodes_tags.key = 'cuisine' \
            GROUP BY nodes_tags.value \
            ORDER BY num DESC;"

cur.execute(cafes)
#cur.execute(cuisines)

rows = cur.fetchall()

pprint(rows)
