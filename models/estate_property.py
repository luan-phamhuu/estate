from odoo import api, fields, models, exceptions, tools
from odoo.tools import date_utils

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real estate property"
    _order = "id desc"

    name = fields.Char('Title', required=True, translate=True)
    description = fields.Text('Description')
    postcode = fields.Char('Postcode')
    date_availability = fields.Date('Date Availability', copy=False, default=lambda self: date_utils.add(fields.Date.today(), months=3))
    expected_price = fields.Float('Expected Price', required=True)
    selling_price = fields.Float('Selling Price', readonly=True, copy=False)
    bedrooms = fields.Integer('Bedrooms', default=2)
    living_area = fields.Integer('Living Area (sqm)')
    facades = fields.Integer('Facades')
    garage = fields.Boolean('Garage')
    garden = fields.Boolean('Garden')
    garden_area = fields.Integer('Garden Area (sqm)')
    garden_orientation = fields.Selection(
        string='Garden Orientation',
        selection=[
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West'),
        ],
        help="Orientation can be choosen among North, South, East and West",
    )
    active = fields.Boolean('Active', default=True)
    state = fields.Selection(
        string='Status',
        required=True,
        copy=False,
        default='new',
        selection=[
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('canceled', 'Canceled'),

        ]
    )
    property_type_id = fields.Many2one("estate.property.type", string="Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    seller_id = fields.Many2one("res.users", string="Salesman", default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    total_area = fields.Integer('Total Area (sqm)', compute='_compute_total_area')
    best_price = fields.Float('Best Price', compute='_compute_best_price')

    _sql_constraints = [
        ('check_expected_price', 'CHECK(expected_price > 0)', 'The expected price must be greater than 0'),
        ('check_selling_price', 'CHECK(selling_price >= 0)', 'The selling price must be greater than 0'),
    ]

    @api.depends('living_area', 'garden_area')
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area
    
    @api.depends('offer_ids.price')
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped('price'))
            else:
                record.best_price = 0

    @api.onchange('garden')
    def _onchange_garden(self):
        # if garden is False, set garden_area to 0 and garden_orientation to empty
        # if garden is True, set garden_area to 100 and garden_orientation to north
        if not self.garden:
            self.garden_area = 0
            self.garden_orientation = ''
        else:
            self.garden_area = 100
            self.garden_orientation = 'north'

    def action_sell(self):
        for record in self:
            if self.state == 'canceled':
                raise exceptions.UserError('Canceled properties cannot be sold')
            self.state = 'sold'
        
        return True


    def action_cancel(self):
        for record in self:
            if self.state == 'sold':
                raise exceptions.UserError('Sold properties cannot be canceled')
            self.state = 'canceled'

        return True
    
    @api.constrains('selling_price', 'expected_price')
    def _check_selling_price(self):
        for record in self:
            if not(tools.float_is_zero(record.selling_price, precision_digits=2)) and tools.float_utils.float_compare(record.selling_price, record.expected_price * 0.9, precision_digits=2) == -1:
                raise exceptions.ValidationError('The selling price cannot be lower than 90% of the expected price')

    def unlink(self):
        for record in self:
            if record.state != 'new' and record.state != 'canceled':
                raise exceptions.UserError('You cannot delete a property that is not new or canceled')

        return super().unlink(self)