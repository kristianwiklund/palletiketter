"""Renders a sample label to docs/screenshot.jpg for the README."""
import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage, QPainter, QTextDocument
from PyQt6.QtCore import QSizeF, Qt

# A4 at 96 dpi
PAGE_W = 794
PAGE_H = 1123

app = QApplication(sys.argv)

from app.excel_reader import load_excel
from app.label_renderer import render_first_page

pallets = load_excel("sample_inventory.xlsx")
pallet = next(p for p in pallets if p.location == "PALL-A1")

html = render_first_page(pallet, pallet.items)

doc = QTextDocument()
doc.setPageSize(QSizeF(PAGE_W, PAGE_H))
doc.setHtml(html)

img = QImage(PAGE_W, PAGE_H, QImage.Format.Format_RGB32)
img.fill(Qt.GlobalColor.white)

painter = QPainter(img)
doc.drawContents(painter)
painter.end()

os.makedirs("docs", exist_ok=True)
img.save("docs/screenshot.jpg", "JPEG", 88)
print(f"Saved docs/screenshot.jpg ({PAGE_W}x{PAGE_H})")
