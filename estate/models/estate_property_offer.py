from dateutil.relativedelta import relativedelta
from odoo import fields, models, api
from odoo.exceptions import UserError
from odoo.tools import float_compare


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Property Offer'
    _order = 'price desc'

    price = fields.Float()
    status = fields.Selection(
        string="Status",
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused')
        ],
        copy=False
    )
    partner_id = fields.Many2one('res.partner', required=True)
    property_id = fields.Many2one('estate.property', required=True)
    validity = fields.Integer("Validity (days)", default=7)
    date_deadline = fields.Date(
        "Deadline",
        compute='_compute_offer_date',
        inverse='_inverse_offer_date'
    )
    property_type_id = fields.Many2one(
        'estate.property.type',
        related='property_id.property_type_id',
        store=True
    )

    # SQL constraints
    _sql_constraints = [
        ('estate_property_offer_check_price', 'CHECK(price > 0.0)',
         'Price must be positive!')
    ]

    # Compute and inverse methods
    @api.depends('create_date', 'validity')
    def _compute_offer_date(self):
        for rec in self:
            date = rec.create_date.date() if rec.create_date else fields.Date.today()
            rec.date_deadline = date + relativedelta(days=rec.validity)

    def _inverse_offer_date(self):
        for rec in self:
            date = rec.create_date.date() if rec.create_date else fields.Date.today()
            rec.validity = (rec.date_deadline - date).days

    # Button actions
    def action_accept(self):
        if self.property_id.selling_price:
            raise UserError("An offer has been accepted.")
        for rec in self:
            if not rec.status:
                rec.status = 'accepted'
                rec.property_id.partner_id = rec.partner_id
                rec.property_id.selling_price = rec.price
        return True

    def action_refuse(self):
        for rec in self:
            if not rec.status:
                rec.status = 'refused'
        return True

    # Crud methods
    @api.model_create_multi
    def create(self, vals):
        if vals.get('property_id') and vals['price']:
            prop = self.env['estate.property'].browse(vals['property_id'])
            if prop.offer_ids:
                max_offer = max(prop.mapped("offer_ids.price"))
                if float_compare(vals['price'], max_offer, precision_rounding=0.01) <= 0:
                    raise UserError("The offer must be higher than {:.2f}".format(max_offer))
            else:
                prop.state = 'offer_received'
        return super().create(vals)
