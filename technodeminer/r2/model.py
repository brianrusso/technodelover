from lxml import etree
from lxml.etree import XMLSyntaxError
import json
from technodeminer.persistence.graph import get_technode_graph, connect_to_arango
from pattern.vector import Document

def r2file_to_arango(filename, colname='r2_exhibits'):
    try:
        this_r2 = R2.from_file(filename)
        this_r2.to_arango()
    except InvalidR2Exception:
        pass  # FIXME: be silent for now.. should log this somewhere


class InvalidR2Exception(Exception):
    pass

class R2(dict):

    @staticmethod
    def from_file(filename):
        try:
            tree = etree.parse(filename)
        except XMLSyntaxError:
            raise InvalidR2Exception("Malformed XML in %s" % filename)
        return R2.from_xmltree(tree, url=filename)

    @staticmethod
    def from_str(str):
        tree = etree.fromstring(str)
        return R2.from_xmltree(tree)

    def to_arango(self, colname='r2_exhibits'):
        db = connect_to_arango()
        graph = get_technode_graph(db)
        graph.create_vertex(colname, self)

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
            try:
                proj['mission_desc'] = elem.find(".//r2:ProjectMissionDescription", elem.nsmap).text
            except AttributeError:
                pass # very small percentage lack description for project
            accomp_plans = []
            for elem in elem.findall(".//r2:Text", elem.nsmap):
                accomp_plans.append(elem.text)
            proj['accomp_planned'] = accomp_plans
            # store project in projects of r2 node
            projects[key] = proj
        return projects

    @staticmethod
    def build_penum(root):
        return root.find(".//r2:ProgramElementNumber", root.nsmap).text

    @staticmethod
    def build_petitle(root):
        return root.find(".//r2:ProgramElementTitle", root.nsmap).text

    @staticmethod
    def build_byear(root):
        return root.find(".//r2:BudgetYear", root.nsmap).text

    @staticmethod
    def build_ap_code(root):
        return root.find(".//r2:AppropriationCode", root.nsmap).text

    @staticmethod
    def build_ba_num(root):
        return int(root.find(".//r2:BudgetActivityNumber", root.nsmap).text)

    @staticmethod
    def build_agency(root):
        return root.find(".//r2:ServiceAgencyName", root.nsmap).text

    @staticmethod
    def build_program_desc(root):
        try:  # this appears to be optional since some lack it
            return root.find(".//r2:ProgramElementMissionDescription", root.nsmap).text.strip()
        except AttributeError:
            return None

    def __init__(self):
        super(R2, self).__init__()

    @staticmethod
    def from_xmltree(tree, url=None):
        new_r2 = R2()
        root = tree.getroot()
        if 'proc' in root.nsmap:
            raise InvalidR2Exception('Found procurement prefix; likely is a procurement record')
        elif not 'r2' in root.nsmap:
            raise InvalidR2Exception("R2 Prefix not in root.nsmap")

        # singular* (should be anyway)
        if url:
            new_r2['url'] = url
        new_r2['pe_num'] = new_r2.build_penum(root)
        new_r2['pe_title'] = new_r2.build_petitle(root)
        new_r2['byear'] = new_r2.build_byear(root)
        new_r2['ap_code'] = new_r2.build_ap_code(root)
        new_r2['ba_num'] = new_r2.build_ba_num(root)
        new_r2['agency'] = new_r2.build_agency(root)
        new_r2['program_desc'] = new_r2.build_program_desc(root)

        # plural
        new_r2['projects'] = new_r2.build_projects(root.findall(".//r2:Project", root.nsmap))

        # all text
        #new_r2['all_text'] = new_r2.get_text()
        return new_r2
    #def __repr__(self):
    #    return self.pe_num + "(" + self.pe_title + ")"

    # Return Program Description, and for each project: mission desc + each accomp + plan as string
    def get_text(self):
        output = self['program_desc']
        for k, v in self['projects'].iteritems():
            output += v['mission_desc']
            output.join(v['accomp_planned'])
        return output

    def as_pattern_doc(self):
        doc = Document(self.get_text(), name=self['pe_num'], type="R2")
        return doc

    def to_json_file(self, filename):
        with open(filename,'w') as fp:
            json.dump(self, fp)
