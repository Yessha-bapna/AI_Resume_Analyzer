from flask import Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, set_access_cookies
from __init__ import db
from models import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Username, email, and password are required'}), 400
        
        # Check if user already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            is_admin=data.get('is_admin', False)
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        # Create response with user data
        response = make_response(jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201)
        
        # Set secure HTTP-only cookie
        response.set_cookie(
            'access_token_cookie',
            access_token,
            max_age=86400,  # 24 hours
            httponly=True,  # HTTP-only for security
            secure=False,   # Set to True in production with HTTPS
            samesite='Lax'  # CSRF protection
        )
        
        return response
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == data['username']) | (User.email == data['username'])
        ).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Create access token
        access_token = create_access_token(identity=str(user.id))
        
        # Create response with user data
        response = make_response(jsonify({
            'message': 'Login successful',
            'user': user.to_dict()
        }), 200)
        
        # Set secure HTTP-only cookie
        response.set_cookie(
            'access_token_cookie',
            access_token,
            max_age=86400,  # 24 hours
            httponly=True,  # HTTP-only for security
            secure=False,   # Set to True in production with HTTPS
            samesite='Lax'  # CSRF protection
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id))
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'email' in data:
            # Check if email is already taken by another user
            existing_user = User.query.filter(
                User.email == data['email'],
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({'error': 'Email already exists'}), 400
            user.email = data['email']
        
        if 'username' in data:
            # Check if username is already taken by another user
            existing_user = User.query.filter(
                User.username == data['username'],
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({'error': 'Username already exists'}), 400
            user.username = data['username']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        # Create response
        response = make_response(jsonify({'message': 'Logout successful'}), 200)
        
        # Clear the access token cookie
        response.set_cookie(
            'access_token_cookie',
            '',
            max_age=0,  # Expire immediately
            httponly=True,
            secure=False,
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
