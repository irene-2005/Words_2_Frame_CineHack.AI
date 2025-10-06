import textwrap

import pytest

from app.ai_integration import ScriptExtractionError, _read_script_text, naive_scene_breakdown


def test_naive_scene_breakdown_extracts_multiple_scenes():
    script = textwrap.dedent(
        """
        INT. LIVING ROOM - DAY
        JOHN sits on the couch reading a script.
        SARAH
        We need to hurry!

        EXT. CITY STREET - NIGHT
        Cars RACE past as lights flicker.
        JOHN
        I'm on my way.
        """
    ).strip()

    scenes = naive_scene_breakdown(script)

    assert len(scenes) == 2
    assert scenes[0]["heading"].upper().startswith("INT")
    assert "JOHN" in scenes[0]["description"].upper()
    assert scenes[0]["word_count"] > 0
    assert any("RACE" in line.upper() for line in scenes[1]["content"])
    assert scenes[0]["characters"]  # should identify character names
    assert scenes[0]["time_of_day"].upper() == "DAY"
    assert scenes[0]["location"] == "LIVING ROOM"
    assert scenes[0]["tone"] in {"neutral", "action", "drama", "romance", "comedy", "thriller"}


def test_naive_scene_breakdown_handles_scripts_without_headings():
    script = "Once upon a time, there was a screenplay fragment without clear scene headings."

    scenes = naive_scene_breakdown(script)

    assert len(scenes) == 1
    assert scenes[0]["word_count"] > 0
    assert "Scene" in scenes[0]["heading"] or scenes[0]["heading"].upper() == "OPENING"
    assert scenes[0]["location"] is None
    assert scenes[0]["characters"] == []


MINIMAL_PDF_BYTES = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 62 >>\nstream\nBT /F1 18 Tf 36 100 Td (INT. ROOM - DAY) Tj T* (JOHN) Tj ET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000112 00000 n \n0000000230 00000 n \n0000000340 00000 n \ntrailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n398\n%%EOF"


def test_read_script_text_from_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(MINIMAL_PDF_BYTES)

    text = _read_script_text(str(pdf_path))

    assert "INT. ROOM - DAY" in text
    assert "JOHN" in text


def test_read_script_text_from_missing_file(tmp_path):
    missing = tmp_path / "ghost.pdf"
    with pytest.raises(ScriptExtractionError):
        _read_script_text(str(missing))
