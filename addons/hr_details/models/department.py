from odoo import fields, models

class DepartmentModel(models.Model):
    _name = "department.model"
    _description = "Description Model"
    name = fields.Char(string='Add A Department', required=True) 