import unittest
import datetime
import xml

from holdings.dto import report13fhr

class TestGet13FXML(unittest.TestCase):

    def test_returns_empty_string_for_other_xml(self):
        text = '<DOCUMENT>\n<TYPE>13F-HR\n<SEQUENCE>1\n<FILENAME>primary_doc.xml\n<TEXT>\n<XML>\n<?xml version="1.0" encoding="UTF-8"?>\n<edgarSubmission xsi:schemaLocation="http://www.sec.gov/edgar/thirteenffiler eis_13F_Filer.xsd" xmlns="http://www.sec.gov/edgar/thirteenffiler" xmlns:ns1="http://www.sec.gov/edgar/common" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">\n  <headerData>\n    <submissionType>13F-HR</submissionType>\n    <filerInfo>\n      <liveTestFlag>LIVE</liveTestFlag>\n      <filer>\n        <credentials>\n          <cik>0001166559</cik>\n          <ccc>XXXXXXXX</ccc>\n        </credentials>\n      </filer>\n      <periodOfReport>09-30-2016</periodOfReport>\n    </filerInfo>\n  </headerData>\n  <formData>\n    <coverPage>\n      <reportCalendarOrQuarter>09-30-2016</reportCalendarOrQuarter>\n      <isAmendment>false</isAmendment>\n      <filingManager>\n        <name>Bill &amp; Melinda Gates Foundation Trust</name>\n        <address>\n          <ns1:street1>2365 Carillon Point</ns1:street1>\n          <ns1:city>Kirkland</ns1:city>\n          <ns1:stateOrCountry>WA</ns1:stateOrCountry>\n          <ns1:zipCode>98033</ns1:zipCode>\n        </address>\n      </filingManager>\n      <reportType>13F HOLDINGS REPORT</reportType>\n      <form13FFileNumber>028-10098</form13FFileNumber>\n      <provideInfoForInstruction5>N</provideInfoForInstruction5>\n    </coverPage>\n    <signatureBlock>\n      <name>Michael Larson</name>\n      <title>Authorized Agent</title>\n      <phone>425-889-7900</phone>\n      <signature>/s/ Michael Larson</signature>\n      <city>Kirkland</city>\n      <stateOrCountry>WA</stateOrCountry>\n      <signatureDate>11-14-2016</signatureDate>\n    </signatureBlock>\n    <summaryPage>\n      <otherIncludedManagersCount>0</otherIncludedManagersCount>\n      <tableEntryTotal>18</tableEntryTotal>\n      <tableValueTotal>18452426</tableValueTotal>\n      <isConfidentialOmitted>false</isConfidentialOmitted>\n    </summaryPage>\n  </formData>\n</edgarSubmission>\n</XML>\n</TEXT>\n</DOCUMENT>'
        accepted_date, submission_type, result = report13fhr.get_13f_xml(text)
        self.assertEqual('', result)

    def test_parses_valid_infotable_xml(self):
        # TODO Make this accessible without hard-coded path

        with open('/home/chpack/Documents/python/quovo_challenge/christian_packard/fund_holdings/resources/gates_fund_complete_text_submission.txt', 'r') as text_submission:
            holdings_statement = text_submission.read()

        try:
            accepted_date, submission_type, holdings_xml = report13fhr.get_13f_xml(holdings_statement)
            self.assertTrue('informationTable' in holdings_xml)
            self.assertTrue('infoTable' in holdings_xml)

            xml.etree.ElementTree.fromstring(holdings_xml)
        except xml.etree.ElementTree.ParseError:
            self.fail('The text in holdings_statement raised ParseError unexpectedly')


class TestGet13FHoldings(unittest.TestCase):

    def test_short_tag(self):
        tag = '{http://www.sec.gov/edgar/document/thirteenf/informationtable}infoTable'
        self.assertEqual('infoTable', report13fhr._short_tag(tag))

    def test_tags_and_vals(self):
        infoTable = '<infoTable>    <nameOfIssuer>COCA COLA FEMSA S A B DE C V</nameOfIssuer>    <titleOfClass>SPON ADR REP L</titleOfClass>    <cusip>191241108</cusip>    <value>466104</value>    <shrsOrPrnAmt>      <sshPrnamt>6214719</sshPrnamt>      <sshPrnamtType>SH</sshPrnamtType>    </shrsOrPrnAmt>    <investmentDiscretion>SOLE</investmentDiscretion>    <votingAuthority>      <Sole>6214719</Sole>      <Shared>0</Shared>      <None>0</None>    </votingAuthority>  </infoTable>'
        result = report13fhr._tags_and_vals(xml.etree.ElementTree.fromstring(infoTable))

        self.assertEqual(result['nameOfIssuer'], 'COCA COLA FEMSA S A B DE C V')
        self.assertEqual(result['shrsOrPrnAmt']['sshPrnamt'], '6214719')

    def test_get_infotables(self):
        informationTable = '<informationTable><infoTable>    <nameOfIssuer>COCA COLA FEMSA S A B DE C V</nameOfIssuer>    <titleOfClass>SPON ADR REP L</titleOfClass>    <cusip>191241108</cusip>    <value>466104</value>    <shrsOrPrnAmt>      <sshPrnamt>6214719</sshPrnamt>      <sshPrnamtType>SH</sshPrnamtType>    </shrsOrPrnAmt>    <investmentDiscretion>SOLE</investmentDiscretion>    <votingAuthority>      <Sole>6214719</Sole>      <Shared>0</Shared>      <None>0</None>    </votingAuthority>  </infoTable>  <infoTable>    <nameOfIssuer>CROWN CASTLE INTL CORP NEW</nameOfIssuer>    <titleOfClass>COM</titleOfClass>    <cusip>22822V101</cusip>    <value>502413</value>    <shrsOrPrnAmt>      <sshPrnamt>5332900</sshPrnamt>      <sshPrnamtType>SH</sshPrnamtType>    </shrsOrPrnAmt>    <investmentDiscretion>SOLE</investmentDiscretion>    <votingAuthority>      <Sole>5332900</Sole>      <Shared>0</Shared>      <None>0</None>    </votingAuthority>  </infoTable></informationTable>'
        result = report13fhr.get_infotables(xml.etree.ElementTree.fromstring(informationTable))

        holding1 = result[0]
        holding2 = result[1]

        self.assertEqual(holding1['nameOfIssuer'], 'COCA COLA FEMSA S A B DE C V')
        self.assertEqual(holding1['shrsOrPrnAmt']['sshPrnamt'], '6214719')

        self.assertEqual(holding2['nameOfIssuer'], 'CROWN CASTLE INTL CORP NEW')
        self.assertEqual(holding2['shrsOrPrnAmt']['sshPrnamt'], '5332900')

    def test_raises_exception_with_malformed_xml(self):
        malformed_xml = '<SEC-DOCUMENT>0001104659-16-156931.txt : 20161114'
        cik = 'viiix'
        accepted_date = datetime.datetime.now()
        submission_type = '13F-HR'

        self.assertRaises(xml.etree.ElementTree.ParseError,
                          report13fhr.get_13f_holdings, cik, accepted_date, submission_type, malformed_xml)

    def test_parse_valid_xml_with_namespace(self):
        holding_xml     = '/home/chpack/Documents/python/quovo_challenge/christian_packard/fund_holdings/resources/13f_hr_with_namespace.xml'
        cik             = 'viiix'
        accepted_date   = datetime.datetime.now()
        submission_type = '13F-HR'

        with open(holding_xml, 'r') as holdings:
            result = report13fhr.get_13f_holdings(cik, accepted_date, submission_type, holdings.read())

        holding1 = result.holdings[0]
        holding2 = result.holdings[1]

        self.assertEqual(holding1.entity, 'ALLIANCE DATA SYSTEMS CORP')
        self.assertEqual(holding1.shares, '5000000')
        self.assertEqual(holding1.value, '1072650')

        self.assertEqual(holding2.entity, 'ALLISON TRANSMISSION HLDGS I')
        self.assertEqual(holding2.shares, '19125204')
        self.assertEqual(holding2.value, '548511')

    def test_parse_valid_xml_without_namespace(self):
        holding_xml     = '/home/chpack/Documents/python/quovo_challenge/christian_packard/fund_holdings/resources/13f_hr_no_namespace.xml'
        cik             = 'viiix'
        accepted_date   = datetime.datetime.now()
        submission_type = '13F-HR'

        with open(holding_xml, 'r') as holdings:
            result = report13fhr.get_13f_holdings(cik, accepted_date, submission_type, holdings.read())

        holding1 = result.holdings[0]
        holding2 = result.holdings[1]

        self.assertEqual(holding1.entity, 'ARCOS DORADOS HOLDINGS INC')
        self.assertEqual(holding1.shares, '3060500')
        self.assertEqual(holding1.value, '16129')

        self.assertEqual(holding2.entity, 'AUTONATION INC')
        self.assertEqual(holding2.shares, '1898717')
        self.assertEqual(holding2.value, '92487')


if __name__ == '__main__':
    unittest.main()
