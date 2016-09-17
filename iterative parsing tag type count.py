import xml.etree.ElementTree as ET
import pprint


VANCOUVER_CITY_OSM = "/Users/nehaludyavar/Documents/Udacity Courses/P3 - Wrangle OpenStreetMap Data/" \
                     "Vancouver_City_v2.osm"
VANCOUVER = "/Users/nehaludyavar/Downloads/vancouver_canada.osm"

def count_tags(filename):
    """ Iteratively parses through OSM XML file, and if the element tag is not
        in the keys of the initiated tags dictionary, it adds the tag to the
        dictionary and initiates the count at 1. If it is already in the tags
        dictionary, it adds 1 to the count.

        Returns:
            dictionary: element tags
    """
    tags = {}
    for event, elem in ET.iterparse(filename, events=("start", )):
        if elem.tag in tags.keys():
            tag_field = "%s" % elem.tag
            tags[tag_field] += 1
        else:
            tag_field = "%s" % elem.tag
            tags[tag_field] = 1

    return tags

def test(filename):
    """ A quick test of the count-tag function on an OSM XML file """
    tags = count_tags(filename)
    pprint.pprint(tags)
