import base64
from datetime import datetime
import xlrd

from odoo import api, fields, models

from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PurchaseOrderLinesImport(models.TransientModel):
    _name = "purchase.order.lines.import"
    _description = "Import Order Lines"

    data_file = fields.Binary(
        string="Order Lines File", required=True, help="Get your order lines file here."
    )
    filename = fields.Char()

    @api.model
    def get_amount(self, string_amount):
        """
        returns the ammount without comma as float
        '13,567.76' --> 13567.76
        """

        return float(str(string_amount).replace(",", ""))

    @api.model
    def get_hashcode(self, default_code, name):
        """
        Receives:

        default_code --> ex: '82121511'
        and the description of the file as name --> ex: 'Mural Informativo Gestión de Calidad'

        returns a unique id from which each order line is identified
        regardless of whether the product is repeated or not ex:

        --> '82121511muralinformativogestiondecalidad'
        """
        repl = str.maketrans("áéúíó", "aeuio")
        return (default_code + name).lower().replace(" ", "").translate(repl)

    def _is_order_lines_file(self, sheet):
        """
        Gets the row in index 1 of file which is supposed to be the header line
        and checks whether all cells meet the expected header in the proper order.
        Else returns false if one fails to meet this standard.

        :param sheet:
        :return validation: boolean
        """
        header_row = [sheet.cell(1, col_idx).value for col_idx in range(0, sheet.ncols)]

        column_headers = {
            0: "Nivel",
            1: "Referencia",
            2: "Código UNSPSC",
            3: "Cuenta presupuestaria",
            4: "Descripción",
            5: "Cantidad",
            6: "Unidad",
            7: "Precio unitario estimado",
            8: "Precio total estimado",
            9: "Comentarios del comprador",
        }

        try:
            for c, col in enumerate(header_row):
                col = col.strip()
                if not col == column_headers[c]:
                    return False
            return True
        except (ValueError, IndexError):
            return False

    @api.model
    def read_file(self):
        """
        Opens the xlsx file and returns all the order lines
        as a list of dictionaries ex;

        [
            {'hashcode': '82121511certificadosdereconocimiento(evaluadoresppc-pnc.-ods,otros)',
            'default_code': '82121511', '
            name': 'Certificados de reconocimiento (Evaluadores PPC-PNC.-ODS, otros)',
            ...
            },
            ...
        ]
        """

        try:
            with open("/tmp/order_lines.xlsx", "wb") as w_file:
                w_file.write(base64.b64decode(self.data_file))

            with xlrd.open_workbook("/tmp/order_lines.xlsx") as data:
                sheet = data.sheet_by_index(0)
                lines = {}

                if not self._is_order_lines_file(sheet):
                    raise UserError(
                        "The file does not meet the proper standard structure"
                    )

                for row_idx in range(2, sheet.nrows):
                    row = [
                        sheet.cell(row_idx, col_idx).value
                        for col_idx in range(0, sheet.ncols)
                    ]

                    try:
                        hashcode = self.get_hashcode(row[2], row[4])
                        if hashcode not in lines:
                            lines[hashcode] = {
                                "default_code": row[2],
                                "name": row[4],
                                "product_qty": self.get_amount(row[5]),
                                "price_unit": self.get_amount(row[7]),
                            }

                    except IndexError:
                        continue

                if len(lines) == 0:
                    raise UserError("Could not read any order line")

                else:
                    return lines

        except xlrd.biffh.XLRDError:
            raise UserError("Error trying to open file as xlsx")

    @api.model
    def get_hashcodes(self, order_lines):
        """
        Iterates through all the purchase order lines
        and returns a dictionary. Each key is the hashcode
        of that order line and the value is the purchase.order.line
        object. ex:

        {
            '82121511muralinformativogestiondecalidad': purchase.order.line(4347,)
        }
        """

        lines = {}

        for line in order_lines:
            lines[self.get_hashcode(line.product_id.default_code, line.name)] = line

        return lines

    @api.model
    def get_name(self, product_id, name):
        """
        returns the concatenation of the name of the product and the description
        in the file ex: '[Brochures CAF] Mural Informativo Gestión de Calidad'
        """

        return "[" + product_id.name + "] " + name

    @api.model
    def sort_lines(self, order_lines, file_lines):
        """
        Evaluate if there is any order line already
        created that matches the hashcode
            in which case updates its values.

        Tries to get the product base on the internal reference and
        then creates a dictionary in case the order line does not exists.

        if the product with this internal reference is not found an string
        with the line, internal reference(not found), the description,
        the error and a sugestion is appended to the error lines list

        returns the order lines to be added
        ex:

        [
            {'name': 'Nuevo Nombre',
            'date_planned': datetime.datetime(2020, 3, 25, 20, 13, 39) ...},
            ...
        ]

        returns a list of strings with the error lines:
        line, internal reference (product not found), description in file, error,
        recommendation
        ex:

        [
            '48, 14111604, Tarjetas de presentación Ministro, Product not found,
            Create the product with the internal reference',
            ...
        ]
        """

        error_lines = []
        add_lines = {}
        product_product = self.env["product.product"]
        dt = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        for i, fl in enumerate(file_lines):
            values = file_lines[fl]

            if fl in order_lines:

                order_line = order_lines[fl]

                if order_line.product_qty != values["product_qty"]:
                    order_line.product_qty = values["product_qty"]

                if order_line.price_unit != values["price_unit"]:
                    order_line.price_unit = values["price_unit"]

            elif fl not in add_lines:
                # TODO: get values from methods in order lines model

                product_id = product_product.search(
                    [("default_code", "=", values["default_code"])]
                )

                if product_id:
                    product_id = product_id[0]
                    del values["default_code"]
                    values.update(
                        {
                            "product_id": product_id.id,
                            # 'name': self.get_name(product_id, values['name']),
                            "product_uom": product_id.uom_po_id.id
                            or product_id.uom_id.id,
                            "date_planned": dt,
                        }
                    )

                    add_lines[fl] = values

                else:
                    message = (
                        "{}, {}, {}, Product not found, "
                        "Create the product with the internal reference".format(
                            str(i + 3), values["default_code"], values["name"]
                        )
                    )

                    error_lines.append(message)

        return add_lines, error_lines

    def get_errors_file(self, error_lines):
        """
        Creates and returns the attachment object
        with the error file generaret from the list
        of error lines.
        """

        dt = fields.Datetime.to_string(fields.Datetime.now())
        file_name = "purchase order log " + dt + ".txt"

        with open("/tmp/" + file_name, "w") as w_file:
            for line in error_lines:
                w_file.write(line + "\n")

        with open("/tmp/" + file_name, "rb") as r_file:
            # attachment = self.env["ir.attachment"].create(
            #     {
            #         "datas": base64.b64encode(r_file.read()),
            #         "name": file_name,
            #         "datas_fname": file_name,
            #     }
            # )
            attachment = self.env["ir.attachment"].create(
                {
                    "name": file_name,
                    "datas": base64.b64encode(r_file.read()),
                    "type": "binary",
                    "res_model": self._name,
                    "res_id": self.id,
                }
            )

            return attachment

    def create_message(self, error_lines, purchase_order_id):
        """
        Posts an internal note indicating that some
        errors ocurred during the file import
        along with the attachment of the file
        containing the details.
        """

        attachment = self.get_errors_file(error_lines)
        body = "Some errors ocurred during the file import, see file for details"

        purchase_order_id.message_post(body=body, attachment_ids=[attachment.id])

    def import_file(self):
        self.ensure_one()
        """
            Process the file chosen in the wizard, replaces all order
            lines with the updated ones, new ones and old ones.

            Call the create message method to post the message and the
            attachment with the corresponding erros if there are any.
        """

        active_id = self.env.context.get("active_id")
        if not active_id:
            raise UserError("active_id not found")

        purchase_order_id = self.env["purchase.order"].browse(active_id)
        order_lines_hardcoded = self.get_hashcodes(purchase_order_id.order_line)
        file_lines = self.read_file()
        add_lines, error_lines = self.sort_lines(order_lines_hardcoded, file_lines)

        if add_lines:
            purchase_order_id.order_line = [(0, 0, line) for line in add_lines.values()]

        if error_lines:
            self.create_message(error_lines, purchase_order_id)
