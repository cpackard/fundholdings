import xml
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
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
    submission_type = ''
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
                # TODO put actual logging here
                print('get_13f_xml expected a well-formatted date')
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

    holdings = [holdingsDTO.Holding(h['nameOfIssuer'],
                                h['shrsOrPrnAmt']['sshPrnamt'],
                                h['value'])
                for h
                in infotables]

    return holdingsDTO.Report13FHR(cik, accepted_date, submission_type, holdings)


####################### nq report #####################################

class InvalidContractTextException(Exception):
    pass

class InvalidSeriesTextException(Exception):
    pass

def _chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]

def _get_line_element_value(element, line, current_exception):
    """
    Given an element to search for in a line of text,
    return the element's value if found.
    Otherwise, raise the appropriate exception.
    """
    if element in line:
        return line[line.rfind('>')+1:]
    else:
        raise current_exception('Couldn\'t find ' + element + ' in '
                                           + line)

def parse_contract(text):
    """
    Given a list of text lines of a class contract from an N-Q report,
    convert the text into a contract DTO object.
    """
    if len(text) < 5:
        raise InvalidContractTextException('Too few elements in contract text')

    ID     = _get_line_element_value('<CLASS-CONTRACT-ID>', text[1].strip(),
                                     InvalidContractTextException)
    name   = _get_line_element_value('<CLASS-CONTRACT-NAME>', text[2].strip(),
                                     InvalidContractTextException)
    ticker = _get_line_element_value('<CLASS-CONTRACT-TICKER-SYMBOL>', text[3].strip(),
                                     InvalidContractTextException)

    return holdingsDTO.ClassContract(ID, name, ticker)


def parse_series(text):
    """
    Given a list of text lines of a series from an N-Q report,
    convert the text into a series DTO object.
    """
    if len(text) < 3:
        raise InvalidSeriesTextException('Too few elements in series text')

    ownerCIK = _get_line_element_value('<OWNER-CIK>', text[0].strip(),
                                       InvalidSeriesTextException)
    ID       = _get_line_element_value('<SERIES-ID>', text[1].strip(),
                                       InvalidSeriesTextException)
    name     = _get_line_element_value('<SERIES-NAME>', text[2].strip(),
                                       InvalidSeriesTextException)

    return holdingsDTO.FundSeries(ID, ownerCIK, name)

def parse_series_and_contracts(text):
    """
    Given a list of text lines containing series and contract info from an N-Q
    report, convert the text into their respective series and contract DTO objects.
    """
    series_text   = text[1:4]
    contract_text = text[4:len(text)-1]
    contract_list = _chunks(contract_text, 5)

    series           = parse_series(series_text)
    contracts        = [parse_contract(text) for text in contract_list]
    series.contracts = contracts

    return series


def parse_nq_report_html(html_text):
    """
    Given the html from the complete submission text for an N-Q filing,
    find and return the list of holdings for each series in the fund.
    """
    # TODO expand this for multipe N-Q submission formats
    # This will currently only support reports whose security,
    # shares, and values are in the same rows
    soup     = BeautifulSoup(html_text, 'html.parser')
    rows     = soup.find_all('tr')
    holdings = []

    for row in rows:
        tds = row.find_all('td')

        if (len(tds) == 3):
            try:
                # If the 2nd and 3rd columns are valid numbers, it's probably
                # a holding 
                int(tds[1].get_text().replace(',', ''))
                int(tds[2].get_text().replace(',', ''))
            except ValueError:
                pass
            else:
                name   = tds[0].get_text()
                shares = tds[1].get_text()
                value  = tds[2].get_text()

                holdings.append(holdingsDTO.Holding(name, shares, value))

    return holdings


def get_nq_report(complete_text):
    """
    Given the complete submission text for an N-Q filing, parse the document
    and return its respective ReportNQ DTO object.
    """
    series_flag = False
    html_flag   = False
    series_text = []
    series_list = []
    html_text   = []
    accepted_date = ''
    submission_type = ''

    for line in complete_text.split('\n'):
        if 'ACCEPTANCE-DATETIME' in line:
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
        elif 'CONFORMED SUBMISSION TYPE' in line:
            submission_type = line[line.find(':')+1:].strip()
        ## Parse all series text and add to the series list
        elif '<SERIES>' in line:
            series_text.append(line)
            series_flag = True
        elif series_flag and '</SERIES>' in line:
            series_text.append(line)
            series_list.append(series_text)
            series_text = []
            series_flag = False
        elif series_flag:
            series_text.append(line)
        ## Parse the actual HTML submission
        elif '<HTML>' in line:
            html_text.append(line)
            html_flag = True
        elif html_flag and '</HTML>' in line:
            html_text.append(line)
            html_flag = False
        elif html_flag:
            html_text.append(line)

    all_series = [parse_series_and_contracts(text) for text in series_list]
    holdings   = parse_nq_report_html(''.join(html_text))

    for series in all_series:
        # TODO expand this to differentiate between different series
        series.holdings = holdings

    report = holdingsDTO.ReportNQ(all_series[0].ownerCIK,
                                  accepted_date,
                                  submission_type,
                                  all_series)

    return report
