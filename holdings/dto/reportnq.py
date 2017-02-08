import csv
from bs4 import BeautifulSoup
from datetime import datetime

from holdings.dto import base

################################## Class Definitions #########################################

class ClassContract():

    def __init__(self, ID, name, ticker):
        self.ID     = ID
        self.name   = name
        self.ticker = ticker

    def __repr__(self):
        return '{id_}::{ticker}'.format(
            id_=self.ID,
            ticker=self.ticker)


class FundSeries():

    def __init__(self, ID, ownerCIK, name, contracts=None, holdings=None):
        self.ID       = ID
        self.ownerCIK = ownerCIK
        self.name     = name
        if contracts is None:
            contracts = []
        if holdings is None:
            holdings = []
        self.contracts = contracts
        self.holdings  = holdings

    def __repr__(self):
        return '{id_}::{cik}'.format(
            id_=self.ID,
            cik=self.ownerCIK)


class ReportNQ(base.SECForm):

    def __init__(self, cik, accepted_date, submission_type, series=None):
        self.cik           = cik
        self.accepted_date = accepted_date
        if series is None:
            series = []
        self.series = series
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
        reportnames = []

        for series in self.series:
            reportname = (self.cik + '_'
                          + series.ID + '_'
                          + self.accepted_date.isoformat().replace('-', '_')
                          + '.txt')
            reportnames.append(reportname)

            with open('reports/' + reportname, 'w') as csvfile:
                fields = ['entity', 'shares', 'value']
                writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter='\t')

                writer.writeheader()
                for holding in series.holdings:
                    writer.writerow({'entity': holding.entity,
                                    'shares': holding.shares,
                                    'value':  holding.value})

        return reportnames


class InvalidContractTextException(Exception):
    pass

class InvalidSeriesTextException(Exception):
    pass

################################ Helper Methods ############################################
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

    return ClassContract(ID, name, ticker)


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

    return FundSeries(ID, ownerCIK, name)

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

                holdings.append(base.Holding(name, shares, value))

    return holdings

def get_nq_report(complete_text):
    """
    Given the complete submission text for an N-Q filing, parse the document
    and return its respective ReportNQ DTO object.
    """
    series_flag     = False
    html_flag       = False
    series_text     = []
    series_list     = []
    html_text       = []
    accepted_date   = ''
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

    report = ReportNQ(all_series[0].ownerCIK,
                      accepted_date,
                      submission_type,
                      all_series)

    return report
