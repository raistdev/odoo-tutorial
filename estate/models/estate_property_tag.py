from odoo import fields, models, api


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Property Tag'
    _order = 'name'

    name = fields.Char("Property Tag", required=True)
    color = fields.Integer()

    _sql_constraints = [
        ('state_property_tag_check_name', 'UNIQUE (name)',
         'Name must be unique!')
    ]
