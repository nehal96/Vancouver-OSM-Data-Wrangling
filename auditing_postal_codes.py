import xml.etree.cElementTree as ET
from collections import defaultdict
import regex as re
import pprint

from auditing_street_names import VANCOUVER_CITY_SAMPLE, VANCOUVER_CITY_OSM
# imports my OSM files

postal_code_re = re.compile(r'[A-Z^DFIOQUWZ]\d[A-Z^DFIOQU]\s\d[A-Z^DFIOQU]\d$')
""" Regex that makes sure that postal codes are in the Canadian format. That is,
    alternating uppercase letters and numbers, grouped by 3s, with a space
    after the first group (for example, V6T 1Z4).

    Canadian postal code regulations state the following characters cannot be
    used: D, F, I, O, Q, U, except for the first character (letter), where X and
    Z cannot be used as well.
"""


def is_postal_code(element):
    """ Checks if the key in an element tag is for a postcode. Returns True if
    it is.
    """
    return (element.get('k') == 'addr:postcode')


def audit_postal_code(correct_PCs, incorrect_PCs, postal_code):
    """ Checks if the regex can find a match in a particular postcode. If yes
        (True), converts the match object into a string, and appends that into
        the list containing correct postcodes. If not (False), appends
        the postcode to a list containing incorrect postcodes.
    """
    m = postal_code_re.match(postal_code)
    if m:
        correct_PC = m.group()              # PC stands for Postal Code
        correct_PCs.append(correct_PC)
    else:
        incorrect_PCs.append(postal_code)


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

def print_audit(osmfile):
    """ Prints the result of the 'audit' function, and the length of the
    returned list
    """
    PC_audit = audit(osmfile)
    pprint.pprint(PC_audit)
    pprint.pprint(len(PC_audit))
