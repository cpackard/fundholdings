import csv

########### base.py ###########################
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


#################### report13fhr.py ###############################

class Report13FHR(SECForm):

    def __init__(self, cik, accepted_date, holdings=None):
        if holdings is None:
            holdings = []

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

######################## reportnq.py #############################

class ClassContract():

    def __init__(self, ID, name, ticker):
        self.ID = ID
        self.name = name
        self.ticker = ticker

    def __repr__(self):
        return '{id_}::{ticker}'.format(
            id_=self.ID,
            ticker=self.ticker)


class FundSeries():

    def __init__(self, ID, ownerCIK, name, contracts=None, holdings=None):
        self.ID = ID
        self.ownerCIK = ownerCIK
        self.name = name
        if contracts is None:
            contracts = []
        if holdings is None:
            holdings = []
        self.contracts = contracts
        self.holdings = holdings

    def __repr__(self):
        return '{id_}::{cik}'.format(
            id_=self.ID,
            cik=self.ownerCIK)


class ReportNQ(SECForm):

    def __init__(self, cik, accepted_date, series=None):
        self.cik = cik
        self.accepted_date = accepted_date
        if series is None:
            series = []
        self.series = series

    def __repr__(self):
        return '{cik}::{date}'.format(
            cik=self.cik,
            date=self.accepted_date)

    def generate_report(self):
        """
        Given the current reports' list of holdings, generate a tab-delimited
        report of the holdings.
        """
        reportnames = []

        for series in self.series:
            reportname = (self.cik + '_'
                          + series.ID + '_'
                          + self.accepted_date.isoformat().replace('-', '_')
                          + '.txt')
            reportnames.append(reportname)

            # TODO Find a way to make this path relative
            with open('reports/' + reportname, 'w') as csvfile:
                fields = ['entity', 'shares', 'value']
                writer = csv.DictWriter(csvfile, fieldnames=fields, delimiter='\t')

                writer.writeheader()
                for holding in series.holdings:
                    writer.writerow({'entity': holding.entity,
                                    'shares': holding.shares,
                                    'value':  holding.value})

        return reportnames

