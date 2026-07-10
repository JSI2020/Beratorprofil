from src.utils.export_name import DEFAULT_EXPORT_STEM, default_export_filename


def test_default_export_filename_never_includes_person_name():
    assert DEFAULT_EXPORT_STEM == "Beraterprofil"
    assert default_export_filename() == "Beraterprofil.pptx"
    assert default_export_filename(suffix=".json") == "Beraterprofil.json"
