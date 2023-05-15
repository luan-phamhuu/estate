from datetime import timedelta
from odoo import api, fields, models

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real estate property offer"

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

    @api.depends('validity')
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.create_date:
                # convert record.create_date into Date type to be able to substract timedelta
                record.validity = (record.date_deadline - fields.Date.from_string(record.create_date)).days

    def action_accept(self):
        for record in self:
            record.status = 'accepted'
            record.property_id.state = 'sold'
            record.property_id.selling_price = record.price
            record.property_id.buyer_id = record.partner_id.id
        return True

    def action_refuse(self):
        for record in self:
            record.status = 'refused'
        return True