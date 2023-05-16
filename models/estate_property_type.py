from odoo import fields, models

class EstatePropertyType(models.Model):
    _name = "estate.property.type"
    _description = "Real estate property type"

    name = fields.Char('Type', required=True, translate=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Type name already exists !')
    ]