from odoo import models, fields


class StockCardWizard(models.TransientModel):
    _name = "stock.card.wizard"
    _description = "Stock Card Wizard"

    product_id = fields.Many2one(
        "product.product",
        required=True
    )

    location_id = fields.Many2one(
        "stock.location",
        required=True
    )

    date_from = fields.Datetime()
    date_to = fields.Datetime()

    def action_load(self):
        self.ensure_one()

        # =========================
        # location hierarchy
        # =========================
        loc_ids = self.env["stock.location"].search([
            ("id", "child_of", self.location_id.id)
        ]).ids

        # =========================
        # SQL engine call
        # =========================
        rows = self.env["stock.card.engine"].get_rows(
            self.product_id.id,
            loc_ids
        )

        # =========================
        # opening balance
        # =========================
        opening_balance = 0

        if self.date_from:
            before_rows = [
                r for r in rows
                if r["date"] and r["date"] < self.date_from
            ]
            if before_rows:
                opening_balance = before_rows[-1]["balance"]

        # =========================
        # date filtering (ORM layer)
        # =========================
        filtered_rows = [
            r for r in rows
            if (not self.date_from or (r["date"] and r["date"] >= self.date_from))
            and (not self.date_to or (r["date"] and r["date"] <= self.date_to))
        ]

        # =========================
        # clear previous result lines
        # =========================
        report_line_model = self.env["stock.card.report.line"]

        report_line_model.search([
            ("wizard_id", "=", self.id)
        ]).unlink()

        # =========================
        # optional opening balance row
        # =========================
        create_vals = []

        if self.date_from:
            create_vals.append({
                "wizard_id": self.id,
                "date": self.date_from,
                "reference": "Opening Balance",
                "qty_in": 0,
                "qty_out": 0,
                "balance": opening_balance,
            })

        # =========================
        # create report rows
        # =========================
        for r in filtered_rows:
            create_vals.append({
                "wizard_id": self.id,
                "date": r["date"],
                "reference": r["reference"],
                "move_id": r["move_id"],
                "qty_in": r["qty_in"],
                "qty_out": r["qty_out"],
                "balance": r["balance"],
            })

        if create_vals:
            report_line_model.create(create_vals)

        # =========================
        # open result tree view
        # =========================
        return {
            "type": "ir.actions.act_window",
            "name": "Stock Card",
            "res_model": "stock.card.report.line",
            "view_mode": "tree",
            "domain": [("wizard_id", "=", self.id)],
            "target": "current",
        }
