from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real estate property tag"
    _order = "name"

    name = fields.Char('Name', required=True, translate=True)
    color = fields.Integer('Color')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Tag name already exists !')
    ]