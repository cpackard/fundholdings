import sys
import logging

from holdings import web

from holdings.dto import report13fhr
from holdings.dto import reportnq

logger    = logging.getLogger()
handler   = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')

handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.WARN)

def generate_13fhr_report(cik, forms, archives):
    # The parser looks for the most recent holdings
    holdings_statement = web.get_holding_info(archives[0])
    accepted_date, submission_type, holdings_xml = report13fhr.get_13f_xml(holdings_statement[0])

    current_13fhr = report13fhr.get_13f_holdings(cik, accepted_date,
                                            submission_type, holdings_xml)
    reportnames   = current_13fhr.generate_report()

    return reportnames

def generate_nq_report(cik, forms, archives):
    holdings_statement = web.get_holding_info(archives[0])
    current_nq         = reportnq.get_nq_report(holdings_statement[0])
    reportnames        = current_nq.generate_report()

    return reportnames

def generate_report(cik, forms):
    submission_type, archives = web.get_archive_links(cik, *forms)

    if submission_type == '13F-HR' or submission_type == '13F-HR/A':
        logger.info('Found 13F-HR filing, proceeding to generate report...')
        return generate_13fhr_report(cik, forms, archives)
    elif submission_type == 'N-Q':
        logger.info('Found N-Q filing, proceeding to generate report...')
        return generate_nq_report(cik, forms, archives)
    else:
        logger.error('Don\'t know how to parse form' + submission_type)
        print('Don\'t know how to parse form' + submission_type)
        sys.exit(1)

def main():
    """Main entry point for the application"""
    if len(sys.argv) < 2:
        print('Usage: python -m holdings.main ticker_or_cik')
        sys.exit(1)

    cik   = sys.argv[1]
    forms = ['13F-HR', '13F-HR/A', 'N-Q']

    try:
        logger.info('Starting to search for report')
        reportnames = generate_report(cik, forms)
    except web.TickerNotFoundException:
        logger.error('No suck ticker ' + cik + ' found in EDGAR')
    except web.HoldingInfoNotFoundException as e:
        logger.error('No submission text found in the following archives:')
        logger.error(str(e))
    except reportnq.InvalidContractTextException as e:
        logger.error('While parsing the contract classes for the fund, '
              + 'the following error occured:')
        logger.error(str(e))
    except reportnq.InvalidSeriesTextException as e:
        logger.error('While parsing the series information for the fund, '
              + 'the following error occured:')
        logger.error(str(e))
    else:
        logger.info('Finished searching for report')
        print('Reports successfully generated and can be found in:')

        for name in reportnames:
            print('reports/' + name)


if __name__ == '__main__':
    main()
