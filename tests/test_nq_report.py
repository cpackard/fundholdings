import unittest
import datetime
import xml

from holdings.dto import reportnq

class TestGetSeriesAndContracts(unittest.TestCase):

    def test_raises_exception_for_invalid_contract_text(self):
        text = ['<CLASS-CONTRACT>', '<CLASS-CONTRACT-ID>C000007825', '<CLASS-CT-NAME>Institutional Shares', '<CLASS-CONTRACT-TICKER-SYMBOL>VINIX', '</CLASS-CONTRACT>']
        self.assertRaises(reportnq.InvalidContractTextException,
                          reportnq.parse_contract, text)

    def test_converts_valid_contract_text_to_contract_object(self):
        text = ['<CLASS-CONTRACT>', '<CLASS-CONTRACT-ID>C000007825', '<CLASS-CONTRACT-NAME>Institutional Shares', '<CLASS-CONTRACT-TICKER-SYMBOL>VINIX', '</CLASS-CONTRACT>']
        contract = reportnq.parse_contract(text)

        self.assertEqual(contract.ID, 'C000007825')
        self.assertEqual(contract.name, 'Institutional Shares')
        self.assertEqual(contract.ticker, 'VINIX')

    def test_raises_exception_for_invalid_series_text(self):
        text = ['<SERIES>und</SERIES>']
        self.assertRaises(reportnq.InvalidSeriesTextException,
                          reportnq.parse_series, text)

    def test_converts_valid_series_text_to_series_object(self):
        text   = ['<OWNER-CIK>0000862084', '<SERIES-ID>S000002853', '<SERIES-NAME>Vanguard Institutional Index Fund']
        series = reportnq.parse_series(text)

        self.assertEqual(series.ID, 'S000002853')
        self.assertEqual(series.ownerCIK, '0000862084')
        self.assertEqual(series.name, 'Vanguard Institutional Index Fund')

    def test_extracts_valid_series_and_contracts_from_text(self):
        text = ['<SERIES>', '<OWNER-CIK>0000862084', '<SERIES-ID>S000002853', '<SERIES-NAME>Vanguard Institutional Index Fund', '<CLASS-CONTRACT>', '<CLASS-CONTRACT-ID>C000007825', '<CLASS-CONTRACT-NAME>Institutional Shares', '<CLASS-CONTRACT-TICKER-SYMBOL>VINIX', '</CLASS-CONTRACT>', '<CLASS-CONTRACT>', '<CLASS-CONTRACT-ID>C000007826', '<CLASS-CONTRACT-NAME>Institutional Plus Shares', '<CLASS-CONTRACT-TICKER-SYMBOL>VIIIX', '</CLASS-CONTRACT>', '</SERIES>']
        series = reportnq.parse_series_and_contracts(text)

        self.assertEqual(series.ID, 'S000002853')
        self.assertEqual(series.ownerCIK, '0000862084')
        self.assertEqual(series.name, 'Vanguard Institutional Index Fund')

        self.assertEqual(len(series.contracts), 2)


class TestGetSeriesHoldings(unittest.TestCase):

    def test_parse_nq_report_html(self):
        with open('/home/chpack/Documents/python/quovo_challenge/christian_packard/fund_holdings/resources/vanguard_html.html', 'r') as vanguard_html:
            html_text = vanguard_html.read()

        holdings = reportnq.parse_nq_report_html(html_text)
        self.assertGreater(len(holdings), 1)

        holding = holdings[0]
        self.assertEqual(holding.entity, '* Amazon.com Inc.')
        self.assertEqual(holding.shares, '4,365,551')
        self.assertEqual(holding.value, '3,655,319')

    def test_get_nq_report(self):
        with open('/home/chpack/Documents/python/quovo_challenge/christian_packard/fund_holdings/resources/vanguard_complete_text_submission.txt', 'r') as vanguard_text:
            complete_text = vanguard_text.read()

        nq_report = reportnq.get_nq_report(complete_text)

        self.assertEqual(nq_report.cik, '0000862084')
        self.assertEqual(nq_report.accepted_date.isoformat(),
                         '2016-11-30')
        self.assertNotEqual([], nq_report.series)

        holding = nq_report.series[0].holdings[0]
        self.assertEqual(holding.entity, '* Amazon.com Inc.')
        self.assertEqual(holding.shares, '4,365,551')
        self.assertEqual(holding.value, '3,655,319')


if __name__ == '__main__':
    unittest.main()
