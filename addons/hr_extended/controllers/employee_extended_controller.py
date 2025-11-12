from odoo import http
from odoo.http import request
import jwt
import datetime
import secrets
from dotenv import load_dotenv
import os
from odoo.service import model,db
from .auth_utils import token_required

class EmployeeController(http.Controller):
    @http.route('/api/employee', type='json', auth='user', methods=['POST'], csrf=False)
    @token_required
    def create_employee(self, **kwargs):
        try:
            # Extract the data from request
            data = kwargs or request.httprequest.get_json(force=True)

            # Check mandatory fields
            if not data.get('name') or not data.get('joining_date'):
                return {'status': 'error', 'message': 'Name and Joining Date are mandatory'}

            # Create employee
            employee = request.env['hr.employee'].sudo().create({
                'name': data.get('name'),
                'job_title': data.get('job_title'),
                'department_id': data.get('department_id'),
                'joining_date': data.get('joining_date'),
            })

            return {
                'status': 'success',
                'message': f'Employee {employee.name} created successfully',
                'employee_id': employee.id
            }

        except Exception as e:
            return {
                'status': 'error',
                'message': str(e)
            }


load_dotenv()
JWT_SECRET = os.getenv("JWT_SECRET_KEY", "default_secret")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
REFRESH_EXP = int(os.getenv("REFRESH_EXP", "1440"))  # Default 24 hours 

class AuthController(http.Controller):

    @http.route('/api/login', type='json', auth='none', methods=['POST'], csrf=False)
    def api_login(self, **kwargs):
        try:
            # Parse data from JSON body or kwargs
            data = kwargs or request.httprequest.get_json(force=True)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return {'status': 'error', 'message': 'username and password are required'}

            # Get database name from current session
            dbname = request.session.db

            uid = request.session.authenticate(dbname, {
                "login": username,
                "password": password,
                "type": "password"
            })


            if not uid:
                return {'status': 'error', 'message': 'Invalid credentials'}

            # Generate JWT token
            access_payload = {
                'user_id': uid,
                'login': username,
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=JWT_EXPIRATION_MINUTES)
            }
            
            refresh_payload = {
                'uid': uid,
                'type': 'refresh',
                'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=REFRESH_EXP)
            }

            access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
            refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

            # request.env['res.users'].sudo().browse(uid).write({'refresh_token': refresh_token})

            return {
                'status': 'success',
                'access_token': access_token,
                'refresh_token': refresh_token,
                'user_id': uid,
                'expires_in': f"{JWT_EXPIRATION_MINUTES} minutes"
            }

        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        
        
    @http.route('/api/token/refresh', type='json', auth='none', methods=['POST'], csrf=False)
    def refresh_token(self, **kwargs):
        data = kwargs or request.httprequest.get_json(force=True)
        refresh_token = data.get('refresh_token')
        if not refresh_token:
            return {"status": "error", "message": "Refresh token missing"}

        try:
            payload = jwt.decode(refresh_token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
            user_id = payload.get('uid')  
            if not user_id:
                return {"status": "error", "message": "Invalid token payload: uid missing"}

            # Generate new tokens
            new_access, new_refresh = generate_tokens(user_id)

            return {
                "status": "success",
                "access_token": new_access,
                "refresh_token": new_refresh
            }

        except jwt.ExpiredSignatureError:
            return {"status": "error", "message": "Refresh token has expired"}
        except jwt.InvalidTokenError:
            return {"status": "error", "message": "Invalid refresh token"}


def generate_tokens(user_id, login=None):
    
    access_payload = {
        'user_id': user_id,
        'login': login,
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=JWT_EXPIRATION_MINUTES)
    }

    refresh_payload = {
        'uid': user_id,
        'type': 'refresh',
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=REFRESH_EXP)
    }

    access_token = jwt.encode(access_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    refresh_token = jwt.encode(refresh_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return access_token, refresh_token

# load_dotenv()
# JWT_SECRET = os.getenv("JWT_SECRET_KEY")
# JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
# JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))


# class AuthController(http.Controller):

#     @http.route('/api/login', type='json', auth='none', methods=['POST'], csrf=False)
#     def api_login(self, **kwargs):

#         try:
#             # Extract credentials
#             # data = request.get_json_data() if hasattr(request, 'get_json_data') else request.httprequest.get_json(force=True)

#             # username = data.get('username')
#             # password = data.get('password')

#             # Handle both normal JSON and JSON-RPC body
#             data = {}
#             # First priority: JSON body sent via kwargs
#             if kwargs:
#                 data = kwargs
#             else:
#                 # If kwargs empty, read directly from HTTP body
#                 try:
#                     data = request.httprequest.get_json(force=True)
#                 except Exception:
#                     data = {}

#             username = data.get('username')
#             password = data.get('password')


#             if not username or not password:
#                 return {'status': 'error', 'message': 'username and password are required'}

#             # Authenticate using Odoo's internal method
#             dbname = request.session.db
#             userid = model.dispatch_rpc('res.users', 'authenticate', [dbname, username, password, {}])


#             if not userid:
#                 return {'status': 'error', 'message': 'Invalid credentials'}

#             # Generate JWT token
#             payload = {
#                 'userid': userid,
#                 'login': username,
#                 'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=JWT_EXPIRATION_MINUTES)
#             }
#             access_token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

#             return {
#                 'status': 'success',
#                 'access_token': access_token,
#                 'user_id': userid,
#                 'expires_in': f"{JWT_EXPIRATION_MINUTES} minutes"
#             }

#         except Exception as e:
#             return {'status': 'error', 'message': str(e)}
