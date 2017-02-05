import pprint

import holdings

xml_with_ns = '/home/chpack/Documents/python/quovo_challenge/christian_packard/fund_holdings/resources/13f_hr_with_namespace.xml'
xml_no_ns = '/home/chpack/Documents/python/quovo_challenge/christian_packard/fund_holdings/resources/13f_hr_no_namespace.xml'

ns_tree = ET.parse(xml_with_ns)
tree = ET.parse(xml_no_ns)

ns_root = ns_tree.getroot()
root = tree.getroot()


if __name__ == '__main__':
    # pp = pprint.PrettyPrinter(indent=4)
    # tables = get_infotables(root)
    # print(len(tables))
    # pp.pprint(tables)
    # cik = 'viiix'
    cik = '0001166559'
    forms = ['13F-HR', '13F-HR/A']
    results = get_archive_links(cik, *forms)
    print(results)
