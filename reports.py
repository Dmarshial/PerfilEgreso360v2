"""
Exportación de reportes a Excel. Los reportes se agrupan bajo un único
módulo "Reportes" en la app en vez de aparecer dispersos en el menú.
"""

import io
import pandas as pd


def exportar_excel(hojas: dict) -> bytes:
    """Recibe un dict {nombre_hoja: DataFrame} y devuelve los bytes de un
    archivo .xlsx con una hoja por elemento."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        for nombre, df in hojas.items():
            df.to_excel(writer, sheet_name=nombre[:31], index=False)
    buffer.seek(0)
    return buffer.getvalue()
