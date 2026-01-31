from odoo import models, fields


class StockCardReportLine(models.TransientModel):
    _name = "stock.card.report.line"
    _description = "Stock Card Report Line"
    _order = "date, id"

    wizard_id = fields.Many2one("stock.card.wizard")

    date = fields.Datetime()
    reference = fields.Char()

    move_id = fields.Many2one("stock.move")

    qty_in = fields.Float()
    qty_out = fields.Float()
    balance = fields.Float()
