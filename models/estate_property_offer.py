from datetime import timedelta
from odoo import api, fields, models, exceptions

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real estate property offer"
    _order = "price desc"


    price = fields.Float('Price', required=True)
    status = fields.Selection(
        string="Status",
        copy=False,
        selection=[
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
            record.status = 'accepted'
            record.property_id.state = 'offer_accepted'
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id.id
        return True

    def action_refuse(self):
        for record in self:
            record.status = 'refused'
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