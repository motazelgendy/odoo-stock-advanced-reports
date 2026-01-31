from odoo import models


class StockCardEngine(models.AbstractModel):
    _name = "stock.card.engine"
    _description = "Stock Card SQL Engine"

    def get_rows(self, product_id, location_ids):
        query = """
            SELECT
                sml.id,
                sml.date,
                sml.product_id,
                sm.id AS move_id,
                sm.reference,
                sm.picking_id,

                CASE
                    WHEN sml.location_dest_id = ANY(%(loc_ids)s)
                    THEN sml.quantity ELSE 0
                END AS qty_in,

                CASE
                    WHEN sml.location_id = ANY(%(loc_ids)s)
                    THEN sml.quantity ELSE 0
                END AS qty_out,

                SUM(
                    CASE
                        WHEN sml.location_dest_id = ANY(%(loc_ids)s)
                            THEN sml.quantity
                        WHEN sml.location_id = ANY(%(loc_ids)s)
                            THEN -sml.quantity
                        ELSE 0
                    END
                ) OVER (
                    PARTITION BY sml.product_id
                    ORDER BY sml.date, sml.id
                ) AS balance

            FROM stock_move_line sml
            JOIN stock_move sm ON sm.id = sml.move_id

            WHERE sml.product_id = %(product_id)s
            AND sml.state = 'done'
            AND (
                sml.location_id = ANY(%(loc_ids)s)
                OR sml.location_dest_id = ANY(%(loc_ids)s)
            )

            ORDER BY sml.date, sml.id
        """

        self.env.cr.execute(query, {
            "product_id": product_id,
            "loc_ids": location_ids,
        })

        return self.env.cr.dictfetchall()
