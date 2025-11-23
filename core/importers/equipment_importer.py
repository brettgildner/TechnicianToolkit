from __future__ import annotations

"""
Controls the 'Import from Excel' function for the Equipment page.
"""

def import_from_excel(self):
    # Import Equipment Info entries from Excel file. Currently handles Serial Number ("Serial
    # No.", "Serial #", "Serial Number", etc), Building ("Building" or "BLDG"), Normalizes
    # headers safely, maps to EquipmentInfo model fields exactly.
    from PySide6.QtWidgets import QFileDialog, QMessageBox, QInputDialog
    import unicodedata, re, openpyxl

    # Step 1 – Choose file
    path, _ = QFileDialog.getOpenFileName(
        self,
        "Select Equipment Info Excel File",
        "",
        "Excel Files (*.xlsx)"
    )
    if not path:
        return

    try:
        wb = openpyxl.load_workbook(path)
        sheet_names = wb.sheetnames

        # Step 2 – Choose sheet
        sheet_name, ok = QInputDialog.getItem(
            self,
            "Select Sheet",
            "Choose which sheet to import:",
            sheet_names,
            0,
            False,
        )
        if not ok:
            wb.close()
            return

        ws = wb[sheet_name]

        # Header normalization
        def norm(h: str) -> str:
            if not h:
                return ""
            h = unicodedata.normalize("NFKC", h)
            h = h.replace("\n", " ")
            h = re.sub(r"\s+", " ", h)
            return h.strip().lower()

        # Grab the header row
        raw_header_cells = list(next(ws.iter_rows(min_row=1, max_row=1)))
        excel_headers = [norm(str(c.value)) for c in raw_header_cells]

        print("\nDEBUG – Normalized Excel headers:")
        for h in excel_headers:
            print(" •", repr(h))

        # Header map > EquipmentInfo fields
        header_map = {
            "area": "area",
            "customer": "customer",
            # Accept both "bldg" and "building"
            "bldg": "building",
            "building": "building",
            "room": "room",
            # MANY acceptable serial number variations:
            "serial no.": "serial_number",
            "serial no": "serial_number",
            "serial #": "serial_number",
            "serial number": "serial_number",
            "model": "model",
            "contact": "poc",
            "contact name": "poc",
            "poc": "poc",
            "contact phone": "poc_phone",
            "poc phone": "poc_phone",
            "it support": "it_support",
            "it contact": "it_support",
            "it phone": "it_phone",
            "notes": "notes",
            "notes/comments": "notes",
            "notes / comments": "notes",
        }

        # Required: these must exist in Excel
        required_normalized = {
            "area",
            "customer",
            "building",  # building OR bldg works
            "room",
            "serial_number",
            "model",
            "poc",
            "poc_phone",
            "it_support",
            "it_phone",
            "notes",
        }

        # Convert excel header names > internal field names
        mapped_internal_fields = set()
        for h in excel_headers:
            if h in header_map:
                mapped_internal_fields.add(header_map[h])

        # Check missing fields
        missing = sorted(required_normalized - mapped_internal_fields)
        if missing:
            QMessageBox.critical(
                self,
                "Import Error",
                "Missing required columns in Excel:\n" +
                "\n".join(f"- {m}" for m in missing)
            )
            wb.close()
            return

        # Step 3 – Import rows
        from core.models.equipment_model import EquipmentInfo
        added = 0
        for row in ws.iter_rows(min_row=2, values_only=True):
            if not any(row):
                continue  # skip empty rows
            row_dict = dict(zip(excel_headers, row))
            clean = {}

            # Convert each excel column to internal field name
            for excel_key, value in row_dict.items():
                if excel_key in header_map:
                    internal_key = header_map[excel_key]
                    clean[internal_key] = value

            clean["user"] = self.user
            EquipmentInfo.create(**clean)
            added += 1

        wb.close()

        # Reload UI
        self.load_items()

        QMessageBox.information(
            self,
            "Import Complete",
            f"Successfully imported {added} equipment records from '{sheet_name}'."
        )

    except Exception as e:
        QMessageBox.critical(self, "Import Error", f"An error occurred:\n{e}")