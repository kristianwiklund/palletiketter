from dataclasses import dataclass, field
from typing import List
import openpyxl


@dataclass
class Item:
    sku: str
    name: str
    last_count: str


@dataclass
class Pallet:
    location: str
    items: List[Item] = field(default_factory=list)


def load_excel(path: str) -> List[Pallet]:
    wb = openpyxl.load_workbook(path, data_only=True)
    ws = wb.active

    pallets: dict[str, Pallet] = {}

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or row[0] is None:
            continue
        sku = str(row[0]).strip() if row[0] is not None else ""
        name = str(row[1]).strip() if row[1] is not None else ""
        location = str(row[2]).strip() if row[2] is not None else ""
        last_count = str(row[3]).strip() if row[3] is not None else ""

        if not location:
            continue

        if location not in pallets:
            pallets[location] = Pallet(location=location)
        pallets[location].items.append(Item(sku=sku, name=name, last_count=last_count))

    return sorted(pallets.values(), key=lambda p: p.location)
