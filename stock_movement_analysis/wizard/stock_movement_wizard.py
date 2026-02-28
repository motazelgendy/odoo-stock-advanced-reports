from odoo import models, fields, api
from odoo.exceptions import ValidationError


class StockMovementAnalysisWizard(models.TransientModel):
    _name = "stock.movement.analysis.wizard"
    _description = "Stock Movement Analysis Wizard"

    product_id = fields.Many2one("product.product")
    categ_id = fields.Many2one("product.category")
    warehouse_id = fields.Many2one("stock.warehouse")
    location_id = fields.Many2one("stock.location")

    company_id = fields.Many2one(
        "res.company",
        required=True,
        default=lambda self: self.env.company
    )

    date_start = fields.Datetime(required=True)
    date_end = fields.Datetime(required=True)

    # --------------------------
    # Constraints
    # --------------------------

    @api.constrains("warehouse_id", "location_id")
    def _check_scope(self):
        for rec in self:
            if rec.warehouse_id and rec.location_id:
                raise ValidationError("You cannot select both Warehouse and Location.")

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for rec in self:
            if rec.date_start > rec.date_end:
                raise ValidationError("Start Date must be before End Date.")

    # --------------------------
    # Scope Resolver
    # --------------------------

    def _get_scope_location_ids(self):
        self.ensure_one()
        Location = self.env["stock.location"]

        domain = [
            ("company_id", "in", [False, self.company_id.id])
        ]

        if self.location_id:
            domain.append(("id", "child_of", self.location_id.id))
        elif self.warehouse_id:
            domain.append(("id", "child_of", self.warehouse_id.view_location_id.id))
        else:
            domain += [
                ("usage", "=", "internal"),
                ("company_id", "=", self.company_id.id),
            ]

        locations = Location.search(domain)
        return locations.ids

    # --------------------------
    # Fetch Moves
    # --------------------------

    def _fetch_move_lines(self, scope_ids):
        domain = [
            ("state", "=", "done"),
            ("qty_done", "!=", 0),
            ("company_id", "=", self.company_id.id),
            ("date", "<=", self.date_end),
            "|",
            ("location_id", "in", scope_ids),
            ("location_dest_id", "in", scope_ids),
        ]

        if self.product_id:
            domain.append(("product_id", "=", self.product_id.id))

        if self.categ_id:
            domain.append(("product_id.categ_id", "child_of", self.categ_id.id))

        return self.env["stock.move.line"].search(domain)

    # --------------------------
    # Aggregation
    # --------------------------

    def _init_bucket(self):
        return {
            "opening": 0.0,
            "purchase": 0.0,
            "purchase_return": 0.0,
            "sales": 0.0,
            "sales_return": 0.0,
            "production": 0.0,
            "unbuild": 0.0,
            "adjustment_in": 0.0,
            "adjustment_out": 0.0,
            "other_inventory_in": 0.0,
            "other_inventory_out": 0.0,
            "internal_in": 0.0,
            "internal_out": 0.0,
            "transit_in": 0.0,
            "transit_out": 0.0,
            "view_in": 0.0,
            "view_out": 0.0,
        }

    def _aggregate_moves(self, move_lines, scope_ids):
        result = {}
        scope_set = set(scope_ids)

        for line in move_lines:

            if line.location_id.id in scope_set and line.location_dest_id.id in scope_set:
                continue

            product_id = line.product_id.id

            if product_id not in result:
                result[product_id] = self._init_bucket()

            bucket = result[product_id]

            if line.location_dest_id.id in scope_set:
                direction = "in"
                opposite_location = line.location_id
            else:
                direction = "out"
                opposite_location = line.location_dest_id

            # Opening
            if line.date < self.date_start:
                if direction == "in":
                    bucket["opening"] += line.qty_done
                else:
                    bucket["opening"] -= line.qty_done
                continue

            usage = opposite_location.usage
            qty = line.qty_done

            if usage == "supplier":
                if direction == "in":
                    bucket["purchase"] += qty
                else:
                    bucket["purchase_return"] += qty

            elif usage == "customer":
                if direction == "out":
                    bucket["sales"] += qty
                else:
                    bucket["sales_return"] += qty

            elif usage == "production":
                if direction == "in":
                    bucket["production"] += qty
                else:
                    bucket["unbuild"] += qty

            elif usage == "inventory":
                if opposite_location == line.product_id.property_stock_inventory:
                    if direction == "in":
                        bucket["adjustment_in"] += qty
                    else:
                        bucket["adjustment_out"] += qty
                else:
                    if direction == "in":
                        bucket["other_inventory_in"] += qty
                    else:
                        bucket["other_inventory_out"] += qty

            elif usage == "internal":
                if direction == "in":
                    bucket["internal_in"] += qty
                else:
                    bucket["internal_out"] += qty

            elif usage == "transit":
                if direction == "in":
                    bucket["transit_in"] += qty
                else:
                    bucket["transit_out"] += qty

            else:
                if direction == "in":
                    bucket["view_in"] += qty
                else:
                    bucket["view_out"] += qty

        return result

    # --------------------------
    # Build Report
    # --------------------------

    def _build_report(self, aggregation):
        Report = self.env["stock.movement.analysis.report"]

        Report.search([("wizard_id", "=", self.id)]).unlink()

        lines = []

        for product_id, data in aggregation.items():

            total_period = sum(v for k, v in data.items() if k != "opening")

            if not data["opening"] and not total_period:
                continue

            closing = data["opening"] + (
                data["purchase"]
                - data["purchase_return"]
                - data["sales"]
                + data["sales_return"]
                + data["production"]
                - data["unbuild"]
                + data["adjustment_in"]
                - data["adjustment_out"]
                + data["other_inventory_in"]
                - data["other_inventory_out"]
                + data["internal_in"]
                - data["internal_out"]
                + data["transit_in"]
                - data["transit_out"]
                + data["view_in"]
                - data["view_out"]
            )

            vals = {
                "wizard_id": self.id,
                "product_id": product_id,
                "opening_qty": data["opening"],
                "closing_qty": closing,
                "purchase_qty": data["purchase"],
                "purchase_return_qty": data["purchase_return"],
                "sales_qty": data["sales"],
                "sales_return_qty": data["sales_return"],
                "production_qty": data["production"],
                "unbuild_qty": data["unbuild"],
                "adjustment_in_qty": data["adjustment_in"],
                "adjustment_out_qty": data["adjustment_out"],
                "other_inventory_in_qty": data["other_inventory_in"],
                "other_inventory_out_qty": data["other_inventory_out"],
                "internal_in_qty": data["internal_in"],
                "internal_out_qty": data["internal_out"],
                "transit_in_qty": data["transit_in"],
                "transit_out_qty": data["transit_out"],
                "view_in_qty": data["view_in"],
                "view_out_qty": data["view_out"],
            }

            lines.append(vals)

        Report.create(lines)

    # --------------------------
    # Main Action
    # --------------------------

    def action_generate_report(self):
        self.ensure_one()

        scope_ids = self._get_scope_location_ids()
        moves = self._fetch_move_lines(scope_ids)
        aggregation = self._aggregate_moves(moves, scope_ids)
        self._build_report(aggregation)

        return {
            "type": "ir.actions.act_window",
            "name": "Stock Movement Analysis",
            "res_model": "stock.movement.analysis.report",
            "view_mode": "tree,pivot",
            "domain": [("wizard_id", "=", self.id)],
        }