from datetime import timedelta
from odoo import api, fields, models, exceptions

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real estate property offer"
    _order = "price desc"


    price = fields.Float('Price', required=True)
    state = fields.Selection(
        string="Status",
        copy=False,
        default='new',
        selection=[
            ('new', 'New'),
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
    )
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    validity = fields.Integer('Validity (days)', default=7)
    date_deadline = fields.Date('Deadline', compute='_compute_date_deadline', inverse='_inverse_date_deadline')

    _sql_constraints = [
        ('check_price', 'CHECK(price > 0)', 'The price must be strictly positive'),
    ]

    @api.depends('validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = fields.Date.from_string(record.create_date + timedelta(days=record.validity))

    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date and record.date_deadline:
                record.validity = (record.date_deadline - fields.Date.from_string(record.create_date)).days

    def action_accept(self):
        for record in self:
            record.state = 'accepted'
            record.property_id.state = 'offer_accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id.id
        return True

    def action_refuse(self):
        for record in self:
            record.state = 'refused'

            # build a set of property's offers state
            # if there is an accepted offer, then the property state is 'offer_accepted'
            # if there is not accepted offer, and there are still 'new' offer, then the property state is 'offer_received'
            # if there is not accepted offer, and there is no 'new' offer, then the property state is 'new'
            offer_states = set(record.property_id.offer_ids.mapped('state'))
            if 'accepted' in offer_states:
                record.property_id.state = 'offer_accepted'
            elif 'new' in offer_states:
                record.property_id.state = 'offer_received'
                record.property_id.selling_price = 0
                record.property_id.buyer_id = False
            else:
                record.property_id.state = 'new'
                record.property_id.selling_price = 0
                record.property_id.buyer_id = False

        return True

    @api.model
    def create(self, vals):
        property_id = vals.get('property_id')
        property = self.env['estate.property'].browse(property_id)

        # raise an error if the current offer price is lower than all the existing offers price
        if property.offer_ids and vals.get('price') < max(property.offer_ids.mapped('price')):
            raise exceptions.UserError('The offer price is lower than the existing offers price')

        res = super().create(vals)
        res.property_id.state = 'offer_received'
        return res