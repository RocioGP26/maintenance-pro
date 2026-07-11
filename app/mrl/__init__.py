"""
Maintix Report Language (MRL) · Sprint 15.1 Foundation.

API pública del núcleo de estilos y metadata. Los motores Excel/PDF
(ExcelExporter, PdfExporter) se añaden en Sprint 15.2 y 15.3.
"""

from app.mrl import colors
from app.mrl import constants
from app.mrl import typography
from app.mrl.constants import MRL_VERSION
from app.mrl.excel.exporter import BaseExcelExporter, ExcelExporter
from app.mrl.metadata import MRLDocumentMeta, build_sample_metadata
from app.mrl.styles import MRLStyle

__all__ = [
    "MRL_VERSION",
    "MRLDocumentMeta",
    "MRLStyle",
    "BaseExcelExporter",
    "ExcelExporter",
    "build_sample_metadata",
    "colors",
    "constants",
    "typography",
]
