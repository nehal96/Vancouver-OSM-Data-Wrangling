import xml.etree.ElementTree as ET
import pprint
import re

VANCOUVER_CITY_OSM = "/Users/nehaludyavar/Downloads/Vancouver_City_v2.osm"
VANCOUVER_CITY_SAMPLE = "/Users/nehaludyavar/Downloads/Vancouver_City_Sample.osm"


def get_user(element):
    """ Returns the user value in the element"""
    return element.get("user")


def process_map(filename):
    """ Iteratively parses through the OSM XML file, and if the element is a
        node, way, or relation, calls the 'get_user' function. Then, if that
        particular user is not in the array of users, it adds the user. Finally,
        the array is assigned to a users set, and that set is returned.
    """
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
    """ A short test that checks the function on a particular file """
    users = process_map(filename)
    pprint.pprint(users)
    pprint.pprint(len(users))
