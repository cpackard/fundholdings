import sys

from holdings import web

from holdings.dto import report13fhr
from holdings.dto import reportnq

def generate_13fhr_report(cik, forms, archives):
    # The parser looks for the most recent holdings
    holdings_statement = web.get_holding_info(archives[0])

    accepted_date, submission_type, holdings_xml = report13fhr.get_13f_xml(holdings_statement[0])

    current_13fhr = report13fhr.get_13f_holdings(cik, accepted_date,
                                            submission_type, holdings_xml)

    reportnames = current_13fhr.generate_report()

    return reportnames

def generate_nq_report(cik, forms, archives):
    holdings_statement = web.get_holding_info(archives[0])
    current_nq = reportnq.get_nq_report(holdings_statement[0])
    reportnames = current_nq.generate_report()

    return reportnames

def generate_report(cik, forms):
    submission_type, archives = web.get_archive_links(cik, *forms)

    if submission_type == '13F-HR' or submission_type == '13F-HR/A':
        return generate_13fhr_report(cik, forms, archives)
    elif submission_type == 'N-Q':
        return generate_nq_report(cik, forms, archives)
    else:
        # TODO add logging here
        print('Don\'t know how to parse form' + submission_type)
        return ''

def main():
    """Main entry point for the application"""
    if len(sys.argv) < 2:
        print('Usage: python -m holdings.main ticker_or_cik')
        sys.exit(1)

    cik = sys.argv[1]
    forms = ['13F-HR', '13F-HR/A', 'N-Q']

    try:
        reportnames = generate_report(cik, forms)
    except web.TickerNotFoundException:
        print('No suck ticker ' + cik + ' found in EDGAR')
    except web.HoldingInfoNotFoundException as e:
        print('No submission text found in the following archives:')
        print(str(e))
    except parser.InvalidContractTextException as e:
        print('While parsing the contract classes for the fund, '
              + 'the following error occured:')
        print(str(e))
    except parser.InvalidSeriesTextException as e:
        print('While parsing the series information for the fund, '
              + 'the following error occured:')
        print(str(e))
    else:
        print('Reports successfully generated and can be found in:')

        for name in reportnames:
            print('reports/' + name)


if __name__ == '__main__':
    main()
