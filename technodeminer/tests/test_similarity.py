import os
import pytest
from spacy.en import English
from technodeminer.similarity.buzzphrases import remove_articles, regularise_key

@pytest.fixture
def make_spacy():
    nlp = English()
    return nlp

def test_remove_articles_negative():
    str = "rubber baby buggy bumpers"
    out_str = remove_articles(str)
    assert out_str == out_str


def test_remove_articles_positive():
    str = "the rubber baby buggy bumpers"
    out_str = remove_articles(str)
    assert out_str == "rubber baby buggy bumpers"

def test_regularise_key_article():
    str = "the foobar"
    assert regularise_key(str) == "foobar"

def test_regularise_key_singularize():
    str = "magic body clocks"
    assert regularise_key(str) == "magic body clock"

def test_spacy_keyphrase_extraction():
    str = """To address the U.S. Air Force need for a low-cost, multibeam antenna to support tracking, telemetry, and
     command, Physical Optics Corporation (POC) proposes to develop a new Multifunctional Phased Array Antenna (MPAA)
      system operating at X-band (8 to 12 GHz) frequencies.  This proposed MPAA system is based on a multilayer
       structure integrating wideband circularly polarized planar antenna elements, low-loss wideband phase shifters,
        a wideband module, full duplex operation, and transmit/receive (T/R) modules.  The innovative new low-loss miniaturized phase shifter, wideband module, and full duplex operation will enable the MPAA system to provide flexibility in future satellite data links and air defense systems.  In addition, this phase shifter design will reduce the number of RF amplifiers in T/R modules to achieve the necessary EIRP, thus providing a new RF antenna element (T/R module integrated with antenna), which will cost less than $100 in production quantities.  In Phase I, POC will establish the feasibility of a 4x4 antenna subarray as the building block of a full capacity antenna system that meets the required system parameters such as EIRP and signal-to-noise ratio.  In Phase II, POC plans to develop a full duplex system incorporating T/R modules, a low-loss phase shifter, and antenna subarray.
    """