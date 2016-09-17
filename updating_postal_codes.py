import xml.etree.ElementTree as ET
from collections import defaultdict
from auditing_postal_codes import audit
import re
import pprint

VANCOUVER_CITY_OSM = "/Users/nehaludyavar/Downloads/Vancouver_City_v2.osm"

postal_code_re_alt = re.compile(r'[A-Z^DFIOQUWZ]\d[A-Z^DFIOQU]\s?\d[A-Z^DFIOQU]\d$', re.IGNORECASE)
""" Regex that is similar to the auditing_postal_codes regex, but this time the
    space between the groups of three is optional.
"""
postal_code_number_re = re.compile(r'\d\d-?\d-?\d\d?\d?\d?$')
""" Regex that matches with numerical postcodes of different kinds. The options
    include 1234, 12345, 12-345, 123-4567.
"""

problem_PCs = []                            # Empty list for problem postcodes
number_PCs = []                             # Empty list for numerical postcodes


def update_postal_code(osmfile):
    """ If a postcode is in the list returned by the audit function, it first
        removes any whitespace and then makes the string uppercase. Then it uses
        the postal_code_re_alt regex to find a match, and if one is found, it
        groups the match object and returns the string grouped by 3. If there is
        no match, it appends the postcode to the problem_PCs list. Next, it
        iterates through the postcodes in this list, and uses the
        postal_code_number_re regex to splits the list into numerical and
        non-numerical postcode lists for further potenial cleaning.
    """
    incorrect_PCs = audit(osmfile)
    for postcode in incorrect_PCs:
        stripped_upper = postcode.strip().upper()
        m = postal_code_re_alt.match(stripped_upper)
        if m:
            PC = m.group()
            char_list = list(PC)
            post_code = char_list[0] + char_list[1] + char_list[2] + " " + \
                    char_list[3] + char_list[4] + char_list[5]
            return post_code
        else:
            problem_PCs.append(postcode)

    for postcode in problem_PCs:
        n = postal_code_number_re.search(postcode)
        if n:
            number_PC = n.group()
            number_PCs.append(number_PC)
            problem_PCs.remove(number_PC)
        else:
            pass



def shape_update_postal_code(postcode):
    """ Same as update_postal_code function, but takes the postcode instead of
        the XML file as the argument (for the shape_element function).
    """
    stripped_upper = postcode.strip().upper()
    m = postal_code_re_alt.match(stripped_upper)
    if m:
        PC = m.group()
        char_list = list(PC)
        post_code = char_list[0] + char_list[1] + char_list[2] + " " + \
                    char_list[3] + char_list[4] + char_list[5]
        return post_code
    else:
        problem_PCs.append(postcode)

    for postcode in problem_PCs:
        n = postal_code_number_re.search(postcode)
        if n:
            number_PC = n.group()
            number_PCs.append(number_PC)
            problem_PCs.remove(number_PC)
        else:
            pass
