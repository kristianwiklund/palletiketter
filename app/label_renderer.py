from datetime import date
from typing import List
from .excel_reader import Pallet


def _e(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


_CSS = """
body {
    font-family: "Courier New", Courier, monospace;
    font-size: 11pt;
    margin: 0;
    padding: 0;
    color: #000;
}
.page {
    padding: 28px 32px 24px 32px;
}
.header {
    border-bottom: 3px solid #000;
    margin-bottom: 14px;
    padding-bottom: 10px;
}
.pallet-id {
    font-size: 26pt;
    font-weight: bold;
    font-family: "Courier New", Courier, monospace;
}
.meta {
    font-size: 9pt;
    color: #333;
    margin-top: 4px;
    font-family: "Courier New", Courier, monospace;
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11pt;
    font-family: "Courier New", Courier, monospace;
}
th {
    background-color: #000;
    color: white;
    padding: 6px 8px;
    text-align: left;
    border: 1px solid #000;
    font-family: "Courier New", Courier, monospace;
    font-size: 10pt;
}
td {
    border: 1px solid #555;
    padding: 5px 8px;
    vertical-align: top;
    color: #000;
}
.col-sku  { width: 16%; }
.col-name { width: 49%; }
.col-last { width: 12%; text-align: right; }
.col-act  { width: 23%; }
"""


def render_pallet_html(pallet: Pallet) -> str:
    today = date.today().strftime("%Y-%m-%d")
    rows = "".join(
        f"<tr>"
        f"<td class='col-sku'>{_e(item.sku)}</td>"
        f"<td class='col-name'>{_e(item.name)}</td>"
        f"<td class='col-last'>{_e(item.last_count)}</td>"
        f"<td class='col-act'></td>"
        f"</tr>"
        for item in pallet.items
    )
    body = (
        f"<div class='page'>"
        f"<div class='header'>"
        f"<div class='pallet-id'>Pall: <b>{_e(pallet.location)}</b></div>"
        f"<div class='meta'>Datum: {today}&nbsp;&nbsp;&nbsp;Artiklar: {len(pallet.items)}</div>"
        f"</div>"
        f"<table width='100%'>"
        f"<thead><tr>"
        f"<th width='16%' class='col-sku'>Artikelnr</th>"
        f"<th width='49%' class='col-name'>Benämning</th>"
        f"<th width='12%' class='col-last'>Sen. inv.</th>"
        f"<th width='23%' class='col-act'>Faktiskt antal / OK</th>"
        f"</tr></thead>"
        f"<tbody>{rows}</tbody>"
        f"</table>"
        f"</div>"
    )
    return f"<html><head><meta charset='utf-8'><style>{_CSS}</style></head><body>{body}</body></html>"
