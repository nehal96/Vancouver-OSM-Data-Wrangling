import xml.etree.ElementTree as ET
from collections import defaultdict
from auditing_street_names import audit
import re
import pprint

VANCOUVER_CITY_OSM = "/Users/nehaludyavar/Downloads/Vancouver_City_v2.osm"

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

def update_name(osmfile, mapping):
    """ Iterates through the audited dictionary, and it the street type is in
        the keys of the mapping dictionary, uses regex sub method to substitute
        the incorrect street type for the correct street type into the street
        name. Once complete, prints both the incorrect and correct street names.
        If the street type is not in the keys of the mapping dictionary, it
        inserts the street type:street name pair into the unlisted dictionary,
        and finally in the end prints it.
    """
    unlisted = {}
    street_types = audit(osmfile)
    for street_type, name in street_types.iteritems():
        if street_type in mapping.keys():
            better_name = re.sub(street_type, mapping[street_type], name)
            print name, "=>", better_name
        else:
            unlisted[street_type] = name
    pprint.pprint(dict(unlisted))

def shape_update_name(name, mapping):
    """ Performs a similar function to the update_name function, but instead of
        printing out the better name it returns it (so that it can be used in
        the shape_element function)
    """
    m = street_type_re.search(name)
    unlisted = {}
    if m:
        street_type = m.group()
        if street_type in mapping.keys():
            better_name = re.sub(street_type, mapping[street_type], name)
        else:
            unlisted[street_type] = name
    return better_name
