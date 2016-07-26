# -*- coding: utf-8 -*-
import pytest, os
from technodeminer.solicitation.model import HTMLSolicitationReader, OldHTMLSolicitationReader

@pytest.fixture
def solicitation_inst_old6():
    solicitation_file = os.path.join(os.getcwd(), 'technodeminer/tests/navy03.htm')
    obj_old = OldHTMLSolicitationReader.from_htmlfile(solicitation_file)
    return obj_old

@pytest.fixture
def solicitation_inst_old5():
    solicitation_file = os.path.join(os.getcwd(), 'technodeminer/tests/dtra041.htm')
    obj_old = OldHTMLSolicitationReader.from_htmlfile(solicitation_file)
    return obj_old

@pytest.fixture
def solicitation_inst_old4():
    solicitation_file = os.path.join(os.getcwd(), 'technodeminer/tests/dtra061.htm')
    obj_old = OldHTMLSolicitationReader.from_htmlfile(solicitation_file)
    return obj_old

@pytest.fixture
def solicitation_inst_old3():
    solicitation_file = os.path.join(os.getcwd(), 'technodeminer/tests/army922.htm')
    obj_old = OldHTMLSolicitationReader.from_htmlfile(solicitation_file)
    return obj_old

@pytest.fixture
def solicitation_inst_old2():
    solicitation_file = os.path.join(os.getcwd(),'technodeminer/tests/darpa133.htm')
    obj_old = OldHTMLSolicitationReader.from_htmlfile(solicitation_file)
    return obj_old

@pytest.fixture
def solicitation_inst_old():
    solicitation_file = os.path.join(os.getcwd(), 'technodeminer/tests/darpa141.htm')
    obj_old = OldHTMLSolicitationReader.from_htmlfile(solicitation_file)
    return obj_old


def test_topic_old6(solicitation_inst_old6):
    assert solicitation_inst_old6[0]['topic'] == u'N03-T001'

def test_topic_len_old6(solicitation_inst_old6):
    assert len(solicitation_inst_old6) == 26


def test_topic_old5(solicitation_inst_old5):
    assert solicitation_inst_old5[0]['topic'] == u'DTRA04-001'

def test_topic_len_old5(solicitation_inst_old5):
    assert len(solicitation_inst_old5) == 12

def test_topic_old4(solicitation_inst_old4):
    assert solicitation_inst_old4[0]['topic'] == u'DTRA06-001'

def test_topic_len_old4(solicitation_inst_old4):
    assert len(solicitation_inst_old4) == 13

def test_topic_old2(solicitation_inst_old2):
    assert solicitation_inst_old2[0]['topic'] == u'SB133-001'

def test_topic_num_older_format(solicitation_inst_old3):
    assert len(solicitation_inst_old3) == 177


def test_topic_raw_len2(solicitation_inst_old2):
    assert len(solicitation_inst_old2.solicitations_raw) == 5


def test_topic_len2(solicitation_inst_old2):
    assert len(solicitation_inst_old2) == 5


def test_objective_old(solicitation_inst_old):
    assert solicitation_inst_old[0]['objective'] == u"To develop nanowire single-photon detectors of shortwave"\
                                                    u" infrared light with high system efficiency (>90%) and bandwidth" \
                                                    u" (~1 GHz), high fabrication yield, and with compact (~5U)" \
                                                    u" packaging and turnkey operation."



def test_solicitation_elem_count_old(solicitation_inst_old):
    assert len(solicitation_inst_old) == 5


def test_topic_old(solicitation_inst_old):
    assert solicitation_inst_old[0]['topic'] == u'SB141-001'


def test_title_old(solicitation_inst_old):
    assert solicitation_inst_old[0]['title'] == u'Superconducting Nanowire Single-Photon Detectors'


def test_keywords_old(solicitation_inst_old):
    assert solicitation_inst_old[0]['keywords'] == [u'Detectors', u'Single photon detectors',
                                                    u'Super conducting nanowire single photon detectors', u'WSi', u'NbN',
                                                    u'LIDAR', u'LADAR', u'Optical communications', u'Photon counting']


def test_techareas_old(solicitation_inst_old):
    assert solicitation_inst_old[0]['tech_areas'] == [u'Sensors', u'Electronics']


def test_references_old(solicitation_inst_old):
    cite_str = u"A. Restelli et al., \"Single-photon detection efficiency up to 50% at 1310 nm with an InGaAs/InP" \
               u" avalanche diode gated at 1.25 GHz,\" App. Phys. Lett. 102, 141104 (2013)."
    assert solicitation_inst_old[0]['references'][0] == cite_str


description_old_actual = u"""Single photon sensitive detectors have many applications including active and passive\
 imaging, traditional and upcoming quantum optical communications, and quantum information processing. For quantum\
 key distribution in fibers, for instance, the noise properties of the detectors limit the distance over which one\
 can establish a secure key. Similarly, for 3D imaging via LADAR, longitudinal resolution is limited by the detector\
 jitter while the detector sensitivity dictates the trade-off between illumination power and maximum range.\
 Therefore, a high-bandwidth, high-sensitivity, compact and readily available photon-counting detector is a key\
 technology for many future scientific developments and improved DoD application capabilities. Technologies for\
 detecting single photons in the telecom band include semiconductor devices such as Geiger-mode InGaAs avalanche\
 photodiodes (APDs) and superconducting devices like the transition edge sensor (TES). The InGaAs APDs can be operated\
 at temperatures accessible via thermoelectric cooling, making them ideal for applications requiring compact\
 photon-counting solutions. InGaAs APDs, however, are typically plagued by after-pulsing effects, making them\
 ill-suited for applications requiring high duty-cycle and high-rate detection [1]. Extremely high efficiency\
 and low dark counts can be achieved with superconducting TES detectors, but the rates are limited to less than 10\
 MHz and the systems must be operated in the 100 mK regime requiring an extensive cooling overhead [2]. New results\
 in superconducting nanowire devices [3] have shown that high detection rates, low dark-count rates (DCRs), and high\
 efficiency are all possible simultaneously with operating temperatures between 1 and 4 K. Despite these results,\
 further performance improvements are needed. For example, detection efficiency (DE) above 90% and bandwidth (BW)\
 approaching 1 GHz has yet to be achieved simultaneously. In addition, innovations leading to a reduction in the\
 system footprint and improved operability will provide better accessibility of such technologies to the relevant\
 scientific and engineering communities. The goal of this SBIR project is to further improve upon the current\
 state-of-the-art in nanowire single-photon\
 detector performance while advancing the supporting technologies to allow for a compact, turn-key commercial\
 system. The final system should provide multiple (>2), independent single-pixel detectors with performance\
 superior to all current commercially available options (DE>90%, BW~1GHz, DCR< 1 Hz) in a ~5U 19™ rack-mount\
 package. To achieve these goals, work under this SBIR may include the following: efforts to increase\
 fabrication yields through the use of new materials or fabrication techniques, new device designs to\
 improve bandwidth and sensitivity, efforts to reduce system SWaP through compact, application-specific\
 cooling systems, electronics, and packaging. PHASE I: Develop an initial concept design and model through computer\
 simulations key elements of the proposed\
 nanowire single-photon detection system. Demonstrate detector development capability by fabricating and testing\
 system parts with performance indicative of a final system achieving the SBIR goals. Exhibit the feasibility\
 of the approach through a laboratory demonstration of the critical system components. Phase I deliverables will\
 include a design review including quantitative justification for the expected system performance and a report\
 presenting the plans for Phase II. PHASE II: Construct and demonstrate the operation of a prototype system\
 validating the performance metrics outlined\
 in Phase I. The final system should be near turn-key and demonstrate all relevant performance characteristics\
 including the SWaP. The Transition Readiness Level to be reached is 5: Component and/or bread-board validation\
 in relevant environment. PHASE III: The detectors developed under this SBIR will have applications for the DoD which\
 include secure\
 communications and active stand-off imaging systems. The improved availability and SWaP will allow the use of these\
 detectors in all relevant government labs and open the door to new fieldable systems. For example, low power,\
 portable optical communication links exceeding RF system bandwidths by 10-100x may be possible using the technology\
 developed under this SBIR [4,5]. The technology developed as a consequence of this effort will have applications which\
 span both DoD and non-DoD areas.\
 One application particularly suited to the private sector is the analysis of integrated circuits (IC).\
 Failure analysis via optical means is known to provide specific information about the operation of individual IC\
 elements. Higher speed and sensitivity of detection leads to higher throughput for such diagnostic systems.\
 Additionally, the technology developed under this SBIR may be integrated into commercially manufactured DoD\
 products such as LADAR and optical communication systems."""

def test_description_old(solicitation_inst_old):
    assert solicitation_inst_old[0]['description'] == description_old_actual

# NEW FORMAT


@pytest.fixture
def solicitation_inst():
    solicitation_file = os.path.join(os.getcwd(), 'technodeminer/tests/darpa_sbir_16.1_1.html')
    obj = HTMLSolicitationReader.from_htmlfile(solicitation_file)
    return obj

@pytest.fixture
def solicitation_inst1():
    solicitation_file = os.path.join(os.getcwd(), 'technodeminer/tests/army162.html')
    obj = HTMLSolicitationReader.from_htmlfile(solicitation_file)
    return obj

@pytest.fixture
def solicitation_inst2():
    solicitation_file = os.path.join(os.getcwd(), 'technodeminer/tests/af161.html')
    obj = HTMLSolicitationReader.from_htmlfile(solicitation_file)
    return obj

def test_topic_2(solicitation_inst2):
    assert solicitation_inst2[0]['topic'] == 'AF161-001'

def test_title_2(solicitation_inst2):
    assert solicitation_inst2[0]['title'] == 'Rapid Expeditionary Fuel Reclamation'

def test_topic_2a(solicitation_inst2):
    assert solicitation_inst2[31]['topic'] == 'AF161-032'

def test_title_2a(solicitation_inst2):
    assert solicitation_inst2[31]['title'] == 'IRIG Data Recorder Validation'

def test_title_1(solicitation_inst1):
    assert solicitation_inst1[0]['title'] == 'Flexible Integrated Intelligent Network (FIIN) for Prognostics Health Management (PHM) Systems'


def test_solicitation_elem_count(solicitation_inst):
    assert len(solicitation_inst) == 7


def test_objective(solicitation_inst):
    assert solicitation_inst[0]['objective'] == "Develop a novel platform for DNA assembly, transfer, and transfection" \
                                                " that uses synthetic DNA products to assemble DNA constructs at least" \
                                                " 50 kbp or at least 100 kbp in length for prokaryotes and eukaryotes," \
                                                " respectively, and transfer these into cells with a transfection" \
                                                " efficiency of at least 1%."

def test_topic(solicitation_inst):
    assert solicitation_inst[0]['topic'] == u'SB161-001'


def test_title(solicitation_inst):
    assert solicitation_inst[0]['title'] == 'Rapid Assembly and Transfer Techniques for Large DNA Constructs'


def test_keywords(solicitation_inst):
    assert solicitation_inst[0]['keywords'] == ['synthetic biology', 'genome editing', 'DNA', 'assembly', 'synthesis', 'transvection']


def test_techareas(solicitation_inst):
    assert solicitation_inst[0]['tech_areas'] == ['Biomedical', 'Materials/Processes']


def test_references(solicitation_inst):
    cite_str = u"Kosuri, S. & Church, G. M. (2014). Large-scale de novo DNA synthesis: technologies and applications." \
              u" Nature Methods, 11(5), 499\u2013507. http://doi.org/10.1038/nmeth.2918"
    assert solicitation_inst[0]['references'][0] == cite_str
