from odoo import http
from odoo.http import request
import jwt
import datetime
from dotenv import load_dotenv
import os
from .auth_utils import token_required
import json

class EmployeeController(http.Controller):
    @http.route('/api/employee/create', type='http', auth='user', methods=['POST'], csrf=False)
    @token_required
    def create_employee(self, **kwargs):
        try:
            # Parse raw JSON body
            raw_data = request.httprequest.data
            if not raw_data:
                return  http.Response(
                        response=json.dumps({
                            'status': 'error',
                            'message': 'Missing request body'
                        }),
                        status=400,
                        content_type='application/json'
                    )

            data = json.loads(raw_data.decode('utf-8'))
            name = data.get('name')
            job_title = data.get('job_title')
            department_id = data.get('department_id')
            joining_date = data.get('joining_date')

            if not name:
                return  http.Response(
                        response=json.dumps({
                            'status': 'error',
                            'message': 'Employee name is required'
                        }),
                        status=400,
                        content_type='application/json'
                    )
            if not job_title:
                return  http.Response(
                        response=json.dumps({
                            'status': 'error',
                            'message': 'Job title is required'
                        }),
                        status=400,
                        content_type='application/json'
                    )

            employee = request.env['hr.employee'].sudo().create({
                'name': name,
                'job_title': job_title,
                'department_id': department_id,
                'joining_date': joining_date,
            })

            return  http.Response(
                    response=json.dumps({
                        'status': 'success',
                        'employee_id': employee.id
                    }),
                    status=201,
                    content_type='application/json'
                )
        except Exception as e:
            return  http.Response(
                    response=json.dumps({
                        'status': 'error',
                        'message': str(e)
                    }),
                    status=500,
                    content_type='application/json'
                )
        
    @http.route('/api/employee/list', type='http', auth='user', methods=['GET'], csrf=False)
    @token_required
    def get_employee_list(self, **kwargs):
        try:
            employees = request.env['hr.employee'].sudo().search([])
            employee_list = []
            for emp in employees:
                employee_list.append({
                    'id': emp.id,
                    'name': emp.name,
                    'job_title': emp.job_title,
                    'department_id': emp.department_id.id,
                    'joining_date': emp.joining_date.isoformat()
                })

            return  http.Response(
                    response=json.dumps({
                        'status': 'success',
                        'employees': employee_list
                    }),
                    status=200,
                    content_type='application/json'
                )
            

        except Exception as e:
            return  http.Response(
                    response=json.dumps({
                        'status': 'error',
                        'message': str(e)
                    }),
                    status=500,
                    content_type='application/json'
                )



load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "default_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = float(os.getenv("JWT_EXPIRATION_MINUTES", "0.35"))
REFRESH_EXP = int(os.getenv("REFRESH_EXP", "1440"))  # Default 24 hours 

class AuthController(http.Controller):

    @http.route('/api/login', type='http', auth='none', methods=['POST'], csrf=False)
    def api_login(self, **kwargs):
        try:
            # Parse raw JSON body
            raw_data = request.httprequest.data
            if not raw_data:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Missing request body'}),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            data = json.loads(raw_data.decode('utf-8'))
            username = data.get('username')
            password = data.get('password')

            # Validate input
            if not username or not password:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Username and password required'}),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )
            
            dbname = request.session.db

            uid = request.session.authenticate(dbname, {
                "login": username,
                "password": password,
                "type": "password"
            })

            if not uid:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Invalid credentials'}),
                    headers=[('Content-Type', 'application/json')],
                    status=401
                )

            access_payload = {
                'userid': uid,
                'login': username,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=JWT_EXPIRATION_MINUTES)
            }
            access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

            refresh_payload = {
                'userid': uid,
                'login': username,
                'type': 'refresh',
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=REFRESH_EXP)
            }

            refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

        
            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'access_token': access_token,
                    'refresh_token': refresh_token,
                    'user_id': uid,
                    'access_expires_in': f"{JWT_EXPIRATION_MINUTES} minutes",
                    'referesh_expires_in': f"{REFRESH_EXP} minutes"
}),
                headers=[('Content-Type', 'application/json')],
                status=200
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )

        
    @http.route('/api/token/refresh', type='http', auth='none', methods=['POST'], csrf=False)
    def refresh_token(self, **kwargs):
        try:
            
            raw_data = request.httprequest.data
            if not raw_data:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Missing request body'}),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            data = json.loads(raw_data.decode('utf-8'))
            refresh_token = data.get('refresh_token')

            if not refresh_token:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Refresh token missing'}),
                    headers=[('Content-Type', 'application/json')],
                    status=400
                )

            # Decode and verify refresh token
            try:
                payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            except jwt.ExpiredSignatureError:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Refresh token has expired'}),
                    headers=[('Content-Type', 'application/json')],
                    status=401
                )
            except jwt.InvalidTokenError:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Invalid refresh token'}),
                    headers=[('Content-Type', 'application/json')],
                    status=401
                )

            # Ensure this is a refresh token
            if payload.get('type') != 'refresh':
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Token is not a refresh token'}),
                    headers=[('Content-Type', 'application/json')],
                    status=401
                )

            uid = payload.get('userid')
            username = payload.get('login')

            if not uid or not username:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Invalid token payload'}),
                    headers=[('Content-Type', 'application/json')],
                    status=401
                )

            # Generate new access token
            access_payload = {
                'userid': uid,
                'login': username,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=JWT_EXPIRATION_MINUTES)
            }
            new_access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

            # Return tokens
            return request.make_response(
                json.dumps({
                    'status': 'success',
                    'access_token': new_access_token,
                    'access_expires_in': f"{JWT_EXPIRATION_MINUTES} minutes",
                }),
                headers=[('Content-Type', 'application/json')],
                status=200
            )

        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')],
                status=500
            )
