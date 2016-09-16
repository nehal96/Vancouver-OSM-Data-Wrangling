import xml.etree.ElementTree as ET
import pprint

WATERFRONT_OSM = "/Users/nehaludyavar/Downloads/WaterFront-Vancouver.osm"
VANCOUVER_CITY_OSM = "/Users/nehaludyavar/Documents/Udacity Courses/P3 - Wrangle OpenStreetMap Data/" \
                     "Vancouver_City_v2.osm"
VANCOUVER = "/Users/nehaludyavar/Downloads/vancouver_canada.osm"

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

def test(filename):
    tags = count_tags(filename)
    pprint.pprint(tags)


#test(WATERFRONT_OSM)
#print ""
test(VANCOUVER_CITY_OSM)
