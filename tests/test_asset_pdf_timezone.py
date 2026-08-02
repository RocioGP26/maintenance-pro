from datetime import datetime, timezone
from types import SimpleNamespace
import unittest

from app.maintenance.asset_life_pdf import _generated_timestamp


class AssetPdfTimezoneTest(unittest.TestCase):
    def test_generated_timestamp_uses_company_timezone(self):
        empresa = SimpleNamespace(zona_horaria="America/Bogota", pais="Colombia")
        generated_at = datetime(2026, 8, 2, 2, 37, tzinfo=timezone.utc)

        self.assertEqual(
            _generated_timestamp(empresa, generated_at),
            "01/08/2026 21:37",
        )


if __name__ == "__main__":
    unittest.main()
