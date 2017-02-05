import sys

from holdings import web
from holdings import parser

def generate_13fhr_report(cik, forms):
    archives = web.get_archive_links(cik, *forms)

    # The parser looks for the most recent holdings
    holdings_statement = web.get_holding_info(archives[0])

    accepted_date, holdings_xml = parser.get_13f_xml(holdings_statement[0])

    current_13fhr = parser.get_13f_holdings(cik, accepted_date,
                                            holdings_xml)

    report_name = current_13fhr.generate_report()


def main():
    """Main entry point for the application"""
    if len(sys.argv) < 2:
        print('Usage: python -m holdings.main ticker_or_cik')
        sys.exit(1)

    cik = sys.argv[1]
    forms = ['13F-HR', '13F-HR/A', 'N-Q']

    generate_13fhr_report(cik, forms)


if __name__ == '__main__':
    # cik = '0001166559'
    main()
