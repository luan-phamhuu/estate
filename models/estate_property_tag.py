from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real estate property tag"

    name = fields.Char('Name', required=True, translate=True)