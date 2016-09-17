import xml.etree.cElementTree as ET
from collections import defaultdict
import regex as re
import pprint

VANCOUVER_CITY_OSM = "/Users/nehaludyavar/Downloads/Vancouver_City_v2.osm"
VANCOUVER_CITY_SAMPLE = "/Users/nehaludyavar/Downloads/Vancouver_City_Sample.osm"
""" The Vancouver OSM file and a created sample """

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
""" Regex to get the last word in a string of words. This is where
    the street type (eg. Street) usually is.
"""
expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square",
            "Lane", "Road", "Trail", "Parkway", "Commons", "Alley", "Broadway",
            "Crescent", "Drive", "Esplanade", "Terminal", "Walk", "Way",
            "Venue", "Kingsway", "Mews", "S."]
""" List of expected values i.e. street names that are correct """


def audit_street_type(street_types, street_name):
    """ Takes in a empty dictionary of street type: street name value pairs and
        the street name and uses the regex to isolate the street type. If there
        is a match, the match object is converted to a string and if the street
        type is not in the expected list, adds the street type and street name
        to the dictionary.
    """
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type] = street_name


def is_street_name(element):
    """ Checks if the key in an element tag is for a street. Returns True if
    it is.
    """
    return (element.get('k') == "addr:street")


def audit(osmfile):
    """ Iteratively parses through each element in an XML file (in this case
        for OSM), and first checks if the element is a node or way element. If
        True, then the function with iterate through each tag in the node or way
        element, and run the 'is_street_name' function on it. If True, the
        function will run the 'audit_street_type' function on it.

        Returns:
            dictionary: street type:street name value pairs.
    """
    street_types = defaultdict(set)
    for event, element in ET.iterparse(osmfile, events=("start", )):
        if element.tag == "way" or element.tag == "node":
            for tag in element.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types

def print_audit(osmfile):
    """ Prints the result of the 'audit' function, and the length of the
    returned dictionary.
    """
    pprint.pprint(dict(audit(osmfile)))
    print len(audit(osmfile))
