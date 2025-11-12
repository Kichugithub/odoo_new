{
    'name': 'Employees Extended',
    'summary': 'Extends the Odoo HR Employee module with extra fields like Joining Date and Experience',
    'description': """
Employee Extended Module
=========================
This module extends Odoo's HR Employee model by adding new fields such as Joining Date and Experience.
""",
    'version': '1.0',
    'author': 'Krishnaveni J',
    'category': 'Human Resources',
    'website': 'http://www.example.com',
    'license': 'LGPL-3',
    'depends': ['base', 'hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_extended_views.xml',
    ],
    'installable': True,
    'application': True,
}
