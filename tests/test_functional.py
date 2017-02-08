import unittest
import csv

import requests

from holdings import web
from holdings import main

from holdings.dto import report13fhr
from holdings.dto import reportnq

class Test13FHRReport(unittest.TestCase):

    def test_valid_13fhr_filing(self):
        ## Mary wants to find out the latest holdings of a fund she's
        ## invested in, the Bill and Melinda Gates Foundation Trust

        ## She searches by the trust's CIK number
        cik = '0001166559'

        # The parser performs the initial search on EDGAR database
        forms = ['13F-HR', '13F-HR/A']
        submission_type, archives = web.get_archive_links(cik, *forms)

        # The parser looks for the most recent holdings
        holdings_statement = web.get_holding_info(archives[0])

        # With the complete submission, the parser cuts down unnecessary info
        accepted_date, submission_type, holdings_xml = report13fhr.get_13f_xml(holdings_statement[0])

        # With all the holdings statements, the parser converts the xml
        # into a more useable form
        current_13fhr = report13fhr.get_13f_holdings(cik, accepted_date,
                                                submission_type, holdings_xml)

        self.assertEqual(current_13fhr.cik, '0001166559')
        self.assertEqual(current_13fhr.submission_type, '13F-HR')

        # With the holdings extracted, the parser prints them into a neatly
        # formatted tab-separated report for Mary
        reportnames = current_13fhr.generate_report()

        ## Mary inspects the report to make sure she has the correct info
        with open('reports/' + reportnames[0], 'r') as report:
            reader = csv.DictReader(report, delimiter='\t')
            for row in reader:
                self.assertIsInstance(int(row['value'].replace(',', '')), int)
                self.assertIsInstance(int(row['shares'].replace(',', '')), int)

        ## Satisfied, she goes back to her other tasks

    def test_valid_13fhr_filing_with_namespace_in_xml(self):
        ## Mary comes back and wants to find the latest holdings on another
        ## fund she's interested in.

        ## She searches the CIK number and forms she's interested in
        cik = '0001418814'
        forms = ['13F-HR', '13F-HR/A']
        reportnames = main.generate_report(cik, forms)

        ## Mary inspects the report to make sure she has the correct info
        with open('reports/' + reportnames[0], 'r') as report:
            reader = csv.DictReader(report, delimiter='\t')
            for row in reader:
                self.assertIsInstance(int(row['value'].replace(',', '')), int)
                self.assertIsInstance(int(row['shares'].replace(',', '')), int)

        ## Satisfied, she goes back to her other tasks


class TestNQReport(unittest.TestCase):

    def test_valid_nq_filing_with_text_report(self):
        ## Jim wants to find out the latest holdings of a fund he's
        ## invested in, the Vanguard Institutional Index Funds

        ## He searches by the trust's ticker
        cik = 'viiix'

        # The parser performs the initial search on EDGAR database
        forms = ['N-Q']
        submission_type, archives = web.get_archive_links(cik, *forms)

        # The parser looks for the most recent holdings
        holdings_statement = web.get_holding_info(archives[0])

        # With the complete submission, the parser extracts the accepted_date,
        # series / contract information, and parses the HTML to read the holdings
        # into a more useable form
        current_nq = reportnq.get_nq_report(holdings_statement[0])

        self.assertEqual(current_nq.cik, '0000862084')
        self.assertEqual(current_nq.submission_type, 'N-Q')

        # With the holdings extracted, the parser prints them into neatly
        # formatted tab-separated reports for Mim
        reportnames = current_nq.generate_report()

        ## Jim inspects the reports to make sure he has the correct info
        for reportname in reportnames:
            with open('reports/' + reportname, 'r') as report:
                reader = csv.DictReader(report, delimiter='\t')
                for row in reader:
                    self.assertIsInstance(int(row['value'].replace(',', '')), int)
                    self.assertIsInstance(int(row['shares'].replace(',', '')), int)

        ## Satisfied, he goes back to his other tasks


if __name__ == '__main__':
    unittest.main()

