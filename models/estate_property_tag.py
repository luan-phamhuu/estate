from odoo import fields, models

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Real estate property tag"

    name = fields.Char('Name', required=True, translate=True)

    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Tag name already exists !')
    ]