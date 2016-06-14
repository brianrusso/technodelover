import os
import pytest

from technodeminer.r2.model import R2


@pytest.fixture
def r2_file():
    R2_FILE = os.path.join(os.getcwd(), 'technodeminer/tests/U_0607828J_7_PB_2017.xml')
    obj = R2.from_file(R2_FILE)
    return obj


@pytest.fixture
def r2_file_2():  # this one has a pe mission desc
    R2_FILE = os.path.join(os.getcwd(), 'tests/U_0607865A_7_PB_2017.xml')
    obj = R2.from_file(R2_FILE)
    return obj


def test_penum(r2_file):
    assert r2_file.get_penum() == '0607828J'


def test_petitle(r2_file):
    assert r2_file.get_petitle() == 'Joint Integration & Interoperability'


def test_byear(r2_file):
    assert r2_file.get_byear() == '2017'


def test_ap_code(r2_file):
    assert r2_file.get_ap_code() == '0400'


def test_ba_num(r2_file):
    assert r2_file.get_ba_num() == '7'


def test_agency(r2_file):
    assert r2_file.get_agency() == 'The Joint Staff'

