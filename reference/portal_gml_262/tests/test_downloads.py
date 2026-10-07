import base64
import re

from downloads import download_html


def test_authorized_bytes_travel_inline_without_public_media_path():
    html = download_html("Roteiro", "Atenção e avaliação", "roteiro.md", "text/markdown")
    encoded = re.search(r"base64,([^\"]+)", html).group(1)
    assert base64.b64decode(encoded).decode("utf-8") == "Atenção e avaliação"
    assert "/media/" not in html


def test_download_label_and_filename_cannot_inject_markup():
    html = download_html('<script>alert(1)</script>', b'ok', 'x" onclick="alert(1)', "text/plain")
    assert "<script>" not in html
    assert 'download="x&quot; onclick=&quot;alert(1)"' in html
