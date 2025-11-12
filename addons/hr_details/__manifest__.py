{
    'name': 'Student List', 
    'summary': 'Module to manage and list student information in Odoo 18',
    'description': '''
    Student Details Management
    ==========================
    This module helps manage student records within Odoo.

    **Features:**
    - Add new student records with personal details (Name, Age, Department, Roll Number, Email)
    - List and search students efficiently
    - Edit or delete existing student data
    - Simple and responsive form and list views
    - Easy integration with Odoo’s user access and security features

    **Use Case:**
    Perfect for schools, colleges, or training institutions to maintain structured student information in one place.
        ''',
    'version': '1.0',
    'category': 'Human Resources/Students Details',
    'license': 'LGPL-3', 
    'author': 'Krishnaveni J',
    'website': 'http://www.example.com',
    'depends': [
        'base',
    ],
    'data': [
        
        'security/ir.model.access.csv',
        'views/student_views.xml',
        'views/department_views.xml',
        
    ],
    
    'installable': True,
    'application': True,

}