import csv

from holdings.dto import base

class Report13FHR(base.SECForm):

    def __init__(self, cik, accepted_date, submission_type, holdings=None):
        if holdings is None:
            holdings = []

        self.holdings = holdings
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
        reportname = (self.cik + '_'
                      + self.accepted_date.isoformat().replace('-', '_')
                      + '.txt')

        # TODO Find a way to make this path relative
        with open('reports/' + reportname, 'w') as csvfile:
            fields = ['entity', 'shares', 'value']
            writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter='\t')

            writer.writeheader()
            for holding in self.holdings:
                writer.writerow({'entity': holding.entity,
                                 'shares': holding.shares,
                                 'value':  holding.value})

        return [reportname]
