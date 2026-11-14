from backend.app.speech.extraction import is_empty, validate

CROPS = ["berseem", "grain_maize", "grain_sorghum", "wheat"]
BASE = {"seasons": [], "area": None, "answer": {"yes_no": None, "confirm": None, "dont_know": None}, "ambiguous": [], "off_topic": False}


def season(**kw):
    s = {"order": 2, "crop": None, "crop_said": None, "purpose": None, "sowing_date": None, "last_cut_date": None, "must_stay": None}
    s.update(kw)
    return s


def test_impossible_dates_become_null():
    x = validate({**BASE, "seasons": [season(sowing_date={"day": 31, "month": 2, "year": 2027})]}, CROPS)
    assert x["seasons"][0]["sowing_date"] is None
    y = validate({**BASE, "seasons": [season(sowing_date={"day": 15, "month": 13, "year": None})]}, CROPS)
    assert y["seasons"][0]["sowing_date"] is None


def test_shape_errors_reject_everything():
    assert validate({**BASE, "seasons": [{**season(), "extra": 1}]}, CROPS) is None
    assert validate({**BASE, "seasons": [season(order=9)]}, CROPS) is None
    assert validate({**BASE, "off_topic": "yes"}, CROPS) is None
    assert validate({**BASE, "seasons": [season(must_stay="true")]}, CROPS) is None


def test_ambiguous_options_limited_to_catalogue():
    x = validate({**BASE, "ambiguous": [{"path": "seasons[1].crop", "said": "ذرة", "options": ["grain_maize", "grain_sorghum", "popcorn"]}]}, CROPS)
    assert x["ambiguous"][0]["options"] == ["grain_maize", "grain_sorghum"]


def test_empty_is_no_match():
    assert is_empty(validate(BASE, CROPS))
