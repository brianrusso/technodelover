from collections import Sequence
from datetime import datetime
from fuzzywuzzy import process
from openpyxl import load_workbook
from technodeminer.util import nonelessdict


class SBIRReader(Sequence):

    def __init__(self, filename):
        self.ws = self.get_iterator(filename)
        self.companies = self.get_companies()
        self.records = self.get_records()

    def get_iterator(self, filename):
        wb = load_workbook(filename=filename, read_only=True)
        ws = wb.worksheets[0]
        return ws

    @staticmethod
    def process_company_name(name):
        name = name.strip()  # whitespace-b-gone
        # Strip commas and periods since they are low-information
        lowbits = [u'.', u',']
        dd = {ord(c):None for c in lowbits}
        name = name.translate(dd)
        # convert to lower case
        name = name.lower()
        return name

    def get_companies(self):
        companies = set()
        for record in self.ws.rows:
            companies.add(self.process_company_name(record[0].value))
        return companies

    def get_closest_company(self, search_str):
        #suggestion = max(self.companies, key=lambda a: fuzz.ratio(a, search_str))
        #score = fuzz.ratio(suggestion, search_str)
        #return (suggestion, score)
        return process.extractOne(search_str, self.companies)  # better/faster

    def __getitem__(self, item):
        return self.records[item]

    def __len__(self):
        return len(self.records)

    def __iter__(self):
        return iter(self.records)

    @staticmethod
    def load_sbir_contracts(filename, graph):
        # init sbir's
        reader = SBIRReader(filename)
        print "Loading contracts into arango"
        for contract in reader:
            graph.create_vertex("contracts", contract)

    def get_records(self):
        records = []
        headers = {}
        generator = self.ws.rows
        # store headers, converting to 0-index (excel is 1-origin index)
        for col in generator.next():
            headers[col.value.strip()] = col.column-1
        for record in generator:
            # check if contract is empty/exists
            rec = nonelessdict()
            rec['contract'] = record[headers['Contract']].value  # contract number
            rec['company'] = record[headers['Company']].value
            rec['award_title'] = record[headers['Award Title']].value
            rec['agency'] = record[headers['Agency']].value
            rec['branch'] = record[headers['Branch']].value
            rec['phase'] = record[headers['Phase']].value
            rec['program'] = record[headers['Program']].value  #SBIR/STTR
            rec['agency_num'] = record[headers['Agency Tracking #']].value
            try:
                award_start_dt = datetime.strptime(record[headers['Award Start Date']].value, "%B %d, %Y")
                rec['award_start_dt'] = award_start_dt.isoformat()
            except: pass
            try:
                award_close_dt = datetime.strptime(record[headers['Award Close Date']].value, "%B %d, %Y")
                rec['award_close_dt'] = award_close_dt.isoformat()
            except: pass
            rec['solicitation_num'] = record[headers['Solicitation #']].value
            rec['solicitation_yr'] = record[headers['Solicitation Year']].value
            rec['topic_code'] = record[headers['Topic Code']].value
            rec['award_year'] = record[headers['Award Year']].value
            rec['award_amount'] = record[headers['Award Amount']].value
            try: rec['keywords'] = record[headers['Research Keywords']].value.split(u",")
            except: pass
            rec['abstract'] = record[headers['Abstract']].value
            # only add ones with contracts
            if 'contract' in rec.keys():
                records.append(rec)

        return records
