from odoo import models, fields


class StockMovementAnalysisReport(models.TransientModel):
    _name = "stock.movement.analysis.report"
    _description = "Stock Movement Analysis Report"
    _order = "product_id"

    wizard_id = fields.Many2one(
        "stock.movement.analysis.wizard",
        ondelete="cascade"
    )

    product_id = fields.Many2one("product.product", required=True)
    categ_id = fields.Many2one(
        related="product_id.categ_id",
        store=True
    )

    uom_id = fields.Many2one(
        related="product_id.uom_id",
        store=True
    )

    opening_qty = fields.Float()
    closing_qty = fields.Float()

    purchase_qty = fields.Float()
    purchase_return_qty = fields.Float()

    sales_qty = fields.Float()
    sales_return_qty = fields.Float()

    production_qty = fields.Float()
    unbuild_qty = fields.Float()

    adjustment_in_qty = fields.Float()
    adjustment_out_qty = fields.Float()
    other_inventory_in_qty = fields.Float()
    other_inventory_out_qty = fields.Float()

    internal_in_qty = fields.Float()
    internal_out_qty = fields.Float()

    transit_in_qty = fields.Float()
    transit_out_qty = fields.Float()

    view_in_qty = fields.Float()
    view_out_qty = fields.Float()