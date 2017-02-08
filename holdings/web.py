from bs4 import BeautifulSoup
import requests

class TickerNotFoundException(Exception):
    pass

class HoldingInfoNotFoundException(Exception):
    pass

def get_archive_links(ticker, *forms):
    """
    Given a ticker or CIK number and a list of forms to search for,
    return a list of Archive links containing information for those filings.
    Forms can be any holding filing to look for, i.e. N-Q, 13F-HR, etc.
    """
    domain   = 'https://www.sec.gov'
    url      = ('https://www.sec.gov/cgi-bin/browse-edgar?CIK='
                + ticker + '&owner =exclude&action =getcompany')
    response = requests.get(url)
    content  = response.content
    soup     = BeautifulSoup(content, 'html.parser')

    submission_type = ''
    results         = []

    if 'No matching Ticker Symbol' in soup.get_text():
        raise TickerNotFoundException(ticker)

    for tr in soup.find_all('tr'):
        tds = tr.find_all('td')
        for td in tds:
            if td.get_text() in forms:
                submission_type = td.get_text()
                archive = [href.get('href')
                           for href
                           in tr.find_all('a')
                           if href.get('href').startswith('/Archive')]
                if archive:
                    results.append(domain + archive[0])

    return submission_type, results

def get_holding_info(*archives):
    """
    Given a list of archive links, find and return the complete submission
    text file of each filing.
    """
    domain  = 'https://www.sec.gov'
    results = []

    for archive in archives:
        response     = requests.get(archive)
        content      = response.content
        soup         = BeautifulSoup(content, 'html.parser')
        holding_info = ''

        for tr in soup.find_all('tr'):
            if 'Complete submission text file' in tr.get_text():
                holding_info = domain + tr.find('a').get('href')

        if holding_info == '':
            raise HoldingInfoNotFoundException(archives)
        else:
            r = requests.get(holding_info) # TODO catch exception here?
            results.append(r.text)

    return results
