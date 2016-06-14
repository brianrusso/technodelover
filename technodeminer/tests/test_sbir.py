import pytest, os
from technodeminer.sbir.reader import SBIRReader


@pytest.fixture
def sbir_inst():
    SBIR_FILE = os.path.join(os.getcwd(), 'technodeminer/tests/subset-sbir.xlsx')
    obj = SBIRReader(SBIR_FILE)
    return obj


def test_solicitation_elem_count(sbir_inst):
    assert len(sbir_inst) == 407


def test_company(sbir_inst):
    assert sbir_inst[0]['company'] == "NAVSYS Corporation"

def test_contract(sbir_inst):
    assert sbir_inst[0]['contract'] == "FA9453-15-C-0433"

def test_topic(sbir_inst):
    assert sbir_inst[0]['topic_code'] == "AF141-122"

