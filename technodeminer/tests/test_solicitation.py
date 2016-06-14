import pytest, os
from technodeminer.solicitation.model import SolicitationReader


@pytest.fixture
def solicitation_inst():
    SOLICITATION_FILE = os.path.join(os.getcwd(), 'technodeminer/tests/darpa_sbir_16.1_1.html')
    obj = SolicitationReader(SOLICITATION_FILE)
    return obj


def test_solicitation_elem_count(solicitation_inst):
    assert len(solicitation_inst) == 7


def test_objective(solicitation_inst):
    assert solicitation_inst[0]['objective'] == "Develop a novel platform for DNA assembly, transfer, and transfection" \
                                                " that uses synthetic DNA products to assemble DNA constructs at least" \
                                                " 50 kbp or at least 100 kbp in length for prokaryotes and eukaryotes," \
                                                " respectively, and transfer these into cells with a transfection" \
                                                " efficiency of at least 1%."


def test_topic(solicitation_inst):
    assert solicitation_inst[0]['topic'] == 'SB161-001'


def test_title(solicitation_inst):
    assert solicitation_inst[0]['title'] == 'Rapid Assembly and Transfer Techniques for Large DNA Constructs'


def test_keywords(solicitation_inst):
    assert solicitation_inst[0]['keywords'] == ['synthetic biology', 'genome editing', 'DNA', 'assembly', 'synthesis', 'transvection']


def test_techareas(solicitation_inst):
    assert solicitation_inst[0]['tech_areas'] == ['Biomedical', 'Materials/Processes']


def test_references(solicitation_inst):
    cit_str = u"Kosuri, S. & Church, G. M. (2014). Large-scale de novo DNA synthesis: technologies and applications." \
              u" Nature Methods, 11(5), 499\u2013507. http://doi.org/10.1038/nmeth.2918"
    assert solicitation_inst[0]['references'][0] == cit_str