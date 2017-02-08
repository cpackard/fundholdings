import csv
import xml
import xml.etree.ElementTree as ET
from datetime import datetime

import logging
logger = logging.getLogger(__name__)

from holdings.dto import base

################################### Class Definitions #######################################

class Report13FHR(base.SECForm):

    def __init__(self, cik, accepted_date, submission_type, holdings=None):
        if holdings is None:
            holdings = []

        self.holdings = holdings
        super().__init__(cik, accepted_date, submission_type)

    def __repr__(self):
        return '{cik}::{date}'.format(
            cik=self.cik,
            date=self.accepted_date)

    def generate_report(self):
        """
        Given the current reports' list of holdings, generate a tab-delimited
        report of the holdings.
        """
        reportname = (self.cik + '_'
                      + self.accepted_date.isoformat().replace('-', '_')
                      + '.txt')

        with open('reports/' + reportname, 'w') as csvfile:
            fields = ['entity', 'shares', 'value']
            writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter='\t')

            writer.writeheader()
            for holding in self.holdings:
                writer.writerow({'entity': holding.entity,
                                 'shares': holding.shares,
                                 'value':  holding.value})

        return [reportname]

################################ Helper Methods ##########################################

def _short_tag(tag):
    """Helper method to remove any namespaces from the XML tag"""
    return tag[tag.rfind('}')+1:len(tag)]

def _tags_and_vals(root):
    """
    Helper method to recursively search through an XML element,
    returning a dict of tag name --> tag text
    """
    result = {}

    for child in root:
        tag = _short_tag(child.tag)

        if list(child):
            result[tag] = _tags_and_vals(child)
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
        tag = _short_tag(child.tag)

        if tag == 'infoTable':
            result.append(_tags_and_vals(child))

    return result

def get_13f_xml(holdings_statement):
    """
    Given the complete submission text for a 13F-HR filing,
    parse and return only the XML containing the information table.
    """
    holdings_xml    = []
    accepted_date   = ''
    submission_type = ''
    info_started    = False

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
        elif 'CONFORMED SUBMISSION TYPE' in line:
            submission_type = line[line.find(':')+1:].strip()
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
                logger.warn('get_13f_xml expected a well-formatted date')
                raise

    return accepted_date, submission_type, ''.join(holdings_xml)

def get_13f_holdings(cik, accepted_date, submission_type, holdings_xml):
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
    holdings   = [base.Holding(h['nameOfIssuer'],
                               h['shrsOrPrnAmt']['sshPrnamt'],
                               h['value'])
                  for h
                  in infotables]

    return Report13FHR(cik, accepted_date, submission_type, holdings)


