from openpyxl import load_workbook
from fuzzywuzzy import fuzz, process
from datetime import datetime

class SBIRReader(object):

    def __init__(self, filename):
        self.ws = self.get_iterator(filename)
        self.companies = self.get_companies()

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
            companies.add(SBIRReader.process_company_name(record[0].value))
        return companies

    def get_closest_company(self, search_str):
        #suggestion = max(self.companies, key=lambda a: fuzz.ratio(a, search_str))
        #score = fuzz.ratio(suggestion, search_str)
        #return (suggestion, score)
        return process.extractOne(search_str, self.companies)  # better/faster

    def get_records(self):
        records = dict()
        headers = dict()
        generator = self.ws.rows
        # store headers, converting to 0-index (excel is 1-origin index)
        for col in generator.next():
            headers[col.value.strip()] = col.column-1
        for record in generator:
            # check if contract is empty/exists
            contract = record[headers['Contract']].value  # contract number
            if contract is None or contract in records.keys():
                break
            rec = dict()
            rec['company'] = record[headers['Company']].value
            rec['award_title'] = record[headers['Award Title']].value
            rec['agency'] = record[headers['Agency']].value
            rec['branch'] = record[headers['Branch']].value
            rec['phase'] = record[headers['Phase']].value
            rec['program'] = record[headers['Program']].value  #SBIR/STTR
            rec['agency_num'] = record[headers['Agency Tracking #']].value
            rec['contract'] = record[headers['Contract']].value  # contract number
            rec['award_start_dt'] = datetime.strptime(record[headers['Award Start Date']].value, "%B %d, %Y")
            rec['award_close_dt'] = datetime.strptime(record[headers['Award Close Date']].value, "%B %d, %Y")
            rec['solicitation_num'] = record[headers['Solicitation #']].value
            rec['solicitation_yr'] = record[headers['Solicitation Year']].value
            rec['topic_code'] = record[headers['Topic Code']].value
            rec['award_year'] = record[headers['Award Year']].value
            rec['award_amount'] = record[headers['Award Amount']].value
            rec['keywords'] = record[headers['Research Keywords']].value.split(u",")
            rec['abstract'] = record[headers['Abstract']].value
            records[contract] = rec
        return records



