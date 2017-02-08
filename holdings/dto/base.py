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

    def __init__(self, cik, accepted_date, submission_type):
        self.cik = cik
        self.accepted_date = accepted_date
        self.submission_type = submission_type

    def generate_report(self):
        raise NotImplementedError('Please implement this method.')
