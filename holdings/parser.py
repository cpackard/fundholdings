import xml
import xml.etree.ElementTree as ET
from datetime import datetime

from holdings import holdingsDTO

def short_tag(tag):
    """Helper method to remove any namespaces from the XML tag"""
    return tag[tag.rfind('}')+1:len(tag)]

def tags_and_vals(root):
    """
    Helper method to recursively search through an XML element,
    returning a dict of tag name --> tag text
    """
    result = {}

    for child in root:
        tag = short_tag(child.tag)

        if list(child):
            result[tag] = tags_and_vals(child)
        else:
            result[tag] = child.text

    return result

def get_infotables(root):
    """
    Given the root XML element informationTable, search through all infoTable
    elements and return a list of dicts mapping tag name --> tag text
    """
    result = []

    for child in root:
        tag = short_tag(child.tag)

        if tag == 'infoTable':
            result.append(tags_and_vals(child))

    return result

def get_13f_xml(holdings_statement):
    """
    Given the complete submission text for a 13F-HR filing,
    parse and return only the XML containing the information table.
    """
    holdings_xml = []
    accepted_date = ''
    info_started = False

    for line in holdings_statement.split('\n'):
        # Parse only the lines between the <informationTable> tags
        if info_started:
            if '</XML>' in line:
                break
            else:
                holdings_xml.append(line)
        elif 'informationTable' in line:
            info_started = True
            holdings_xml.append(line)
        elif 'ACCEPTANCE-DATETIME' in line:
            full_date      = line[line.rfind('>')+1:len(line)]
            year           = full_date[:4]
            month          = full_date[4:6]
            day            = full_date[6:8]
            formatted_date = year + ' ' + month + ' ' + day
            try:
                accepted_date  = datetime.strptime(formatted_date,
                                                   '%Y %m %d').date()
            except ValueError:
                # TODO put actual logging here
                print('get_13f_xml expected a well-formatted date')
                raise

    return accepted_date, ''.join(holdings_xml)

def get_13f_holdings(cik, accepted_date, holdings_xml):
    """
    Given a well-formed xml containing the holding data from a 13F-HR filing,
    parse the xml and return a 13FHR object containing a list of holdings DTO objects.
    """
    try:
        tree = ET.fromstring(holdings_xml)
    except xml.etree.ElementTree.ParseError:
        # TODO Change this to actual logging
        print('get_13f_holdings expected a well-formed xml but ParseError occured')
        raise

    infotables = get_infotables(tree)

    holdings = [holdingsDTO.Holding(h['nameOfIssuer'],
                                h['shrsOrPrnAmt']['sshPrnamt'],
                                h['value'])
                for h
                in infotables]

    return holdingsDTO.Report13FHR(holdings, cik, accepted_date)
