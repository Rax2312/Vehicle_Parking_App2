from flask import Blueprint, request, jsonify, current_app, make_response
from ..models import db, User
from flask_jwt_extended import create_access_token


auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/<path:path>', methods=['OPTIONS'])
def options_auth(path, **kwargs):
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,POST,PUT,DELETE,OPTIONS")
    return response, 200

# User registration
@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        phone_number = data.get('phone_number')
        age = data.get('age')
        address = data.get('address', '')

        # Validating fields
        required_fields = ['username', 'email', 'password', 'first_name', 'last_name', 'phone_number']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400

        # Check if username already exists
        if User.query.filter_by(username=username).first():
            return jsonify({
                'success': False,
                'message': 'Username already exists'
            }), 409

        # Check if email already exists
        if User.query.filter_by(email=email).first():
            return jsonify({
                'success': False,
                'message': 'Email already exists'
            }), 409

        # Create new user with all required fields
        new_user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone_number=phone_number,
            age=age,
            address=address,
            role='user'  # Default role for new registrations
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'User registered successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        }), 500

# User/Admin login
@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username_or_email = data.get('username')  
        password = data.get('password')

        if not username_or_email or not password:
            return jsonify({
                'success': False,
                'message': 'Missing username/email or password'
            }), 400

        user = User.query.filter(
            (User.username == username_or_email) | (User.email == username_or_email)
        ).first()

        if user and user.check_password(password):
            identity_str = f"{user.id}:{user.role}"
            
            access_token = create_access_token(identity=identity_str)
            return jsonify({
                'success': True,
                'access_token': access_token,
                'role': user.role,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'phone_number': user.phone_number,
                    'address': user.address,
                    'age': user.age
                }
            })

        return jsonify({
            'success': False,
            'message': 'Invalid credentials'
        }), 401
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Login failed: {str(e)}'
        }), 500

# Check username availability
@auth_bp.route('/check-username', methods=['POST'])
def check_username():
    try:
        data = request.get_json()
        username = data.get('username')
        
        if not username:
            return jsonify({
                'success': False,
                'message': 'Username is required'
            }), 400
        
        # Check if username exists
        existing_user = User.query.filter_by(username=username).first()
        
        return jsonify({
            'success': True,
            'available': existing_user is None
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Check failed: {str(e)}'
        }), 500 