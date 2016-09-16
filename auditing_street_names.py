import xml.etree.cElementTree as ET
from collections import defaultdict
import regex as re
import pprint

VANCOUVER_CITY_OSM = "/Users/nehaludyavar/Downloads/Vancouver_City_v2.osm"
VANCOUVER_CITY_SAMPLE = "/Users/nehaludyavar/Downloads/Vancouver_City_Sample.osm"

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square",
            "Lane", "Road", "Trail", "Parkway", "Commons", "Alley", "Broadway",
            "Crescent", "Drive", "Esplanade", "Terminal", "Walk", "Way",
            "Venue", "Kingsway", "Mews", "S."]


def audit_street_type(street_types, street_name):
    m = street_type_re.search(street_name)
    if m:
        street_type = m.group()
        if street_type not in expected:
            street_types[street_type] = street_name


def is_street_name(element):
    if (element.get('k') == "addr:street"):
        return element.get('k')


def audit(osmfile):
    street_types = defaultdict(set)
    for event, element in ET.iterparse(osmfile, events=("start", )):
        if element.tag == "way" or element.tag == "node":
            for tag in element.iter("tag"):
                if is_street_name(tag):
                    audit_street_type(street_types, tag.attrib['v'])
    return street_types

def print_audit(osmfile):
    pprint.pprint(dict(audit(osmfile)))
    print len(audit(osmfile))



#print_audit(VANCOUVER_CITY_OSM)
