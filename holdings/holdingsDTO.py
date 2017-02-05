import csv

class Holding():

    def __init__(self, entity, shares, value):
        self.entity = entity
        self.shares = shares
        self.value  = value

    def __repr__(self):
        return '{entity}::{shares}/{value}'.format(
            entity=self.entity,
            shares=self.shares,
            value=self.value)

    def __str__(self):
        return '{entity}\t{shares}\t{value}'.format(
            entity=self.entity,
            shares=self.shares,
            value=self.value)


class SECForm():

    def __init__(self, cik, accepted_date):
        self.cik = cik
        self.accepted_date = accepted_date

    def generate_report(self):
        raise NotImplementedError('Please implement this method.')


class Report13FHR(SECForm):

    def __init__(self, holdings, cik, accepted_date):
        if not holdings:
            self.holdings = []
        else:
            self.holdings = holdings

        super().__init__(cik, accepted_date)

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

        return reportname


