import os
import pytest

from technodeminer.similarity.buzzphrases import remove_articles, add_countdict, remove_low_count_words, regularise_key


def test_remove_articles_negative():
    str = "rubber baby buggy bumpers"
    out_str = remove_articles(str)
    assert out_str == out_str


def test_remove_articles_positive():
    str = "the rubber baby buggy bumpers"
    out_str = remove_articles(str)
    assert out_str == "rubber baby buggy bumpers"


def test_add_countdict():
    correct_outputdict = {'a':1, 'b':1}
    input_dict = {'a':2, 'b':1}
    out_dict = add_countdict(correct_outputdict, input_dict)
    assert out_dict['a'] == 3


def test_remove_low_count_words():
    dict = {'a': 2, 'b': 1}
    out_dict = remove_low_count_words(dict)
    assert 'b' not in out_dict


def test_regularise_key_uppercase():
    str = "FOOBAR foobar FOOBAR"
    assert regularise_key(str) == "foobar foobar foobar"


def test_regularise_key_article():
    str = "the foobar FOOBAR"
    assert regularise_key(str) == "foobar foobar"

def test_regularise_key_singularize():
    str = "magic body clocks"
    assert regularise_key(str) == "magic body clock"
