from lxml import etree


class R2(object):


    @staticmethod
    def build_projects(project_elements):

        projects = dict()
        for elem in project_elements:
            # key is project number
            proj = dict()
            key = elem.find("r2:ProjectNumber", elem.nsmap).text
            proj['title'] = elem.find("r2:ProjectTitle", elem.nsmap).text
            proj['funding_allprior'] = elem.find(".//r2:AllPriorYears", elem.nsmap).text
            proj['funding_prior'] = elem.find(".//r2:PriorYear", elem.nsmap).text
            proj['funding_curr'] = elem.find(".//r2:CurrentYear", elem.nsmap).text
            proj['mission_desc'] = elem.find(".//r2:ProjectMissionDescription", elem.nsmap).text
            accomp_plans = []
            for elem in elem.findall(".//r2:Text", elem.nsmap):
                accomp_plans.append(elem.text)
            proj['accomp_planned'] = accomp_plans
            # store project in projects of r2 node
            projects[key] = proj
        return projects

    def __init__(self, str):
        tree = etree.fromstring(str)
        root = tree.getroot()

        # singular* (should be anyway)
        self.pe_num = root.find(".//r2:ProgramElementNumber", root.nsmap).text
        self.pe_title = root.find(".//r2:ProgramElementTitle", root.nsmap).text
        self.fyear = root.find(".//r2:BudgetYear", root.nsmap).text
        self.ap_code = root.find(".//r2:AppropriationCode", root.nsmap).text
        self.ba_num = root.find(".//r2:BudgetActivityNumber", root.nsmap).text
        self.agency = root.find(".//r2:ServiceAgencyName", root.nsmap).text
        self.program_desc = root.find(".//r2:ProgramElementMissionDescription", root.nsmap).text


        # plural
        self.projects = self.build_projects(root.findall(".//r2:Project", root.nsmap))


    def __repr__(self):
        return self.pe_num + "(" + self.pe_title + ")"

    # Return Program Description, and for each project: mission desc + each accomp + plan as string
    def get_text(self):
        output = self.program_desc
        for k, v in self.projects:
            output += v['mission_desc']
            output.join(v['accomp_plans'])
        return output
