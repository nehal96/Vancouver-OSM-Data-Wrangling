import sqlite3
from pprint import pprint

sqlite_file = "/Users/nehaludyavar/Documents/Udacity Courses/P3 - Wrangle OpenStreetMap Data/Vancouver OSM/SQLite Database/vancouver_osm.db"

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

postal_codes = "SELECT tags.value, COUNT(*) as num \
                FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags  \
                WHERE tags.key = 'postcode' AND tags.type='addr' \
                GROUP BY tags.value \
                ORDER BY num DESC;"

postcode_95326 = "SELECT * \
                  FROM nodes \
                  WHERE id IN (SELECT DISTINCT(id) FROM nodes_tags WHERE key='postcode' AND value=95326);"

specific_addr = "SELECT * \
                 FROM nodes_tags \
                 WHERE id='3129993831' and type='addr';"



cur.execute(cafes)
cur.execute(cuisines)
cur.execute(postal_codes)
cur.execute(postcode_95326)
cur.execute(specific_addr)

rows = cur.fetchall()

pprint(rows)
