from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QFileDialog, QStatusBar, QMessageBox, QSizePolicy, QInputDialog, QLineEdit,
)
from PyQt6.QtCore import Qt, QRectF, QSizeF
from PyQt6.QtGui import QFont, QPageSize, QTextDocument, QPainter
from PyQt6.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog

from .excel_reader import load_excel, is_encrypted, Pallet
from .label_renderer import render_first_page, render_continuation_page


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._pallets: list[Pallet] = []
        self._setup_ui()

    def _setup_ui(self):
        self.setWindowTitle("Pallskrivare")
        self.setMinimumSize(520, 580)

        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(10)
        root.setContentsMargins(16, 16, 16, 12)

        # --- File row ---
        file_row = QHBoxLayout()
        self._btn_load = QPushButton("Ladda Excel…")
        self._btn_load.setFixedWidth(130)
        self._btn_load.clicked.connect(self._load_excel)
        self._lbl_file = QLabel("Ingen fil laddad")
        self._lbl_file.setStyleSheet("color: #888;")
        self._lbl_file.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        file_row.addWidget(self._btn_load)
        file_row.addWidget(self._lbl_file)
        root.addLayout(file_row)

        # --- List label ---
        lbl = QLabel("Pallar att skriva ut:")
        lbl.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        root.addWidget(lbl)

        # --- Pallet list ---
        self._list = QListWidget()
        self._list.setSelectionMode(QListWidget.SelectionMode.NoSelection)
        root.addWidget(self._list, stretch=1)

        # --- Select helpers ---
        sel_row = QHBoxLayout()
        btn_all = QPushButton("Välj alla")
        btn_all.clicked.connect(self._select_all)
        btn_none = QPushButton("Avmarkera alla")
        btn_none.clicked.connect(self._select_none)
        sel_row.addWidget(btn_all)
        sel_row.addWidget(btn_none)
        sel_row.addStretch()
        root.addLayout(sel_row)

        # --- Print row ---
        print_row = QHBoxLayout()
        print_row.addStretch()
        self._btn_preview = QPushButton("Förhandsgranska")
        self._btn_preview.setEnabled(False)
        self._btn_preview.clicked.connect(self._preview)
        self._btn_print = QPushButton("Skriv ut")
        self._btn_print.setEnabled(False)
        self._btn_print.clicked.connect(self._print)
        print_row.addWidget(self._btn_preview)
        print_row.addWidget(self._btn_print)
        root.addLayout(print_row)

        # --- Status bar ---
        self._status = QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Redo.")

    # ------------------------------------------------------------------
    def _load_excel(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Välj inventarielista", "",
            "Excel-filer (*.xlsx *.xls)"
        )
        if not path:
            return
        try:
            password = None
            if is_encrypted(path):
                pwd, ok = QInputDialog.getText(
                    self, "Lösenordsskyddad fil",
                    "Filen är krypterad. Ange lösenord:",
                    QLineEdit.EchoMode.Password,
                )
                if not ok:
                    return
                password = pwd
            self._pallets = load_excel(path, password=password)
            self._populate_list()
            filename = path.replace("\\", "/").split("/")[-1]
            self._lbl_file.setText(filename)
            self._lbl_file.setStyleSheet("color: #000;")
            self._btn_preview.setEnabled(True)
            self._btn_print.setEnabled(True)
            total_items = sum(len(p.items) for p in self._pallets)
            self._status.showMessage(
                f"Laddade {len(self._pallets)} pallar, {total_items} artikelrader."
            )
        except Exception as exc:
            QMessageBox.critical(self, "Fel vid inläsning", str(exc))
            self._status.showMessage("Fel vid inläsning.")

    def _populate_list(self):
        self._list.clear()
        for pallet in self._pallets:
            item = QListWidgetItem(
                f"{pallet.location}   ({len(pallet.items)} artiklar)"
            )
            item.setCheckState(Qt.CheckState.Checked)
            self._list.addItem(item)

    def _select_all(self):
        for i in range(self._list.count()):
            self._list.item(i).setCheckState(Qt.CheckState.Checked)

    def _select_none(self):
        for i in range(self._list.count()):
            self._list.item(i).setCheckState(Qt.CheckState.Unchecked)

    def _selected_pallets(self) -> list[Pallet]:
        return [
            self._pallets[i]
            for i in range(self._list.count())
            if self._list.item(i).checkState() == Qt.CheckState.Checked
        ]

    # ------------------------------------------------------------------
    def _make_printer(self) -> QPrinter:
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        return printer

    def _make_doc(self, html: str, page_w: float, page_h: float) -> QTextDocument:
        doc = QTextDocument()
        doc.setPageSize(QSizeF(page_w, page_h))
        doc.setHtml(html)
        return doc

    def _rows_fitting(self, html_fn, items, page_w: float, page_h: float) -> int:
        """Binary search: max items from `items` whose rendered HTML fits in 1 page."""
        if not items:
            return 0
        # Guard: if even 1 item overflows, return 1 to avoid infinite loop
        if self._make_doc(html_fn(items[:1]), page_w, page_h).pageCount() > 1:
            return 1
        lo, hi = 1, len(items)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if self._make_doc(html_fn(items[:mid]), page_w, page_h).pageCount() <= 1:
                lo = mid
            else:
                hi = mid - 1
        return lo

    def _paint_page(self, painter: QPainter, doc: QTextDocument,
                    page_w: float, page_h: float):
        painter.save()
        painter.setClipRect(QRectF(0, 0, page_w, page_h))
        doc.drawContents(painter)
        painter.restore()

    def _paint(self, printer: QPrinter, pallets: list[Pallet]):
        pt_rect = printer.pageRect(QPrinter.Unit.Point)
        px_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
        scale_x = px_rect.width() / pt_rect.width()
        scale_y = px_rect.height() / pt_rect.height()
        page_w = pt_rect.width()
        page_h = pt_rect.height()

        painter = QPainter(printer)
        painter.scale(scale_x, scale_y)

        first = True
        for pallet in pallets:
            remaining = pallet.items
            page_num = 1

            while remaining:
                if page_num == 1:
                    html_fn = lambda items, p=pallet: render_first_page(p, items)
                else:
                    html_fn = lambda items, p=pallet, n=page_num: render_continuation_page(p, items, n)

                count = self._rows_fitting(html_fn, remaining, page_w, page_h)
                doc = self._make_doc(html_fn(remaining[:count]), page_w, page_h)

                if not first:
                    printer.newPage()
                first = False
                painter.resetTransform()
                painter.scale(scale_x, scale_y)

                self._paint_page(painter, doc, page_w, page_h)
                remaining = remaining[count:]
                page_num += 1

        painter.end()

    def _preview(self):
        selected = self._selected_pallets()
        if not selected:
            QMessageBox.information(self, "Inga pallar", "Välj minst en pall.")
            return
        printer = self._make_printer()
        dlg = QPrintPreviewDialog(printer, self)
        dlg.paintRequested.connect(lambda p: self._paint(p, selected))
        dlg.exec()

    def _print(self):
        selected = self._selected_pallets()
        if not selected:
            QMessageBox.information(self, "Inga pallar", "Välj minst en pall.")
            return
        printer = self._make_printer()
        dlg = QPrintDialog(printer, self)
        if dlg.exec() == QPrintDialog.DialogCode.Accepted:
            self._paint(printer, selected)
            self._status.showMessage(
                f"Skickade {len(selected)} pall-etiketter till skrivaren."
            )
