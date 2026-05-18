"""Generates sample_inventory.xlsx for testing."""
import openpyxl

wb = openpyxl.Workbook()
ws = wb.active
ws.title = "Inventarie"
ws.append(["Artikelnr", "Benämning", "Plats", "Senaste inventering"])

data = [
    ("ART-001", "Skruv M6x20 rostfri", "PALL-A1", 500),
    ("ART-002", "Skruv M8x30 rostfri", "PALL-A1", 250),
    ("ART-003", "Mutter M6 rostfri", "PALL-A1", 800),
    ("ART-004", "Bricka M6 rostfri", "PALL-A1", 1200),
    ("ART-005", "Bricka M8 rostfri", "PALL-A1", 600),
    ("ART-006", "Sprintbult 5x40", "PALL-B3", 300),
    ("ART-007", "Sprintbult 6x50", "PALL-B3", 150),
    ("ART-008", "Låsbricka M10", "PALL-B3", 400),
    ("ART-009", "Pinnbult M10x80", "PALL-C7", 200),
    ("ART-010", "Pinnbult M12x100", "PALL-C7", 100),
    ("ART-011", "Sexkantsbult M10x60", "PALL-C7", 350),
    ("ART-012", "Sexkantsbult M12x80", "PALL-C7", 175),
    ("ART-013", "Extremt lång produktbenämning som verkligen inte får plats på en rad utan måste brytas och flöda ned på nästa rad i cellen", "PALL-C7", 42),
]

for row in data:
    ws.append(row)

wb.save("sample_inventory.xlsx")
print("Wrote sample_inventory.xlsx")
