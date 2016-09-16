import csv
import sqlite3
import pprint

NODES_CSV = "nodes.csv"
NODES_TAGS_CSV = "nodes_tags.csv"
WAYS_CSV = "ways.csv"
WAY_NODES_CSV = "way_nodes.csv"
WAY_TAGS_CSV = "way_tags.csv"

NODES_SQL = "nodes.db"
NODES_TAGS_SQL = "nodes_tag.db"

NODES_TABLE_NAME = """nodes"""
NODES_TABLE_PARAMS = """(id INTEGER, lat TEXT, lon TEXT, user TEXT, uid TEXT, version TEXT, changeset TEXT, timestamp TEXT
)"""
NODES_TABLE_FIELDS = """(id, lat, lon, user, version, changeset, timestamp)"""
NODES_TABLE_VALUES = """(:id, :lat, :lon, :user, :version, :changeset, :timestamp)"""

NODES_TAGS_TN = """nodes_tags"""
NODES_TAGS_TABLE_PARAMS = """(id INTEGER, key TEXT, value TEXT, type TEXT, FOREIGN KEY (id) REFERENCES nodes(id))"""
NODES_TAGS_TF = """(id, key, value, type)"""
NODES_TAGS_TV = """(:id, :key, :value, :type)"""

def UnicodeDictReader(utf8_data, **kwargs):
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key: unicode(value, 'utf-8') for key, value in row.iteritems()}

def sql_importer(csv_file, sql_file, table_name, table_params, table_fields, table_values):
    conn = sqlite3.connect(sql_file)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE""" + """ """ + table_name + table_params)
    conn.commit()
    with open(csv_file, 'rb') as csvfile:
        csv_reader = UnicodeDictReader(csvfile)
        SQL = """INSERT INTO""" + """ """ + table_name + """ """ + table_fields + """ """ + """VALUES""" + """ """ + table_values
    cur.executemany(SQL, csv_reader)
    conn.commit()

#sql_importer(NODES_TAGS_CSV, NODES_TAGS_SQL, NODES_TAGS_TN, NODES_TAGS_TABLE_PARAMS, NODES_TAGS_TF, NODES_TAGS_TV)


cur.execute('SELECT user, count(*) FROM nodes GROUP BY user ORDER BY count(*) desc')
all_rows = cur.fetchall()
pprint.pprint(all_rows)

conn.close()
