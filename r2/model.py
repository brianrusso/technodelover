from lxml import etree


class R2(object):

    @staticmethod
    def from_file(filename):
        tree = etree.parse(filename)
        return R2(tree)

    @staticmethod
    def from_str(str):
        tree = etree.fromstring(str)
        return R2(tree)

    @staticmethod
    def build_projects(project_elements):

        projects = dict()
        for elem in project_elements:
            # key is project number
            proj = dict()
            key = elem.find("r2:ProjectNumber", elem.nsmap).text
            proj['title'] = elem.find("r2:ProjectTitle", elem.nsmap).text
            try:
                proj['funding_allprior'] = elem.find(".//r2:AllPriorYears", elem.nsmap).text
            except AttributeError:
                pass

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

    def get_penum(self):
        return self.root.find(".//r2:ProgramElementNumber", self.root.nsmap).text

    def get_petitle(self):
        return self.root.find(".//r2:ProgramElementTitle", self.root.nsmap).text

    def get_byear(self):
        return self.root.find(".//r2:BudgetYear", self.root.nsmap).text

    def get_ap_code(self):
        return self.root.find(".//r2:AppropriationCode", self.root.nsmap).text

    def get_ba_num(self):
        return self.root.find(".//r2:BudgetActivityNumber", self.root.nsmap).text

    def get_agency(self):
        return self.root.find(".//r2:ServiceAgencyName", self.root.nsmap).text

    def get_program_desc(self):
        try:  # this appears to be optional since some lack it
            return self.root.find(".//r2:ProgramElementMissionDescription", self.root.nsmap).text.strip()
        except AttributeError:
            return None

    def __init__(self, tree):
        self.root = tree.getroot()

        # singular* (should be anyway)
        self.pe_num = self.get_penum()
        self.pe_title = self.get_petitle()
        self.byear = self.get_byear()
        self.ap_code = self.get_ap_code()
        self.ba_num = self.get_ba_num()
        self.agency = self.get_agency()
        self.program_desc = self.get_program_desc()

        # plural
        self.projects = self.build_projects(self.root.findall(".//r2:Project", self.root.nsmap))

    def __repr__(self):
        return self.pe_num + "(" + self.pe_title + ")"

    # Return Program Description, and for each project: mission desc + each accomp + plan as string
    def get_text(self):
        output = self.program_desc
        for k, v in self.projects.iteritems():
            output += v['mission_desc']
            output.join(v['accomp_planned'])
        return output
