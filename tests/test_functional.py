import unittest
import csv

import requests

from holdings import web
from holdings import parser

class Test13FHR(unittest.TestCase):

    def test_valid_13fhr_filing(self):
        ## Mary wants to find out the latest holdings of a fund she's
        ## invested in, the Bill and Melinda Gates Foundation Trust

        ## She searches by the trust's CIK number
        cik = '0001166559'

        # The parser performs the initial search on EDGAR database

        # url = ('https://www.sec.gov/cgi-bin/browse-edgar?CIK='
        #        + cik + '&owner=exclude&action=getcompany')
        forms = ['13F-HR', '13F-HR/A']
        archives = web.get_archive_links(cik, *forms)

        # The parser looks for the most recent holdings
        holdings_statement = web.get_holding_info(archives[0])

        # With the complete submission, the parser cuts down unnecessary info
        accepted_date, holdings_xml = parser.get_13f_xml(holdings_statement[0])

        # With all the holdings statements, the parser converts the xml
        # into a more useable form
        current_13fhr = parser.get_13f_holdings(cik, accepted_date,
                                                holdings_xml)

        # With the holdings extracted, the parser prints them into a neatly
        # formatted tab-separated report for Mary
        report_name = current_13fhr.generate_report()

        ## Mary inspects the report to make sure she has the correct info
        with open('reports/' + report_name, 'r') as report:
            reader = csv.DictReader(report, delimiter='\t')
            for row in reader:
                self.assertIsInstance(int(row['value'].replace(',', '')), int)
                self.assertIsInstance(int(row['shares'].replace(',', '')), int)

        ## Satisfied, she goes back to her other tasks


if __name__ == '__main__':
    unittest.main()

