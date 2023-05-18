from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real estate property type"
    _order = "sequence, name"

    name = fields.Char('Type', required=True, translate=True)
    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    sequence = fields.Integer('Sequence', default=1)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Type name already exists !')
    ]