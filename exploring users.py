import xml.etree.ElementTree as ET
import pprint
import re

WATERFRONT_OSM = "/Users/nehaludyavar/Downloads/WaterFront-Vancouver.osm"
DOWNTOWN = "/Users/nehaludyavar/Downloads/Downtown-Vancouver.osm"
VANCOUVER_CITY_OSM = "/Users/nehaludyavar/Downloads/Vancouver_City_v2.osm"
VANCOUVER_CITY_SAMPLE = "/Users/nehaludyavar/Downloads/Vancouver_City_Sample.osm"
VANCOUVER = "/Users/nehaludyavar/Downloads/vancouver_canada.osm"

def get_user(element):

    return element.get("user")

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


def test(filename):

    users = process_map(filename)
    pprint.pprint(users)
    pprint.pprint(len(users))


#test(WATERFRONT_OSM)
#print ""
#test(VANCOUVER_CITY_SAMPLE)
#print ""
test(VANCOUVER_CITY_OSM)
