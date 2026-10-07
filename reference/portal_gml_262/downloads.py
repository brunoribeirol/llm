"""Send authorized downloads over the existing WebSocket, without /media URLs."""
import base64
from html import escape

import streamlit as st


def download_html(label: str, data: bytes | str, filename: str, mime: str) -> str:
    payload = data.encode("utf-8") if isinstance(data, str) else data
    encoded = base64.b64encode(payload).decode("ascii")
    return f'''<!doctype html><html lang="pt-BR"><meta charset="utf-8">
<style>body{{margin:0;font:14px system-ui,sans-serif}}a{{display:inline-block;padding:10px 15px;color:#146952;background:#eaf5ef;border:1px solid #bad9ca;border-radius:8px;text-decoration:none;font-weight:600}}a:hover{{background:#dbeee3}}a:focus-visible{{outline:3px solid #204dc1;outline-offset:2px}}</style>
<a href="data:{escape(mime, quote=True)};base64,{encoded}" download="{escape(filename, quote=True)}">↓ {escape(label)}</a></html>'''


def download_link(label: str, data: bytes | str, filename: str, mime="text/plain"):
    st.iframe(download_html(label, data, filename, mime), height=58)
