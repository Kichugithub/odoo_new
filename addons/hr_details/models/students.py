from odoo import fields, models

class TestModel(models.Model):
    _name = "student.model"
    _description = "Test Model"
    name = fields.Char(string='Name', required=True)
    class_feild = fields.Char(string='Class', required=True)
    age = fields.Integer(string='Age', required=True)
    phone = fields.Char(string='Phone', required=True)
    school = fields.Char(string='School', required=True)
    image_1920 = fields.Image(string="Student Image") 
    department_id = fields.Many2one('department.model', string='Department')