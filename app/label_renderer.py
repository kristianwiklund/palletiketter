from datetime import date
from typing import List
from .excel_reader import Pallet, Item


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
    padding: 0 32px 24px 32px;
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
    word-wrap: break-word;
}
.col-sku  { width: 16%; }
.col-name { width: 49%; }
.col-last { width: 12%; text-align: right; }
.col-act  { width: 23%; }
"""

_TABLE_HEADER = (
    "<table width='100%' style='table-layout: fixed;'>"
    "<thead><tr>"
    "<th width='16%' class='col-sku'>Artikelnr</th>"
    "<th width='49%' class='col-name'>Benämning</th>"
    "<th width='12%' class='col-last'>Sen. inv.</th>"
    "<th width='23%' class='col-act'>Faktiskt antal / OK</th>"
    "</tr></thead>"
)


def _rows_html(items: List[Item]) -> str:
    return "".join(
        f"<tr>"
        f"<td class='col-sku'>{_e(item.sku)}</td>"
        f"<td class='col-name'>{_e(item.name)}</td>"
        f"<td class='col-last'>{_e(item.last_count)}</td>"
        f"<td class='col-act'></td>"
        f"</tr>"
        for item in items
    )


def _wrap(body: str) -> str:
    return f"<html><head><meta charset='utf-8'><style>{_CSS}</style></head><body>{body}</body></html>"


def render_first_page(pallet: Pallet, items: List[Item]) -> str:
    today = date.today().strftime("%Y-%m-%d")
    # Big black text on white — readable from across a warehouse, no inverse blobs
    banner = (
        f"<table width='100%' style='border: 4px solid #000; margin-bottom: 14px;'>"
        f"<tr><td style='padding: 16px 20px 8px 20px;"
        f" border-bottom: 2px solid #000;"
        f" font-size: 80pt; font-weight: bold;"
        f" font-family: \"Courier New\", Courier, monospace; color: #000;'>"
        f"{_e(pallet.location)}"
        f"</td></tr>"
        f"<tr><td style='padding: 6px 20px 10px 20px;"
        f" font-size: 10pt;"
        f" font-family: \"Courier New\", Courier, monospace; color: #000;'>"
        f"{today}&nbsp;&nbsp;&nbsp;&nbsp;{len(pallet.items)} artiklar"
        f"</td></tr>"
        f"</table>"
    )
    body = f"<div class='page'>{banner}{_TABLE_HEADER}<tbody>{_rows_html(items)}</tbody></table></div>"
    return _wrap(body)


def render_continuation_page(pallet: Pallet, items: List[Item], page_num: int) -> str:
    today = date.today().strftime("%Y-%m-%d")
    cont_header = (
        f"<table width='100%' style='margin-top: 28px; margin-bottom: 12px;"
        f" border-bottom: 3px solid #000;'>"
        f"<tr><td style='padding: 0 0 6px 0;"
        f" font-family: \"Courier New\", Courier, monospace; color: #000;'>"
        f"<span style='font-size: 16pt; font-weight: bold;'>{_e(pallet.location)}</span>"
        f"<span style='font-size: 9pt;'>"
        f"&nbsp;&nbsp;/&nbsp;&nbsp;sida {page_num}&nbsp;&nbsp;/&nbsp;&nbsp;{today}"
        f"</span>"
        f"</td></tr>"
        f"</table>"
    )
    body = f"<div class='page'>{cont_header}{_TABLE_HEADER}<tbody>{_rows_html(items)}</tbody></table></div>"
    return _wrap(body)
