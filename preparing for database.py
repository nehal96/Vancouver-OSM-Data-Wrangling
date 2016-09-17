import csv
import codecs
import re
import xml.etree.ElementTree as ET

import cerberus

import schema

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
""" Regex to get the last word in a string of words. This is where
    the street type (eg. Street) usually is.
"""

mapping = {
    "St": "Street",
    "St.": "Street",
    "Steet": "Street",
    "street": "Street",
    "Ave": "Avenue",
    "Ave.": "Avenue",
    "Rd": "Road",
    "Rd.": "Road",
    "Dr.": "Drive",
    "Denmanstreet": "Denman Street",
    "Jervis": "Jervis Street",
    "Broughton": "Broughton Street"
}
""" Dictionary that maps incorrect street types to correct street types """


VANCOUVER_CITY_OSM = "/Users/nehaludyavar/Downloads/Vancouver_City_v2.osm"
VANCOUVER_CITY_SAMPLE = "/Users/nehaludyavar/Downloads/Vancouver_City_Sample.osm"

NODES_PATH = "nodes.csv"
NODES_TAG_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "way_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
""" Regex to choose string from left side of colon """
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
""" Regex for problem characters """

SCHEMA = schema.schema
""" Imports the schema from the schema.py file """

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAG_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']
""" List of headers that will be on the CSV file, which is also the table
    parameters for the SQLite database that it will be imported into later.
"""

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                  problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    """ Iteratively parses through each element tag for some OSM XML file and
        adds the data from the tag into the dictionary provided in the schema.py
        file. Along the way, the street types are updated to clean out incorrect
        street types, and the postal codes are updated to make sure all postal
        codes are consistent in their representation. This is what's used to
        organize the XML data so that it can be imported into CSV files

        Returns:
            A dictionary with nodes and nodes_tags dictionaries, which include
            nodes attributes dictionary and tags list respectively.
            Another dictionary with ways, way_nodes and way_tags keys, with ways
            having a way attributes dictionary and way_nodes and way_tags
            including way_nodes and tags list respectively.
    """
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []

    if element.tag == 'node':
        for item in NODE_FIELDS:
            node_attribs[item] = element.get(item)
        for child in element:
            if child.tag == 'tag':
                node_tag = {}
                for item in NODE_TAG_FIELDS:
                    if item == 'id':
                        node_tag[item] = element.attrib['id']
                    elif item == 'key':
                        key = child.attrib['k']
                        if key == 'addr:street':
                            child.attrib['v'] = shape_update_name(child.get('v'), mapping) # Updates the street name
                        elif key == 'addr:postcode':
                            child.attrib['v'] = shape_update_postal_code(child.get('v')) # Updates the postal codes
                        elif PROBLEMCHARS.search(key):
                            pass
                        key_split = key.split(":")
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


# ================================ #
#           Helper Functions       #
# ================================ #

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()


def shape_update_name(name, mapping):
    unlisted = {}
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type in mapping.keys():
            name = re.sub(street_type, mapping[street_type], name)
        else:
            unlisted[street_type] = name
    return name

def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""

    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_strings = (
            "{0}: {1}".format(k, v if isinstance(v, str) else ", ".join(v))
            for k, v in errors.iteritems()
        )
        raise cerberus.ValidationError(
            message_string.format(field, "\n".join(error_strings))
        )


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)



# ================================ #
#           Main Function          #
# ================================ #

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
