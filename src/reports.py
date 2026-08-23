"""Exportación de reportes."""
from __future__ import annotations

from io import BytesIO
import pandas as pd


def exportar_excel(hojas: dict[str, pd.DataFrame]) -> bytes:
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="xlsxwriter") as writer:
        wb = writer.book
        fmt_header = wb.add_format({"bold": True, "bg_color": "#101820", "font_color": "#FFFFFF", "border": 0})
        fmt_pct = wb.add_format({"num_format": "0.0"})
        for nombre, df in hojas.items():
            sheet = str(nombre)[:31] or "Reporte"
            safe = df.copy() if df is not None else pd.DataFrame()
            safe.to_excel(writer, sheet_name=sheet, index=False, startrow=1)
            ws = writer.sheets[sheet]
            ws.freeze_panes(2, 0)
            ws.autofilter(1, 0, max(1, len(safe) + 1), max(0, len(safe.columns) - 1))
            for c, col in enumerate(safe.columns):
                ws.write(1, c, col, fmt_header)
                width = min(42, max(12, len(str(col)) + 2,
                                    safe[col].astype(str).map(len).max() + 2 if len(safe) else 12))
                ws.set_column(c, c, width)
            ws.write(0, 0, "PerfilEgreso 360")
    return bio.getvalue()
