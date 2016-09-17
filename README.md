# OpenStreetMap Data Wrangling Project

### Abstract
For this project I've decided to download OpenStreetMap data for Vancouver from [Mapzen](https://mapzen.com/data/metro-extracts/). The full metro extract was 175MB, so I used Mapzen's Custom Extract tool to select an area with a file size of 72MB.

Once I had the OSM file, I proceeded to familiarize myself with the data, before beginning the auditing and cleaning. I counted the tag types (nodes, ways, etc.), and then explored the users and their contributions. I then audited the street names and postal codes to check if they were all consistent (for example, if 'Street' was not sometimes written as 'St.'), or that all postal codes were written in the spaced form (for example, V6T 1Z4). After that was complete, I wrote code to update and change the inconsistent street names and postal codes.

After the data cleaning was complete, I prepared the data for database entry. The XML was parsed and organized according to an SQL schema. The data was then converted from XML into CSV before being imported into a SQLite database.

Finally, I explored my SQL database of Vancouver OpenStreetMap data by running a few queries and showing their results.



### Map Area

The map area is a subset of the Vancouver metro area on Mapzen. Since it was a custom extract, there is no direct link, but the bounds of the area are:

- Minimum latitude = 49.2404657
- Minimum longitude = -123.2185363
- Maximum latitude = 49.3329531
- Maximum longitude = -123.0743408

Vancouver is the city that I study in. I've been here a bit over two years, so I'm excited to see what interesting things pop up through the database queries.

### Playing Around with the Data

#### Tag Type Count

The 3 main elements of OpenStreetMap data are nodes, ways and relations. Each element has tags, which describe what exactly that point in the map is, be it a street, traffic light or a Starbucks. All this does most of the legwork in describing map data.

The `count_tag` function iteratively parses through the OSM data, and if a element type (node, way) exists in the `tags` dictionary, it adds 1 to the total. If not, it adds the tag to the dictionary and initiates the count at 1. Here's what the code looks like:

```python
def count_tags(filename):
    tags = {}
    for event, elem in ET.iterparse(filename, events=("start", )):
        if elem.tag in tags.keys():
            tag_field = "%s" % elem.tag
            tags[tag_field] += 1
        else:
            tag_field = "%s" % elem.tag
            tags[tag_field] = 1

    return tags
```

Running this on my Vancouver dataset and printing the results gave the following dictionary:

```python
tags = {
  'bounds': 1,
  'member': 4903,
  'nd': 397410,
  'node': 308209,
  'osm': 1,
  'relation': 948,
  'tag': 134303,
  'way': 63203
}
```

A sizeable dataset indeed.

#### Exploring Users

The next demo was to write code to explore the user information that is available in each main element. The user items in each data point include 'user', which is the person's username, and 'uid', which is the person's user ID.

The `process_map` function goes through each node, way, and relation element and looks for the 'user' tag. If that particular user is not already on the `users_array`, he or she is added to it. This way, each user is represented once, and you get a list of all the users that have provided data to this OpenStreetMap dataset.

```python
def process_map(filename):
    users_array = []
    for event, element in ET.iterparse(filename, events=("start", )):
        if element.tag in ["node", "way", "relation"]:
            user = get_user(element)
            if user not in users_array:
                users_array.append(user)
            else:
                pass

    users = set(users_array)

    return users
```

Running the code on my Vancouver dataset returned a huge list of 1236 users. More database queries will be done on user data once the cleaned data is inserted in a SQL database.


### Problems Encountered in Data

#### Abbreviated Street Names

One of the most obvious area for error is consistency in street names. Since OpenStreetMap is an open-source community, and despite the guidelines posted, users may often name streets differently. For example, 'Avenue' may occasionally be written as 'Ave' or 'Ave.'. It's useful to have all the same street types consistently, so an audit of street types was done.

The audit function parses through the XML and looks for tags with a `k` attribute of `addr:street`, and if it doesn't match a list of accepted values - the `expected` - it is added to a dictionary.

```python
def audit(osmfile):
    street_types = defaultdict(set)
    for event, element in ET.iterparse(osmfile, events=("start", )):
        if element.tag == "way" or element.tag == "node":
            for tag in element.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types
```

The audit returned a dictionary with around 40 key:value pairs. Below is a sample of the entire dictionary:

```python
street_audit = {
    'Ave': 'West 3rd Ave',
    'Ave.': 'Forbes Ave.',
    'Dr.': 'Marine Dr.',
    'Rd': 'Capilano Rd',
    'St': 'Beatty St'
}
```

Running the audit also returns correct street names that were not a part of `expected`, such as 'Terminal', 'Crescent' and 'Kingsway', just to name a few.

Since these are not incorrect street names, I updated the expected list and ran the audit again, reducing the number of incorrect street names.

The next step was to write code that converted the incorrect street types into the correct ones. The `update_name` function parses through the audit dictionary and compares its keys with the keys of the `mapping` dictionary, which maps common mistakes with the correct version. If there is a match, it will change the incorrect street type to the correct one. If there isn't, it will add the street type and the street name to a dictionary named 'unlisted', so I can see what exactly the issue is on a case-by-case basis.

```python
def update_name(osmfile, mapping):
    unlisted = {}
    street_types = audit(osmfile)
    for street_type, name in street_types.iteritems():
        if street_type in mapping.keys():
            better_name = re.sub(street_type, mapping[street_type], name)
            print name, "=>", better_name
        else:
            unlisted[street_type] = name
    pprint.pprint(dict(unlisted))
```

Running this code, you get the old name and the conversion to the new name, which looks like this:

```python
Mainland St. => Mainland Street
Capilano Rd. => Capilano Road
Marine Dr. => Marine Drive
```

And finally, you get the `unlisted` dictionary for all remaining street type, street name pairs.

```python
unlisted = {
  'Denmanstreet': 'Denmanstreet',
  'Cervenon': 'Route De Cervenon', # It's in France
  'Gascho': 'Rua Emidia Prestini Gascho', # In Brazil
  'Mickiewicza': 'Adama Mickiewicza', # In Poland
  'Rasen': 'Am Rasen' # Doesn't exist
}
```

Finally, I had to go through the `unlisted` dictionary to see why their names weren't getting updated. Often, they were just different kinds of mistakes. For example, `Denmanstreet` was actually supposed to be `Denman Street`. A simple fix for this was to just update the `mapping` dictionary to account for these types of mistakes.

The other kind of mistake was street names either did not exist, or were not situated in Vancouver. There were street names from Mexico, Poland, and Germany, among other countries. It is not known how these street names appeared in the audit, but the solution for this is to delete the particular data from the file.

#### Inconsistent Postal Codes

The next area for auditing and cleaning was postal codes. Canadian postal codes are alphanumeric 6-character codes, with the first 3 being the Forward Sortation Area (FSA) and the last 3 being the local delivery unit. The correct format is of the form A1A 1A1, but A1A1A1 is common too. For consistency, I wanted to keep all postal codes in the spaced form, and that was the reason for this audit and clean up.

```python
def audit(osmfile):
    """ Iteratively parses through each element in an XML file (in this case
        for OSM), and first checks if the element is a node or way element. If
        True, then the function with iterate through each tag in the node or way
        element, and run the 'is_postal_code' function on it. If True, the
        function will run the 'audit_postal_code' function on it.

        Returns:
            list with incorrect postcodes.
    """
    correct_PCs = []
    incorrect_PCs = []
    for event, element in ET.iterparse(osmfile, events=("start", )):
        if element.tag == 'node' or element.tag == 'way':
            for tag in element.iter('tag'):
                if is_postal_code(tag):
                    audit_postal_code(correct_PCs, incorrect_PCs, tag.attrib['v'])

    return incorrect_PCs
```

Running this code, I got a list of 104 incorrect postal codes, of which I'll show a small sample:

```python
incorrect_PCs = [
    'V53 3H9',
    'V6Z1M4',
    'V6Z1R2',
    'v5t 4r8',
    'BC V6B 2E2',
    'V5T-4T1;V5T 4T1',
    '179-0085',
    '95326'
]
```

The audit returns a list of incorrect postal codes which I can take a look at and then decide how to clean it. I noticed a lot of 4-digit and 5-digit numerical postal codes, which is not used in Canada, so there is clearly some errors. Also the no-space version was quite common, as well as postal codes where all the letters were lowercase. With that information, I set to write a function that would update the postal codes to the correct version.

```python
def update_postal_code(osmfile):
    """ If a postcode is in the list returned by the audit function, it first
        removes any whitespace and then makes the string uppercase. Then it uses
        the postal_code_re_alt regex to find a match, and if one is found, it
        groups the match object and returns the string grouped by 3. If there is
        no match, it appends the postcode to the problem_PCs list. Next, it
        iterates through the postcodes in this list, and uses the
        postal_code_number_re regex to splits the list into numerical and
        non-numerical postcode lists for further potenial cleaning.
    """
    incorrect_PCs = audit(osmfile)
    for postcode in incorrect_PCs:
        stripped_upper = postcode.strip().upper()
        m = postal_code_re_alt.match(stripped_upper)
        if m:
            PC = m.group()
            char_list = list(PC)
            post_code = char_list[0] + char_list[1] + char_list[2] + " " + \
                    char_list[3] + char_list[4] + char_list[5]
            return post_code
        else:
            problem_PCs.append(postcode)

    for postcode in problem_PCs:
        n = postal_code_number_re.search(postcode)
        if n:
            number_PC = n.group()
            number_PCs.append(number_PC)
            problem_PCs.remove(number_PC)
        else:
            pass
```
Now, the incorrect postal codes are split into two lists: numerical and non-numerical. When I ran this code, the lists weren't perfectly separate, and at times the same numerical postal code appeared in both lists (for some reason). Not wanting to start deleting incorrect postal codes just yet, I decided to leave this further cleaning for a later time.

I'm sure more problems will appear as I explore the dataset through SQL, but for now let this complete the cleaning and let's prepare the data to import into SQL.

### Preparing for Database Entry

#### Schema

Before I can import the data into a SQL database, I must convert the XML data into CSV, organized based on a schema. This Python schema will have the same columns as the schema of the SQL tables that I'll import to later.

So the first thing I need to build is the schema, so that I know how to organize the XML data as I parse through each element. [This is the schema](https://gist.github.com/nehal96/5d4f5330797dda7a83d09620d566a381) that I used:


#### Shaping the Elements

Now that I have the schema ready, I need to shape each XML element into this format. This is done using the `shape_element` function, which iteratively parses through each element, and if it is a node or way element along with their respective tags, it will organize the data according to the schema.

This is also the perfect opportunity to update the incorrect street types onto the file, as well as delete the foreign names.

```python
def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []

    if element.tag == 'node':
        for item in NODE_FIELDS:
            node_attribs[item] = element.attrib[item]
        for child in element:
            if child.tag == 'tag':
                node_tag = {}
                for item in NODE_TAG_FIELDS:
                    if item == 'id':
                        node_tag[item] = element.attrib['id']
                    elif item == 'key':
                        key = child.attrib['k']
                        if key == 'addr:street':
                            # This is where I update the incorrect street names
                            child.attrib['v'] = shape_update_name(child.get('v'), mapping)
                        key_split = key.split(":")
                        if PROBLEMCHARS.search(key):
                            pass
                        elif len(key_split) == 2:
                            node_tag[item] = key_split[1]
                        elif len(key_split) == 3:
                            node_tag[item] = key_split[1] + ":" + key_split[2]
                        else:
                            node_tag[item] = child.attrib['k']
                    elif item == 'value':
                        node_tag[item] = child.attrib['v']
                    elif item == 'type':
                        key = child.attrib['k']
                        key_split = key.split(":", 1)
                        if len(key_split) > 1:
                            node_tag[item] = key_split[0]
                        else:
                            node_tag[item] = 'regular'
                tags.append(node_tag)
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        for item in WAY_FIELDS:
            way_attribs[item] = element.attrib[item]
        for index, child in enumerate(element):
            if child.tag == 'nd':
                way_node = {}
                for item in WAY_NODES_FIELDS:
                    if item == 'id':
                        way_node[item] = element.attrib['id']
                    elif item == 'node_id':
                        way_node[item] = child.attrib['ref']
                    elif item == 'position':
                        way_node[item] = index
                way_nodes.append(way_node)
            if child.tag == 'tag':
                way_tag = {}
                for item in WAY_TAGS_FIELDS:
                    if item == 'id':
                        way_tag[item] = element.attrib['id']
                    elif item == 'key':
                        key = child.attrib['k']
                        if key == 'addr:street':
                          child.attrib['v'] = shape_update_name(child.get('v'), mapping)
                        key_split = key.split(":")
                        if PROBLEMCHARS.search(key):
                            pass
                        elif len(key_split) == 2:
                            way_tag[item] = key_split[1]
                        elif len(key_split) == 3:
                            way_tag[item] = key_split[1] + ":" + key_split[2]
                        else:
                            way_tag[item] = child.attrib['k']
                    elif item == 'value':
                        way_tag[item] = child.attrib['v']
                    elif item == 'type':
                        key = child.attrib['k']
                        key_split = key.split(":")
                        if len(key_split) > 1:
                            way_tag[item] = key_split[0]
                        else:
                            way_tag[item] = 'regular'
                tags.append(way_tag)
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}
```

[When I ran this function, I forgot to change the process_map function to create a new OSM file, so that the old one is not overwitten. Thankfully the code worked as planned, albeit overwriting the original OSM file. I decided not to proceed with deleting the non-existent/foreign street names, and leave that for a later time]

#### Converting to CSV

The final step in the preparation is to convert the data from XML to CSV using the schema, `shape_element` function, and a new `process_map` function that actually writes the data into a .csv file.

The `process_map` function uses helper functions `get_element` and `validate_element`, as well as the `class UnicodeDictWriter` to make the code more organized and to avoid repetition. All the functions can be found in the full Github repository.

```python
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'w') as nodes_file, \
         codecs.open(NODES_TAG_PATH, 'w') as nodes_tags_file, \
         codecs.open(WAYS_PATH, 'w') as ways_file, \
         codecs.open(WAY_NODES_PATH, 'w') as way_nodes_file, \
         codecs.open(WAY_TAGS_PATH, 'w') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        nodes_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAG_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        nodes_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    nodes_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])
```

Running this code creates .csv files for each future database table, with a header of the table fields. The next step is to create the SQLite database, create the tables and import the CSV files into them.

### Creating the Database

The first thing I tried was to write a function in Python that created all the tables in a SQL database, and automatically imported the csv files into each one. Unfortunately that led to a lot of errors, so I kept that aside and I thought I'd first begin by doing it manually using SQLite on the Terminal.

The tables were created using [this schema](https://gist.github.com/swwelch/f1144229848b407e0a5d13fcb7fbbd6f), which has to be the same one used when converting XML to CSV.

The first thing I needed to do was create a new database to create all the tables in. So after making my way to the folder I wanted to be in, I made a new sqlite database:

```sql
$ sqlite3 vancouver_osm.db
```
Running this creates a new database where I can create the tables.

```sql
sqlite> CREATE TABLE nodes_tags(
   ...>   id INTEGER,
   ...>   key TEXT,
   ...>   value TEXT,
   ...>   type TEXT,
   ...>   FOREIGN KEY (id) REFERENCES nodes(id)
   ...> );
```

Now that I have a `nodes_tags` table, I can import my `nodes_tags.csv` file into it.

```sql
sqlite> .mode csv
sqlite> .import nodes_tags.csv nodes_tags
```

And that's one table done! I did a small query to check if the data has been imported correctly, which I'll show later when I document all the queries.

This same process was used to create the `ways_tags` and `ways_nodes` tables, and ofcourse to import their respective .csv files into them.

The `nodes` and `ways` tables, however, erred when this process was used. This, I guess, is because they contain primary keys, but I'm not entirely sure why. The fix for this was to use SQLite's Python module to import the .csv files (and good practice).

```python
sqlite_file = "vancouver_osm.db"
NODES_CSV = "nodes.csv"


conn = sqlite3.connect(sqlite_file)   # Connect to the database
cur = conn.cursor()                   # Create a cursor object

cur.execute('''DROP TABLE IF EXISTS nodes;''')  # Drops the table if one with that name already exists
conn.commit()

cur.execute('''
    CREATE TABLE IF NOT EXISTS nodes(id INTEGER PRIMARY KEY, lat REAL,
    lon REAL, user TEXT, uid INTEGER, version TEXT, changeset INTEGER, timestamp DATE)
''')
# Creates a new table if another with the name doesn't exist (it shouldn't now that I dropped it earlier)
conn.commit()


def UnicodeDictReader(utf8_data, **kwargs):                 # CSV reader that handles utf-8 encoding
    csv_reader = csv.DictReader(utf8_data, **kwargs)
    for row in csv_reader:
        yield {key: unicode(value, 'utf-8') for key, value in row.iteritems()}


with open(NODES_CSV, 'rb') as csvfile:
    csv_reader = UnicodeDictReader(csvfile)
    SQL = """INSERT INTO nodes(id, lat, lon, user, uid, version, changeset, timestamp)
          VALUES (:id, :lat, :lon, :user, :uid, :version, :changeset, :timestamp)"""
          # Inserts the data into the table in the particular column
    with sqlite3.connect(sqlite_file) as conn:
        cur = conn.cursor()
        cur.executemany(SQL, csv_reader)
        conn.commit()
```
Now, all the tables have been created in the database, and all the CSV data has been imported into their respective tables, so we can begin exploring!


## Exploring the data

### Data Overview

#### File Sizes

```
Vancouver_City.osm.......... 72.5 MB
vancouver_osm.db............ 88.6 MB
nodes.csv................... 27.1 MB
nodes_tags.csv.............. 0.77 MB
ways.csv.................... 04.1 MB
way_nodes.csv............... 09.5 MB
ways_tags.csv............... 03.8 MB
```

#### Number of nodes
```sql
sqlite> SELECT COUNT(*) FROM nodes;
```
308209

#### Number of ways
```sql
sqlite> SELECT COUNT(*) FROM ways;
```
63203

#### Number of Unique users
```sql
sqlite> SELECT COUNT(DISTINCT(uid))
   ...> FROM (SELECT uid FROM nodes UNION ALL SELECT uid FROM ways);
```
1132

#### Top 10 Contributing Users
```sql
sqlite> SELECT user, COUNT(*) as num
   ...> FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways)
   ...> GROUP BY user
   ...> ORDER BY num DESC
   ...> LIMIT 10;
```
```
keithonearth        111612
michael_moovelmaps  93147
still-a-worm        28216
rbrtwhite           21899
WBSKI               17164
pdunn               16904
MetVanRider123acme  12268
pnorman             6945
fmarier             5318
Nihat               5174   
```

#### Number of Users Posting Only Once
```sql
sqlite> SELECT COUNT(*)
   ...> FROM (SELECT user, COUNT(*) as num
   ...>       FROM (SELECT user FROM nodes UNION ALL SELECT user FROM ways)
   ...>       GROUP BY user
   ...>       HAVING num=1);
```
432

### Further Data Exploration

#### Postal Codes
```sql
sqlite> SELECT tags.value, COUNT(*) as num
   ...> FROM (SELECT * FROM nodes_tags UNION ALL SELECT * FROM ways_tags) AS tags
   ...> WHERE tags.key = 'postcode' AND tags.type='addr'
   ...> GROUP BY tags.value;
```
```
48-316   15
95326    14
V5V 3A4   7
V5Y 1R4   6
V6A 3T8   5
```

#### Specific Post Code ID
```sql
sqlite> SELECT *
   ...> FROM nodes
   ...> WHERE id IN (SELECT DISTINCT(id) FROM nodes_tags WHERE key='postcode' AND value='V6J 1M4');
```
```
id|lat|lon|user|uid|version|changeset|timestamp
1305430209|49.268151|-123.146189|david105|2982288|4|31951326|2015-06-12T21:23:46Z
```

#### Node Info from Post Code ID
```sql
sqlite> SELECT *
   ...> FROM nodes_tags
   ...> WHERE id='1305430209';
```
```
id|key|value|type
1305430209|name|Wow Interiors|regular
1305430209|shop|furniture|regular
1305430209|city|Vancouver|addr
1305430209|street|West 4th Avenue|addr
1305430209|postcode|V6J 1M4|addr
1305430209|province|BC|addr
1305430209|housenumber|1823|addr
```

#### Top 10 Amenities
```sql
sqlite> SELECT value, COUNT(*) as num
   ...> FROM nodes_tags
   ...> WHERE key='amenity'
   ...> GROUP BY value
   ...> ORDER BY num DESC
   ...> LIMIT 10;
```
```
bench            544
restaurant       435
cafe             297
fast_food        188
bicycle_parking  169
post_box         166
bank             79
toilets          63
pub              56
bar              48
```
No surprise to see bicycle_parking right up there in the Top 10 amenities, Vancouverites love biking around the city.

### Top 10 Cuisines
```sql
sqlite> SELECT nodes_tags.value, COUNT(*) as num
   ...> FROM nodes_tags
   ...>     JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurants') AS restaurants
   ...>     ON nodes_tags.id = restaurants.id
   ...> WHERE nodes_tags.key='cuisine'
   ...> GROUP BY nodes_tags.value
   ...> ORDER BY num DESC
   ...> LIMIT 10;
```
```
japanese    31
sushi       21
chinese     17
indian      12
pizza       11
mexican      9
italian      8
burger       7
vietnamese   7
greek        6
```
Japanse cuisine dominates the cuisines of this West Coast city, with two other Asian cuisines coming 3rd and 4th. Again, there is a question of this data's validity: does the 'japanese' tags include restaurants that serve sushi, and if so should it remain 'japanese', or should it be 'sushi'? Same with 'pizza' and 'italian' - is there an overlap or are they distinct cuisines by definition.

### Cafés of Vancouver

Let's take a closer look at the different kinds of cafés found around Vancouver, namely how many Starbucks are dispersed around the city.

```sql
sqlite> SELECT nodes_tags.value, COUNT(*) as num
   ...> FROM nodes_tags
   ...>     JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='coffee_shop') AS cafes
   ...>     ON nodes_tags.id = cafes.id
   ...> WHERE nodes_tags.key='name'
   ...> GROUP BY nodes_tags.value
   ...> ORDER BY num DESC
   ...> LIMIT 10;
```
```
Tim Hortons                    11
Starbucks                       6
Blenz Coffee                    3
JJ Bean                         2
49th Parallel & Lucky's Donuts  1
Bean Around The World           1
Bean around the World           1
Blenz                           1
Breka Bakery & Cafe             1
Bump n Grind Cafe               1
Caffé Artigiano                 1
Caffé Brixton                   1
Cuppa Joe                       1
Delany's Coffee                 1
Ed's Daily                      1
Elysian Coffee                  1
JJ Beans                        1
JJBean                          1
Kafka's Coffee and Tea          1
Revolver                        1
Sciué                           1
Smart Mouth                     1
Starbucks Coffee                1
Trees Organic                   1
Waves                           1
Willow Cafe & Bakery            1
```

Immediately it's clear that there are duplicate names that invalidate the count, particularly for the popular chains. Starbucks is written as 'Starbucks' and 'Starbucks Coffee'; Blenz is written as 'Blenz' and 'Blenz Coffee'; and a similar story for Bean Around The World and JJ Bean. This in an area that should be improved in a future audit on OSM data.

Also, my personal experience in Vancouver argues that there are way more than 7 Starbucks coffee shops in the city. So there is definitely lots of missing data in the dataset.

## Improving OSM data

To improve the data being added by users in OpenStreetMaps, I'd recommend implementing a gamification or badging system where users get their achievements recognized, and if they're not doing something correctly, they're notified through this same manner. I was/am a big fan of KhanAcademy's badge system, and often it motivated me to watch more videos or answer more exercises. Other than just adding some fun to the entire process, it also is a measure of trustworthiness of the user, and a check if users are adhering to the guidelines.

One issue with this is that it is a big and complicated system to implement. Being an open source community, OpenStreetMaps likely must measure the pros and cons of such a considerable step. Apart from being ambitious, the concept possesses an issue with the very thing that makes it better: incentive. If the gamification incentivizes to use OSM more, it might mean users abuse the system and add data as quickly as possible, in an effort to get more badges or points. In this case, data quality is compromised, and the effort is counter-productive. There must be a more efficient and effective check on data quality when it's being added, but again that's another system to add on. A simpler solution might be to just do more frequent audits on the data, or create a bot that finds inconsistencies in the data (or newly added data) very quickly.

## Conclusion

Auditing and cleaning data is a long and tedious process, but it is also arguably the most important. Finding and correcting mistakes in the data makes sure that any conclusions I make from it are accurate and trustworthy. It also makes the exploration concise and straightforward. Unfortunately, it's difficult to know what the mistakes are and where they might be beforehand, so going through the entire process like this invariably shows where there are errors. Using this information, I can go back and audit and clean the data, and redo the process. Also, I now know where mistakes usually end up and can use that knowledge in future OSM data analysis.

With clean and accurate data, one can make correct decisions based of it. Making decisions with wrong data is just as misguided as making decisions without data, so auditing and cleaning are extremely important steps. That's what I've learnt through this project.


***Areas to take this project forward:
- Auditing and cleaning coffee shop and restaurant data
- Deleting numerical/wrong postal codes and updating unique mistakes
- Deleting the non-existent/foreign street names from the dataset
- More detailed/new SQL queries with cleaner data (and possibly find more mistakes)
