from src.utils.filename import sanitize_filename


def test_sanitize_filename_strips_tabs_and_control_chars():
    assert sanitize_filename("\tFahad Nasir") == "Fahad_Nasir"
    assert sanitize_filename("  John / Doe  ") == "John_Doe"
    assert sanitize_filename("\n") == "Beraterprofil"
