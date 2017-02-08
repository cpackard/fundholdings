import unittest
from holdings import web

class TestArchiveLinks(unittest.TestCase):

    def test_doesnt_return_links_for_bad_ticker(self):
        ticker = 'whatever'
        forms  = ['N-Q']
        self.assertRaises(web.TickerNotFoundException,
                          web.get_archive_links, ticker, *forms)

    def test_doesnt_return_links_for_bad_forms(self):
        ticker = 'viiix'
        forms  = ['Q-N']
        self.assertEqual(('', []),
                          web.get_archive_links(ticker, *forms))

    def test_returns_links_for_13fhr(self):
        ticker = '0001166559'
        forms  = ['13F-HR', '13F-HR/A']
        self.assertNotEqual([],
                            web.get_archive_links(ticker, *forms))

    def test_returns_links_for_nq(self):
        ticker = 'viiix'
        forms  = ['N-Q']
        self.assertNotEqual([],
                            web.get_archive_links(ticker, *forms))


class TestGetHoldingInfo(unittest.TestCase):

    def test_raises_exception_for_missing_info(self):
        urls = ['https://www.google.com']
        self.assertRaises(web.HoldingInfoNotFoundException,
                          web.get_holding_info, *urls)

    def test_returns_holdings_info_text(self):
        urls = ['https://www.sec.gov/Archives/edgar/data/1166559/000110465916156931/0001104659-16-156931-index.htm',
                'https://www.sec.gov/Archives/edgar/data/1418814/000141881216000209/0001418812-16-000209-index.htm']

        holding_info = web.get_holding_info(*urls)
        self.assertNotEqual([], holding_info)

        for info in holding_info:
            self.assertTrue(info.startswith('<SEC-DOCUMENT>'),
                            info)


if __name__ == '__main__':
    unittest.main()
