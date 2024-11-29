from odoo import Command, models


class EstateProperty(models.Model):
    _inherit = 'estate.property'

    # Theoretically, this inherited function would need the @api.model 
    # decorator, although the only way it works is if you remove it.
    def action_sold(self):
        journal_id = self.env['account.journal'].search(
            [('type', '=', 'sale')], limit=1
        )
        for prop in self:
            self.env['account.move'].create(
                {
                    'partner_id': prop.partner_id.id,
                    'journal_id': journal_id.id,
                    'move_type': 'out_invoice',
                    'line_ids': [
                        Command.create(
                            {
                                'name': prop.name,
                                'quantity': 1,
                                'price_unit': prop.selling_price * 0.06
                            }
                        ),
                        Command.create(
                            {
                                'name': "Administrative fees",
                                'quantity': 1.0,
                                'price_unit': 100.0
                            }
                        )
                    ]
                }
            )
        return super().action_sold()
