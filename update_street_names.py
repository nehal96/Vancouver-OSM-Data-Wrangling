import xml.etree.ElementTree as ET
from collections import defaultdict
from auditing_street_names import audit
import re
import pprint

VANCOUVER_CITY_OSM = "/Users/nehaludyavar/Downloads/Vancouver_City_v2.osm"
street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)

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

def shape_update_name(name, mapping):
    m = street_type_re.search(name)
    unlisted = {}
    if m:
        street_type = m.group()
        if street_type in mapping.keys():
            better_name = re.sub(street_type, mapping[street_type], name)
        else:
            unlisted[street_type] = name
    return better_name


#update_name(VANCOUVER_CITY_OSM, mapping)
