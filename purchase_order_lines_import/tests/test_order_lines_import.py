import xlrd

from odoo.tests.common import TransactionCase
from odoo.modules.module import get_module_resource


class PurchaseOrderLineImportTest(TransactionCase):
    def validate_file(self, file_name):
        file_path = get_module_resource(
            "purchase_order_lines_import", "order_line_file", file_name
        )
        workbook = xlrd.open_workbook(file_path)
        sheet = workbook.sheet_by_index(0)

        return self.env["purchase.order.lines.import"]._is_order_lines_file(sheet)

    def test_002_order_lines_file_validation(self):
        """
        Check order line file format validation works properly
        """

        self.assertTrue(self.validate_file("order_line_file.xlsx"))
        self.assertFalse(self.validate_file("bad_order_line_file.xlsx"))
