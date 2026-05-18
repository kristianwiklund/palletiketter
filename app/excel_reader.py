from dataclasses import dataclass, field
from typing import List
import io
import openpyxl
import xlrd
import msoffcrypto


@dataclass
class Item:
    sku: str
    name: str
    last_count: str


@dataclass
class Pallet:
    location: str
    items: List[Item] = field(default_factory=list)


def is_encrypted(path: str) -> bool:
    with open(path, "rb") as f:
        try:
            return msoffcrypto.OfficeFile(f).is_encrypted()
        except Exception:
            return False


def _decrypt(path: str, password: str) -> io.BytesIO:
    with open(path, "rb") as f:
        office = msoffcrypto.OfficeFile(f)
        office.load_key(password=password)
        buf = io.BytesIO()
        office.decrypt(buf)
    buf.seek(0)
    return buf


def _is_xls_magic(path: str) -> bool:
    with open(path, "rb") as f:
        return f.read(8) == b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"


def _iter_rows_xlsx(source) -> list:
    wb = openpyxl.load_workbook(source, data_only=True)
    return list(wb.active.iter_rows(min_row=2, values_only=True))


def _iter_rows_xls(path: str) -> list:
    wb = xlrd.open_workbook(path)
    ws = wb.sheet_by_index(0)
    return [ws.row_values(i) for i in range(1, ws.nrows)]


def _parse_rows(rows) -> List[Pallet]:
    pallets: dict[str, Pallet] = {}
    for row in rows:
        if not row or row[0] is None or row[0] == "":
            continue
        sku = str(row[0]).strip()
        name = str(row[1]).strip() if row[1] is not None else ""
        location = str(row[2]).strip() if row[2] is not None else ""
        last_count = str(row[3]).strip() if row[3] is not None else ""
        if not location:
            continue
        if location not in pallets:
            pallets[location] = Pallet(location=location)
        pallets[location].items.append(Item(sku=sku, name=name, last_count=last_count))
    return sorted(pallets.values(), key=lambda p: p.location)


def load_excel(path: str, password: str = None) -> List[Pallet]:
    if is_encrypted(path):
        buf = _decrypt(path, password)
        rows = _iter_rows_xlsx(buf)
    elif _is_xls_magic(path):
        rows = _iter_rows_xls(path)
    else:
        rows = _iter_rows_xlsx(path)
    return _parse_rows(rows)
