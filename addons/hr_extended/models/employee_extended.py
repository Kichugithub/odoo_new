from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class EmployeeInherit(models.Model):
    _inherit = "hr.employee" 

    joining_date = fields.Date(string="Joining Date", required=True)

    experience = fields.Char(string="Experience",compute="computetheexperience",store=True,readonly=True)

    @api.depends('joining_date')
    def computetheexperience(self):
        for rec in self:
            if rec.joining_date:
               diff = relativedelta(fields.Date.today(), rec.joining_date)
               years = diff.years
               months = diff.months
               days = diff.days
               
               rec.experience = f"{years} year(s), {months} month(s), {days} day(s)"
               
            else:
                rec.experience = "0 year(s), 0 month(s), 0 day(s)"
