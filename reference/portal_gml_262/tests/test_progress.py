import pytest
from progress import export_notebook, import_notebook


def test_notebook_roundtrip():
    completed, notes = import_notebook(export_notebook({0, 6, 30}, {"6": "Atenção combina valores."}))
    assert completed == {0, 6, 30}
    assert notes["6"] == "Atenção combina valores."


@pytest.mark.parametrize("data", ['[]', '{"version":1,"completed":[31]}', '{"version":1,"completed":[true]}', '{"version":1,"notes":{"6":null}}', '{"version":1,"notes":{"secret":"x"}}', 'not json', 'x' * 200001], ids=["array", "lesson-range", "boolean-id", "null-note", "unknown-key", "invalid-json", "too-large"])
def test_invalid_notebooks(data):
    with pytest.raises(ValueError):
        import_notebook(data)
