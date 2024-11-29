from odoo import api, fields, models


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Property Type'
    _order = 'name'

    name = fields.Char("Property Type")
    property_ids = fields.One2many('estate.property', 'property_type_id')
    sequence = fields.Integer("Sequence", default=1, help="Used to order stages. Lower is better")
    offer_ids = fields.One2many(
        'estate.property.offer',
        'property_type_id'
    )
    offer_count = fields.Integer("offers", compute='_compute_offers_count')

    _sql_constraints = [
        ('estate_property_type_check_name', 'UNIQUE (name)',
         'Name must be unique!')
    ]

    def _compute_offers_count(self):
        for rec in self:
            rec.offer_count = len(rec.offer_ids) if rec.offer_ids else 0
