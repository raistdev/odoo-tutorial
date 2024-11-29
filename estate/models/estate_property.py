from dateutil.relativedelta import relativedelta

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare, float_is_zero


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Estate Property'
    _order = 'id desc'

    name = fields.Char("Title", required=True)
    description = fields.Text()
    postcode = fields.Char()
    date_availability = fields.Date(
        "Available From",
        copy=False,
        default=fields.Date.today() + relativedelta(months=3)
    )
    expected_price = fields.Float(required=True)
    selling_price = fields.Float(readonly=True, copy=False)
    bedrooms = fields.Integer()
    living_area = fields.Integer("Living Area (sqm)")
    facades = fields.Integer()
    garage = fields.Boolean()
    garden = fields.Boolean()
    garden_area = fields.Integer("Garden Area (sqm)")
    garden_orientation = fields.Selection(
        string="Orientation",
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ],
        help="Add an orientation."
    )
    total_area = fields.Integer(
        "Total Area (sqm)",
        compute='_compute_total_area',
        readonly=True
    )
    best_price = fields.Float(
        "Best Offer",
        compute='_compute_best_price',
        readonly=True
    )
    active = fields.Boolean(default=True)
    state = fields.Selection(
        string="Status",
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled')
        ],
        default='new'
    )
    # Many2one fields
    property_type_id = fields.Many2one(
        'estate.property.type',
        string="Property Type"
    )
    partner_id = fields.Many2one('res.partner', string="Buyer")
    user_id = fields.Many2one(
        'res.users',
        string="Salesman",
        default=lambda self: self.env.user
    )
    # Many2many fields
    tag_ids = fields.Many2many('estate.property.tag')
    # One2many fields
    offer_ids = fields.One2many('estate.property.offer', 'property_id')

    # SQL constraints
    _sql_constraints = [
        ('estate_property_check_expected_price', 'CHECK(expected_price > 0.0)',
         'Expected price must be positive!'),
        ('estate_property_check_selling_price', 'CHECK(selling_price > 0.0)',
         'Selling price must be positive!')
    ]

    # Compute fields
    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for rec in self:
            rec.total_area = rec.living_area + rec.garden_area

    @api.depends('offer_ids')
    def _compute_best_price(self):
        for rec in self:
            rec.best_price = max(
                rec.offer_ids.mapped('price')
                ) if rec.offer_ids else 0.0

    # Onchange field
    @api.onchange('garden')
    def _set_garden_values(self):
        for rec in self:
            rec.garden_area = 10 if rec.garden else 0
            rec.garden_orientation = 'north' if rec.garden else ''

    # Button actions
    def action_sold(self):
        for rec in self:
            if not rec.state == 'cancelled':
                rec.state = 'sold'
            else:
                raise UserError("You can't sell a cancelled property!")

    def action_cancel(self):
        for rec in self:
            if not rec.state == 'sold':
                rec.state = 'canceled'
            else:
                raise UserError("You can't cancel a sold property!")

    # Python constrains
    @api.constrains('selling_price')
    def _check_selling_price(self):
        for rec in self:
            if (
                not float_is_zero(rec.selling_price, precision_rounding=0.01)
                and float_compare(rec.selling_price, rec.expected_price *
                                  0.9, precision_rounding=0.01) <= 0
            ):
                raise ValidationError("Selling price must be at lest 90%",
                                      "of expected price")

    # Crud
    # ondelte record
    @api.ondelete(at_uninstall=False)
    def _unlink_if_not_new_or_cancelled(self):
        if any(property.state not in ['new', 'canceled']
                for property in self):
            raise UserError("Property state mustn't be",
                            " in sold or cancelled")
