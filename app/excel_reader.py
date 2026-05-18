from dataclasses import dataclass, field
from typing import List
import os
import openpyxl
import xlrd


@dataclass
class Item:
    sku: str
    name: str
    last_count: str


@dataclass
class Pallet:
    location: str
    items: List[Item] = field(default_factory=list)


def _iter_rows_xlsx(path: str):
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active
    for row in ws.iter_rows(min_row=2, values_only=True):
        yield row


def _iter_rows_xls(path: str):
    wb = xlrd.open_workbook(path)
    ws = wb.sheet_by_index(0)
    for i in range(1, ws.nrows):
        yield ws.row_values(i)


def load_excel(path: str) -> List[Pallet]:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".xls":
        rows = _iter_rows_xls(path)
    else:
        rows = _iter_rows_xlsx(path)

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
