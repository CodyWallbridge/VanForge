import pytest
from backend.app.utils.validation import InvalidNameError, clean_name

@pytest.mark.parametrize("name", ["", "   ", "\t\n"])
def test_clean_name_rejects_blank_values(
    name,
):
    with pytest.raises(InvalidNameError):
        clean_name(name)

def test_clean_name_trims_edges_and_preserves_spelling():
    assert clean_name("  Flask of Blood Knights  ") == "Flask of Blood Knights"
